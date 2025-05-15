import pandas as pd
import numpy as np
import ast
import os
from datetime import datetime
import re
import string
import nltk
from nltk.corpus import stopwords, opinion_lexicon
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import seaborn as sns
import csv

# Step 1: Identify the maximum number of columns
input_file = './data/raw/steam_games.csv'
max_columns = 0
with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if len(row) > max_columns:
            max_columns = len(row)

print(f"Maximum number of columns found: {max_columns}")

# Step 2: Read the file with padding
output_file = './data/raw/steam_games_cleaned.csv'
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        while len(row) < max_columns:
            row.append('')  # Pad with empty values
        writer.writerow(row)

print("Preprocessing completed. Cleaned file saved as steam_games_cleaned.csv")

# Load the cleaned data
df = pd.read_csv('./data/raw/steam_games_cleaned.csv')

# Now you can proceed with the rest of your code
