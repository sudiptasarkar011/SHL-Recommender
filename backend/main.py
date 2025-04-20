from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import httpx
import os
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Load models/data
model = SentenceTransformer("all-MiniLM-L6-v2")
df = pd.read_pickle("shl_data.pkl")
index = faiss.read_index("shl_index.faiss")

# Optional: from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class QueryRequest(BaseModel):
    query: str

@app.get("/healthcheck")
def health():
    return {"status": "ok"}

@app.post("/recommend")
async def recommend(query_data: QueryRequest):
    query = query_data.query
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), 10)
    retrieved = df.iloc[I[0]].to_dict(orient="records")

    prompt = f"""You are an assessment advisor.
A recruiter gave the following hiring need:\n\n"{query}"

Here are 10 SHL assessments that could match:
{retrieved}

Based on the query, recommend 3–5 best fitting assessments and explain why they are suitable.
Respond in bullet points."""

    # Call Gemini API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            params={"key": GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )
        result = response.json()
        answer = result['candidates'][0]['content']['parts'][0]['text']

    return {
        "retrieved": retrieved,
        "generated_answer": answer
    }
