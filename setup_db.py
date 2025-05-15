import sqlite3

def create_tables():
    conn = sqlite3.connect('steam_games.db')
    c = conn.cursor()

    # Create table for game details
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

    # Create table for game reviews
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

if __name__ == '__main__':
    create_tables()
