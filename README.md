

# Steam-lit: Word Embeddings and LDA-Based NLP Recommendation System

This project demonstrates the creation of a Steam game recommendation system using a combination of BERT word embeddings and Latent Dirichlet Allocation (LDA) for topic modeling. The system recommends games based on user input descriptions.

## Table of Contents
- [Overview](#overview)
- [Technologies Used](#technologies-used)
- [Data Extraction](#data-extraction)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Latent Dirichlet Allocation (LDA)](#latent-dirichlet-allocation-lda)
- [BERT Embeddings](#bert-embeddings)
- [Cosine Similarity](#cosine-similarity)
- [Implementation](#implementation)
- [Conclusion](#conclusion)

## Overview

The Steam-lit project involves building a recommendation system that combines the power of topic modeling through LDA and contextual word embeddings via BERT to provide game recommendations based on user-provided text descriptions.

## Technologies Used

- **Python**
- **Streamlit** - For the web interface
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical operations
- **scikit-learn** - Machine learning algorithms and utilities
- **Hugging Face Transformers** - For BERT embeddings
- **Latent Dirichlet Allocation (LDA)** - For topic modeling
- **SQLite** - For data storage

## Data Extraction

The data for this project was extracted using the Steam Web API, allowing us to retrieve details about various games, including descriptions, reviews, and metadata.

## Exploratory Data Analysis (EDA)

Before building the recommendation system, the data was thoroughly cleaned and analyzed. This involved:
- Filtering out non-game items like soundtracks, DLCs, and demos.
- Analyzing the distribution of game tags, genres, and user reviews.
- Visualizing the relationships between different features to understand the dataset better.

## Latent Dirichlet Allocation (LDA)

LDA is used in this project to identify topics within the user reviews.

**Mathematics**:

- LDA assumes that each document (in our case, a game review) is a mixture of topics and that each word in the document is attributable to one of the document's topics.
- The LDA model produces a matrix of topic distributions for each review, which is then aggregated to form a topic distribution for each game.

## BERT Embeddings

BERT (Bidirectional Encoder Representations from Transformers) is used to create embeddings for game descriptions.

**Process**:

- Each game description is tokenized using BERT's tokenizer, then passed through the BERT model to obtain a dense vector representation (embedding).
- These embeddings capture the semantic meaning of the game descriptions.

## Cosine Similarity

Cosine similarity is used to compare the user input with the game embeddings to find the most similar games.

**Mathematics**:

- The cosine similarity between two vectors `A` and `B` is calculated as:

  ```
  cosine_similarity(A, B) = (A · B) / (||A|| ||B||)
  ```

- In this project, cosine similarity is used to compute the similarity between the user's input embedding and the combined game description and topic embeddings.

## Implementation

The project was implemented in several key steps:

1. **Data Preparation**: Data was extracted from the Steam API, cleaned, and stored in an SQLite database.
2. **Topic Modeling with LDA**: LDA was applied to game reviews to extract topics, which were then associated with each game.
3. **Word Embeddings with BERT**: BERT was used to convert game descriptions into embeddings.
4. **Combining Features**: The LDA topic matrix and BERT embeddings were combined to form a comprehensive feature matrix for each game.
5. **Recommendation System**: The cosine similarity between user input and the game feature matrix was calculated to provide the top game recommendations.

## Conclusion

The Steam-lit project showcases the power of combining modern NLP techniques like BERT embeddings with classical topic modeling approaches such as LDA. The result is a recommendation system that can provide meaningful game suggestions based on textual input from users.
