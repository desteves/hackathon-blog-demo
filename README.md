# Wonders of the World

Dummy dataset of world wonders, loaded into MongoDB Atlas with per-fact vector search embeddings.

## Setup

```bash
cp .env.sample .env   # fill in your own values
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python3 test_connection.py
```

## Contents

- `data/wonders.csv` — one row per wonder (location, category, wonder status).
- `data/wonders_facts.csv` — one row per fact, joined to `wonders.csv` on `name`.
- `test_connection.py` — sanity-checks the `MONGODB_URI` connection.

## Data model

Both CSVs are merged into a single `wonders_db.wonders` collection, one document per wonder, with `facts` embedded as an array of `{ text, embedding }` subdocuments. A vector search index (`nestedRoot: "facts"`) enables semantic search over individual facts.

Data was loaded into the collection using the Claude Code MongoDB plugin (MCP server), which connects directly to the cluster to create the collection and insert documents.
