import sqlite3
import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
from sklearn.decomposition import PCA

def main():
    # Connect to the database
    print("Connecting to the database...")
    conn = sqlite3.connect('steam_games.db')
    cursor = conn.cursor()
    
    # List all tables in the database
    print("Listing all tables in the database...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables found: {tables}")
    
    # Close the initial connection
    conn.close()
    
    # Correct table names based on your database structure
    game_table = 'game_details'
    review_table = 'game_reviews'
    
    # Reconnect to the database
    print("Reconnecting to the database...")
    conn = sqlite3.connect('steam_games.db')
    
    # Load the data into pandas DataFrames
    print(f"Loading data from table: {game_table}")
    games_df = pd.read_sql_query(f"SELECT * FROM {game_table}", conn)
    print(f"Loading data from table: {review_table}")
    reviews_df = pd.read_sql_query(f"SELECT * FROM {review_table}", conn)
    
    # Close the connection
    conn.close()
    print("Database connection closed.")
    
    # Remove DLCs, Playtests, and Demos from games_df
    print("Filtering out soundtracks, OSTs, demos, DLCs, and playtests from games_df...")
    filtered_games_df = games_df[~games_df['name'].str.contains('soundtrack|OST|demo|DLC|playtest', case=False, na=False)]
    filtered_games_df.to_csv('filtered_games_df.csv', index=False)
    print(f"Filtered games saved to 'filtered_games_df.csv'. Number of filtered games: {filtered_games_df.shape[0]}")
    
    # Filter reviews based on the filtered games_df appid
    print("Filtering reviews based on the filtered games_df appid...")
    filtered_reviews_df = reviews_df[reviews_df['appid'].isin(filtered_games_df['appid'])]
    
    # Load pre-trained BERT model and tokenizer
    print("Loading pre-trained BERT model and tokenizer...")
    bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert_model = BertModel.from_pretrained('bert-base-uncased')
    
    # Function to get text embedding
    def get_embedding(text):
        inputs = bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).cpu().detach().numpy()
    
    # Generate embeddings for all game descriptions
    print("Generating embeddings for all game descriptions...")
    embeddings = []
    for idx, description in enumerate(filtered_games_df['description']):
        embeddings.append(get_embedding(description).flatten())
        if idx % 100 == 0:
            print(f"Processed {idx} descriptions...")
    
    # Convert to numpy array and save
    bert_item_feature_matrix = np.array(embeddings)
    np.save('bert_item_feature_matrix.npy', bert_item_feature_matrix)
    print("BERT item feature matrix saved to 'bert_item_feature_matrix.npy'.")
    
    # Perform PCA on the embeddings
    print("Performing PCA on the embeddings...")
    pca = PCA(n_components=768)
    reduced_item_feature_matrix = pca.fit_transform(bert_item_feature_matrix)
    np.save('reduced_item_feature_matrix.npy', reduced_item_feature_matrix)
    print("Reduced item feature matrix saved to 'reduced_item_feature_matrix.npy'.")

if __name__ == "__main__":
    main()
