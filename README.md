# Wonders of the World

Dummy dataset of world wonders, loaded into MongoDB Atlas with per-fact vector search embeddings.

> This repo was built while exploring the Atlas **Ephemeral Clusters** feature — an unauthenticated API that lets an agent deploy a real MongoDB cluster with zero registration or sign-up. Writeup: _[link coming soon]_.

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
- `test_vector_search.py` — runs a `$vectorSearch` query against `facts_nested_vector_index` and prints matches.
- `test_mongodump.sh` — dumps `wonders_db` to `./dump` using `mongodump`.
- `test_mongoexport.sh` — exports the `wonders` collection to `./export/wonders.json` using `mongoexport`.

## Data model

Both CSVs are merged into a single `wonders_db.wonders` collection, one document per wonder, with `facts` embedded as an array of `{ text, embedding }` subdocuments. A vector search index (`nestedRoot: "facts"`) enables semantic search over individual facts.

Data was loaded into the collection using the Claude Code MongoDB plugin (MCP server), which connects directly to the cluster to create the collection and insert documents.

### Sample document

Each `embedding` is a 512-dimensional vector (from `voyage-3-lite`); shown truncated below for readability.

```json
{
  "_id": { "$oid": "6a6253dc856ca032028e9ca2" },
  "name": "Taj Mahal",
  "location": {
    "country": "India",
    "geo": { "type": "Point", "coordinates": [78.0421, 27.1751] }
  },
  "category": "Medieval",
  "year_built": 1653,
  "height_m": 73,
  "wonder_status": {
    "designated_year": 2007,
    "wonder_list": "New7Wonders of the World",
    "is_current": true,
    "status_years": "2007-present"
  },
  "facts": [
    {
      "text": "Built by Emperor Shah Jahan as a mausoleum for his wife Mumtaz Mahal.",
      "embedding": [-0.027368912, 0.034467518, 0.03372249, 0.022610979, -0.035798829, "... 512 floats total"]
    },
    {
      "text": "Took approximately 22 years and over 20000 workers to complete.",
      "embedding": [-0.082305156, 0.035452142, 0.011168324, 0.023210831, 0.02782141, "... 512 floats total"]
    },
    {
      "text": "The main dome appears to change color depending on the time of day and light.",
      "embedding": [-0.119243629, 0.100950569, 0.057788756, -0.051553972, -0.010192438, "... 512 floats total"]
    },
    {
      "text": "Constructed primarily of white marble inlaid with semi-precious stones.",
      "embedding": [-0.047609512, 0.032451827, -0.00234966, 0.036333758, 0.008313105, "... 512 floats total"]
    }
  ]
}
```

## Testing

### Connection test

```bash
.venv/bin/python3 test_connection.py
```

On success, this prints:

```
Houston, we have liftoff!
```

### Vector search test

```bash
.venv/bin/python3 test_vector_search.py "Brazil"
```

This embeds the query with Voyage AI, runs a `$vectorSearch` against `facts_nested_vector_index`, and prints matches scoring 0.6+ that belong to currently recognized wonders:

```
Query: 'Brazil'
Showing results that are current wonders with a relevance score of 0.6 or above:

0.6356  Christ the Redeemer (Modern) - Current(1)
    - Struck by lightning multiple times due to its elevated hilltop position.
    - Stands atop Corcovado mountain overlooking Rio de Janeiro.
    - The statue's arms span roughly 28 meters wide.
    - Took around nine years to construct
```

(exact scores and matches depend on the query and current data)

### mongodump test

Requires the [MongoDB Database Tools](https://www.mongodb.com/docs/database-tools/) (`mongodump`) installed locally.

```bash
./test_mongodump.sh
```

Dumps `wonders_db` (BSON + metadata) to `./dump/wonders_db`. The output is committed to this repo as a sample snapshot.

### mongoexport test

Requires the [MongoDB Database Tools](https://www.mongodb.com/docs/database-tools/) (`mongoexport`) installed locally.

```bash
./test_mongoexport.sh
```

Exports the `wonders` collection as a JSON array to `./export/wonders.json` (human-readable, unlike `mongodump`'s BSON) — handy for eyeballing content or diffing against `data/wonders.csv` / `data/wonders_facts.csv`. The output is committed to this repo as a sample snapshot.

## Notes

- **Never commit `.env`** — it holds the real connection string, Voyage API key, and claim link. Use `.env.sample` as the template; `.env` is already gitignored.
- **The Atlas cluster is ephemeral** — it expires ~48h after creation (see `ATLAS_CLUSTER_EXPIRES_AT` in `.env`). Visit `ATLAS_CLAIM_URL` before then if you want to keep it.
- **Use a virtualenv, not a global `pip install`** — Homebrew's Python is externally managed (PEP 668) and will refuse global installs.
- **`nestedRoot` on vector search indexes may or may not work via the MongoDB Atlas MCP server's `create-index` tool** — in my testing, it was silently dropped from the stored index definition; I'm checking internally if this is a bug. Workaround: create/edit indexes needing `nestedRoot` through MongoDB Compass.
- **Embedding dimensions must match the index** — `numDimensions` in the vector index has to equal whatever your embedding model actually outputs (512 for `voyage-3-lite` here); mismatches fail silently at query time rather than erroring clearly.
