from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np

df = pd.read_csv("../data/assessments.csv")
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['name'].tolist())

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

faiss.write_index(index, "shl_index.faiss")
df.to_pickle("shl_data.pkl")

print("✅ FAISS index and catalog saved.")
