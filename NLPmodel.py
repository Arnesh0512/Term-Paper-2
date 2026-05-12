from sentence_transformers import SentenceTransformer
import numpy as np



print("Loading BERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded")

def get_embedding(text):
    return model.encode(text)

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
