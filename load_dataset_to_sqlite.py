import sqlite3

from datasets import load_dataset

repo = "LeandroRibeiro/JurisTCU"

# Load each CSV file separately since they have different schemas
print("Loading datasets...")
docs    = load_dataset(repo, data_files="doc.csv",   split="train")
qrels   = load_dataset(repo, data_files="qrel.csv",  split="train")
queries = load_dataset(repo, data_files="query.csv", split="train")

# Convert to pandas DataFrames
df_docs    = docs.to_pandas()
df_qrels   = qrels.to_pandas()
df_queries = queries.to_pandas()

# Write to SQLite
db_path = "juristcu.db"
con = sqlite3.connect(db_path)

df_docs.to_sql("docs",    con, if_exists="replace", index=False)
df_qrels.to_sql("qrels",  con, if_exists="replace", index=False)
df_queries.to_sql("queries", con, if_exists="replace", index=False)

con.close()
print(f"Saved to {db_path}")
print(f"  docs:    {len(df_docs)} rows, columns: {list(df_docs.columns)}")
print(f"  qrels:   {len(df_qrels)} rows, columns: {list(df_qrels.columns)}")
print(f"  queries: {len(df_queries)} rows, columns: {list(df_queries.columns)}")
