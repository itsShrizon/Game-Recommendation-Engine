import requests
import sqlite3
import time
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import random

API_KEY = os.getenv('STEAM_API_KEY')
BASE_URL = 'http://api.steampowered.com/ISteamApps/GetAppList/v2/'
DETAILS_URL = 'https://store.steampowered.com/api/appdetails'
MAX_RETRIES = 5
RATE_LIMIT = 1  # requests per second
MAX_WORKERS = 3  # Number of concurrent threads
BATCH_SIZE = 50  # Save progress in batches
PROCESSED_IDS_FILE = 'processed_ids.txt'

def setup_logging():
    logging.basicConfig(
        filename='fetch_data.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    return logging.getLogger()

logger = setup_logging()

def create_tables():
    conn = sqlite3.connect('steam_games.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS game_details (
            appid INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            price TEXT,
            release_date TEXT,
            developer TEXT,
            publisher TEXT,
            tags TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS game_reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid INTEGER,
            review_text TEXT,
            voted_up BOOLEAN,
            timestamp_created INTEGER,
            author_playtime_forever INTEGER,
            author_playtime_last_two_weeks INTEGER,
            author_num_reviews INTEGER,
            FOREIGN KEY(appid) REFERENCES game_details(appid)
        )
    ''')

    conn.commit()
    conn.close()

def fetch_app_list():
    logger.info("Fetching app list...")
    response = requests.get(BASE_URL)
    response.raise_for_status()
    app_list = response.json()['applist']['apps']
    logger.info(f"Fetched {len(app_list)} apps.")
    return app_list

def fetch_app_details(appid):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(DETAILS_URL, params={'appids': appid})
            if response.status_code == 429:  # Too Many Requests
                logger.warning(f"Rate limit exceeded for appid {appid}. Retrying after delay.")
                sleep_time = 30 * (2 ** attempt) + random.uniform(0.5, 1.5)  # Exponential backoff with jitter
                time.sleep(sleep_time)
                continue
            response.raise_for_status()
            data = response.json()
            if data and str(appid) in data and data[str(appid)]['success']:
                details = data[str(appid)]['data']
                game_data = (
                    appid,
                    details.get('name'),
                    details.get('short_description'),
                    details.get('price_overview', {}).get('final_formatted', 'N/A'),
                    details.get('release_date', {}).get('date', 'N/A'),
                    details.get('developers', ['N/A'])[0],
                    details.get('publishers', ['N/A'])[0],
                    ', '.join([genre['description'] for genre in details.get('genres', [])])
                )
                return game_data
            else:
                logger.warning(f"Failed to fetch game details for appid: {appid}")
                return None
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for appid {appid}: {str(e)}")
            sleep_time = 2 ** attempt + random.uniform(0.5, 1.5)  # Exponential backoff with jitter
            time.sleep(sleep_time)
    return None

def fetch_app_reviews(appid, num_reviews=100):
    try:
        url = f"https://store.steampowered.com/appreviews/{appid}?json=1&num_per_page={num_reviews}"
        response = requests.get(url)
        data = response.json()
        if 'reviews' in data:
            reviews = data['reviews']
            review_entries = []
            for review in reviews:
                review_data = (
                    appid,
                    review['review'],
                    review['voted_up'],
                    review['timestamp_created'],
                    review['author']['playtime_forever'],
                    review['author']['playtime_last_two_weeks'],
                    review['author']['num_reviews']
                )
                review_entries.append(review_data)
            return review_entries
        else:
            logger.warning(f"Failed to fetch reviews for appid: {appid}")
            return []
    except Exception as e:
        logger.error(f"Error fetching reviews for appid: {appid} - {e}")
        return []

def save_batch_to_db(game_details, game_reviews):
    conn = sqlite3.connect('steam_games.db')
    c = conn.cursor()
    try:
        # Insert game details
        c.executemany('''
            INSERT OR IGNORE INTO game_details (appid, name, description, price, release_date, developer, publisher, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', game_details)

        # Insert game reviews
        for review in game_reviews:
            c.executemany('''
                INSERT INTO game_reviews (appid, review_text, voted_up, timestamp_created, author_playtime_forever, author_playtime_last_two_weeks, author_num_reviews)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', review)
        conn.commit()
    except sqlite3.OperationalError as e:
        logger.error(f"Error inserting batch data: {e}")
    finally:
        conn.close()

def load_processed_ids():
    if os.path.exists(PROCESSED_IDS_FILE):
        with open(PROCESSED_IDS_FILE, 'r') as file:
            processed_ids = set(int(line.strip()) for line in file)
        return processed_ids
    return set()

def save_processed_id(appid):
    with open(PROCESSED_IDS_FILE, 'a') as file:
        file.write(f"{appid}\n")

def fetch_data(appid):
    game_data = fetch_app_details(appid)
    game_reviews = []
    if game_data:
        reviews = fetch_app_reviews(appid, num_reviews=100)
        if reviews:
            game_reviews = reviews
    return game_data, game_reviews

def main():
    setup_logging()
    create_tables()  # Ensure tables are created
    processed_ids = load_processed_ids()
    app_list = fetch_app_list()
    total_apps = len(app_list)

    game_details_batch = []
    game_reviews_batch = []
    batch_counter = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_data, app['appid']): app['appid'] for app in app_list if app['appid'] not in processed_ids}
        with tqdm(total=len(futures)) as pbar:
            for future in as_completed(futures):
                appid = futures[future]
                try:
                    game_data, game_reviews = future.result()
                    if game_data:
                        game_details_batch.append(game_data)
                        game_reviews_batch.append(game_reviews)
                        save_processed_id(appid)

                    if len(game_details_batch) >= BATCH_SIZE:
                        save_batch_to_db(game_details_batch, game_reviews_batch)
                        game_details_batch.clear()
                        game_reviews_batch.clear()
                        batch_counter += 1
                        logger.info(f"Saved batch {batch_counter}")

                    logger.info(f"Fetched details for appid: {appid}")
                except Exception as e:
                    logger.warning(f"Failed to fetch details for appid: {appid} - {e}")
                # Update progress bar
                pbar.update(1)
                # Rate limiting
                time.sleep(1 / RATE_LIMIT + random.uniform(0.5, 1.5))  # Randomized sleep to reduce contention

        # Save any remaining entries
        if game_details_batch:
            save_batch_to_db(game_details_batch, game_reviews_batch)
            logger.info(f"Saved final batch")

    logger.info(f"Data collection complete.")

if __name__ == '__main__':
    main()
