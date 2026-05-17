import os

import pandas as pd
import snowflake.connector

from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


# =========================================================
# PostgreSQL Connection
# =========================================================

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")


postgres_url = (
    f"postgresql://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

postgres_engine = create_engine(postgres_url)


# =========================================================
# Snowflake Connection
# =========================================================

snowflake_conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),

    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
)

snowflake_cursor = snowflake_conn.cursor()


# =========================================================
# Extract PostgreSQL Data
# =========================================================

transactions_df = pd.read_sql(
    "SELECT * FROM transactions",
    postgres_engine
)

fraud_scores_df = pd.read_sql(
    "SELECT * FROM fraud_scores",
    postgres_engine
)

transaction_events_df = pd.read_sql(
    "SELECT * FROM transaction_events",
    postgres_engine
)


# =========================================================
# Helper Function
# =========================================================

def insert_dataframe(
    dataframe: pd.DataFrame,
    table_name: str
):

    if dataframe.empty:
        print(f"No rows found for {table_name}")
        return

    columns = list(dataframe.columns)

    column_names = ", ".join(columns)

    placeholders = ", ".join(["%s"] * len(columns))

    insert_query = f"""
    INSERT INTO {table_name}
    ({column_names})
    VALUES ({placeholders})
    """

    rows = [
        tuple(row)
        for row in dataframe.itertuples(index=False)
    ]

    snowflake_cursor.executemany(
        insert_query,
        rows
    )

    print(
        f"Inserted {len(rows)} rows "
        f"into Snowflake table {table_name}"
    )


# =========================================================
# Load Into Snowflake
# =========================================================

insert_dataframe(
    transactions_df,
    "transactions"
)

insert_dataframe(
    fraud_scores_df,
    "fraud_scores"
)

insert_dataframe(
    transaction_events_df,
    "transaction_events"
)


# =========================================================
# Cleanup
# =========================================================

snowflake_cursor.close()
snowflake_conn.close()

print("Postgres → Snowflake ETL complete")