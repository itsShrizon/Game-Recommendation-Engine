import streamlit as st
import numpy as np
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Custom CSS for styling
def local_css():
    css = """
    <style>
        /* General Page Styles */
        .stApp {
            background-color: #f0f2f6; /* Light gray background */
        }
        h1.title {
            color: #2c3e50; /* Dark blue-gray */
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 0.5rem;
        }
        h2.header {
            color: #3498db; /* Bright blue */
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 2rem;
        }
        h3.subheader {
            color: #1abc9c; /* Turquoise */
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 1rem;
        }
        .stTextInput > div > div > input {
            border-radius: 5px;
            border: 1px solid #bdc3c7; /* Light silver border */
            padding: 10px;
        }
        .stButton > button {
            background-color: #3498db; /* Bright blue */
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #2980b9; /* Darker blue on hover */
        }
        /* Game Card Styles */
        .game-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 20px;
            margin: 15px auto; /* Centered cards */
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            text-align: center;
            max-width: 500px; /* Max width for cards */
        }
        .game-card:hover {
            transform: translateY(-5px);
        }
        .game-card img {
            border-radius: 4px;
            margin-bottom: 15px;
            max-width: 100%;
            height: auto;
        }
        .game-card .game-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50; /* Dark blue-gray */
            margin-bottom: 10px;
        }
        .game-card .game-description, .game-card .game-price, .game-card .game-release {
            font-size: 0.95em;
            color: #555;
            margin-bottom: 8px;
            text-align: left; /* Align text details to the left for readability */
        }
        .game-card .game-description strong, .game-card .game-price strong, .game-card .game-release strong {
            color: #34495e; /* Slightly darker for labels */
        }
        .game-card hr {
            border-top: 1px solid #ecf0f1; /* Light gray separator */
            margin-top: 1rem;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply the custom CSS
local_css()

# Load pre-trained BERT model and tokenizer
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

@st.cache_data
def load_data():
    games_df = pd.read_csv('filtered_games_df.csv')
    reduced_item_feature_matrix = np.load('reduced_item_feature_matrix.npy')
    return games_df, reduced_item_feature_matrix

# Function to get text embedding
def get_embedding(text):
    inputs = bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).cpu().detach().numpy()

# Recommendation function
def recommend_games(user_input, item_feature_matrix, games_df):
    user_embedding = get_embedding(user_input)
    similarities = cosine_similarity(user_embedding, reduced_item_feature_matrix)
    top_n = 5
    recommendations = similarities[0].argsort()[-top_n:][::-1]
    return recommendations

# Load data
games_df, reduced_item_feature_matrix = load_data()

# Streamlit app
st.markdown("<h1 class='title'>Steam Game Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='header'>Find Your Next Favorite Game!</h2>", unsafe_allow_html=True)

# User input
st.markdown("<h3 class='subheader'>Describe your ideal game:</h3>", unsafe_allow_html=True)
user_input = st.text_input("Enter a description (e.g., 'I want a History focussed RPG.')", key="user_input", placeholder="e.g., 'fast-paced multiplayer shooter'")

# Add a button to trigger recommendations
col1, col2, col3 = st.columns([2,1,2]) # Centering the button
with col2:
    recommend_button = st.button("Get Recommendations", key="recommend_button")

if recommend_button and user_input:
    with st.spinner('Finding the best games for you...'):
        st.markdown("<h3 class='subheader' style='margin-top: 2rem;'>Top 5 Recommended Games</h3>", unsafe_allow_html=True)
        recommendations = recommend_games(user_input, reduced_item_feature_matrix, games_df)
        
        if not recommendations.size:
            st.warning("Could not find any recommendations based on your description. Try being more specific or general!")
        else:
            for idx in recommendations:
                game_info = games_df.iloc[idx]
                
                # Using st.container to create a card-like structure with custom HTML/CSS
                st.markdown(f"""
                <div class='game-card'>
                    <img src="https://steamcdn-a.akamaihd.net/steam/apps/{game_info['appid']}/header.jpg" alt="{game_info['name']} Image">
                    <div class='game-name'>{game_info['name']}</div>
                    <hr>
                    <div class='game-description'><strong>Description:</strong> {game_info['description'][:250] + '...' if len(game_info['description']) > 250 else game_info['description']}</div>
                    <div class='game-price'><strong>Price:</strong> {game_info['price']}</div>
                    <div class='game-release'><strong>Release Date:</strong> {game_info['release_date']}</div>
                </div>
                """, unsafe_allow_html=True)
elif recommend_button and not user_input:
    st.warning("Please enter a description of the game you want to play.")

st.markdown("<hr style='margin-top: 3rem; border-top: 1px solid #bdc3c7;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: #7f8c8d; font-size: 0.9em;'>Powered by Trae AI & Streamlit</p>", unsafe_allow_html=True)
