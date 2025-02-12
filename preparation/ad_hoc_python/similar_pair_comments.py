import numpy as np
from sentence_transformers import SentenceTransformer

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Read comments from file, one per line
with open(r'D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\comments.txt', 'r', encoding='utf-8') as f:
    comments = [line.strip() for line in f if line.strip()]

# Compute embeddings for all comments
embeddings = model.encode(comments)

# Function to compute cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Initialize variables to store the highest similarity and the corresponding pair of comments
max_sim = -1
most_similar_pair = (None, None)
n = len(embeddings)

# Compare each unique pair of comments
for i in range(n):
    for j in range(i + 1, n):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        if sim > max_sim:
            max_sim = sim
            most_similar_pair = (comments[i], comments[j])

# Write the most similar comments to the output file
with open(r'D:\work\gramener\anand_assignment\project1\tds_project1_automation_agent\data\comments-similar.txt', 'w', encoding='utf-8') as f:
    f.write(most_similar_pair[0] + '\n')
    f.write(most_similar_pair[1] + '\n')

print("Most similar comments have been written to /data/comments-similar.txt")