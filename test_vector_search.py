import json
import os
import sys
import urllib.request

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

QUERY = sys.argv[1] if len(sys.argv) > 1 else "Brazil"


def embed(text):
    req = urllib.request.Request(
        "https://api.voyageai.com/v1/embeddings",
        data=json.dumps({"input": [text], "model": "voyage-3-lite"}).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['VOYAGE_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["data"][0]["embedding"]


query_vector = embed(QUERY)

client = MongoClient(os.environ["MONGODB_URI"])
try:
    pipeline = [
        {
            "$vectorSearch": {
                "index": "facts_nested_vector_index",
                "path": "facts.embedding",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": 5,
                "nestedOptions": {"scoreMode": "max"},
                "parentFilter": { "wonder_status.is_current": { "$eq": True } },

            }
        },
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "category": 1,
                "facts.text": 1,
                "wonder_status.is_current": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
        {"$match": {"score": {"$gte": 0.6}}},
    ]
    results = list(client["wonders_db"]["wonders"].aggregate(pipeline))
    print(f"Query: {QUERY!r}")
    print("Showing results that are current wonders with a relevance score of 0.6 or above:\n")
    for r in results:
        is_current = int(r["wonder_status"]["is_current"])
        print(f"{r['score']:.4f}  {r['name']} ({r['category']}) - Current({is_current})")
        for fact in r["facts"]:
            print(f"    - {fact['text']}")
finally:
    client.close()
