import argparse
import os
import math
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def load_environment() -> dict:
    load_dotenv()
    env = {
        "DB_USER": os.getenv("POSTGRES_USER"),
        "DB_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "DB_NAME": os.getenv("POSTGRES_DB"),
        "DB_HOST": "localhost", #os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "SNOWFLAKE_USER": os.getenv("SNOWFLAKE_USER"),
        "SNOWFLAKE_ACCOUNT": os.getenv("SNOWFLAKE_ACCOUNT"),
        "SNOWFLAKE_ROLE": os.getenv("SNOWFLAKE_ROLE"),
        "SNOWFLAKE_WAREHOUSE": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "SNOWFLAKE_DATABASE": os.getenv("SNOWFLAKE_DATABASE"),
        "SNOWFLAKE_SCHEMA": os.getenv("SNOWFLAKE_SCHEMA"),
        "SNOWFLAKE_PK_PATH": os.getenv("SNOWFLAKE_PK_PATH"),
        "SNOWFLAKE_PK_PASSPHRASE": os.getenv("SNOWFLAKE_PK_PASSPHRASE")
    }
    return env


def get_postgres_engine(env: dict):
    postgres_url = (
        f"postgresql://{env['DB_USER']}:"
        f"{env['DB_PASSWORD']}@"
        f"{env['DB_HOST']}:"
        f"{env['DB_PORT']}/"
        f"{env['DB_NAME']}"
    )
    return create_engine(postgres_url)


def get_snowflake_connection(env: dict):
    key_path = Path(env["SNOWFLAKE_PK_PATH"])
    if not key_path.exists():
        raise FileNotFoundError(f"Snowflake private key path not found: {key_path}")
    password = env.get("SNOWFLAKE_PK_PASSPHRASE")
    password_bytes = password.encode()
    with key_path.open("rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password_bytes,
            backend=default_backend(),
        )

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return snowflake.connector.connect(
        user=env["SNOWFLAKE_USER"],
        account=env["SNOWFLAKE_ACCOUNT"],
        private_key=private_key_bytes,
        role=env["SNOWFLAKE_ROLE"],
        autocommit=True,
    )


def fetch_postgres_table(engine, table_name):
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

def normalize_dataframe(dataframe: pd.DataFrame):
    dataframe = dataframe.copy()
    for column in dataframe.columns:
        if pd.api.types.is_datetime64_any_dtype(dataframe[column]):
            dataframe[column] = (
                dataframe[column]
                .astype(str)
                .replace("NaT", None)
            )
    dataframe = dataframe.where(pd.notnull(dataframe), None)
    return dataframe


def map_pandas_type(dtype):
    dtype = str(dtype)
    if "int" in dtype: return "INTEGER"
    if "float" in dtype: return "FLOAT"
    if "bool" in dtype: return "BOOLEAN"
    if "datetime" in dtype: return "TIMESTAMP"
    return "STRING"

def table_exists(cursor, table_name):
    query = f"SHOW TABLES LIKE '{table_name}'"
    cursor.execute(query)
    return cursor.fetchone() is not None

def create_table_if_not_exists(cursor,dataframe, table_name, primary_key="id"):
    if table_exists(cursor, table_name):
        print(f"Table already exists: {table_name}")
        return
    column_definitions = []
    for column in dataframe.columns:
        snowflake_type = map_pandas_type(dataframe[column].dtype)
        definition = f"{column} {snowflake_type}"
        if column == primary_key: definition += " PRIMARY KEY"
        column_definitions.append(definition)
    create_query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
    print(f"Creating table: {table_name}")
    cursor.execute(create_query)

def insert_rows_in_batches(cursor, query, rows, batch_size=1000):
    total_batches = math.ceil(len(rows) / batch_size)
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        cursor.executemany(query, batch)
        current_batch = (i // batch_size) + 1
        print(f"Inserted batch {current_batch}/{total_batches}")


def upsert_dataframe(cursor, dataframe, table_name, mode="incremental", primary_key="id",):
    if dataframe.empty:
        print(f"No rows found for {table_name}")
        return
    
    dataframe = normalize_dataframe(dataframe)
    create_table_if_not_exists(
        cursor,
        dataframe,
        table_name,
        primary_key
    )
    columns = list(dataframe.columns)
    column_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    rows = [
        tuple(row)
        for row in dataframe.itertuples(index=False)
    ]
    if mode == "full_refresh":
        print(f"Full refresh: Dropping table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        create_table_if_not_exists(cursor, dataframe, table_name, primary_key)
        insert_query = f"""
            INSERT INTO {table_name}
            ({column_names})
            VALUES ({placeholders})
        """
        insert_rows_in_batches(cursor, insert_query, rows)
        print(f"Inserted {len(rows)} rows into {table_name}")
        return

    temp_table = f"{table_name}_temp"
    print(f"Creating temp table: {temp_table}")
    cursor.execute(f"""
        CREATE OR REPLACE TEMP TABLE
        {temp_table}
        LIKE {table_name}
    """)
    insert_temp_query = f"""
        INSERT INTO {temp_table}
        ({column_names})
        VALUES ({placeholders})
    """
    insert_rows_in_batches(cursor, insert_temp_query, rows)
    update_clause = ", ".join([
        f"{column} = source.{column}"
        for column in columns
        if column != primary_key
    ])
    merge_query = f"""
        MERGE INTO {table_name} AS target
        USING {temp_table} AS source
        ON target.{primary_key}
            = source.{primary_key}
        WHEN MATCHED THEN
            UPDATE SET
                {update_clause}
        WHEN NOT MATCHED THEN
            INSERT ({column_names})
            VALUES (
                {", ".join([f"source.{column}" for column in columns])}
            )
    """
    print(f"Running MERGE for {table_name}")
    cursor.execute(merge_query)
    print(f"Upserted {len(rows)} rows into {table_name}")
    
def parse_args():
    parser = argparse.ArgumentParser(description="Postgres to Snowflake ETL")
    parser.add_argument(
        "--mode",
        choices=["full_refresh", "incremental"],
        default="incremental",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Running ETL mode: {args.mode}")
    env = load_environment()
    postgres_engine = get_postgres_engine(env)
    snowflake_conn = get_snowflake_connection(env)
    snowflake_cursor = snowflake_conn.cursor()
    snowflake_cursor.execute(f"USE WAREHOUSE {env['SNOWFLAKE_WAREHOUSE']}")
    snowflake_cursor.execute(f"USE DATABASE {env['SNOWFLAKE_DATABASE']}")
    snowflake_cursor.execute(f"USE SCHEMA {env['SNOWFLAKE_SCHEMA']}")
    try:
        for table_name in [
            "merchants",
            "transactions",
            "payments",
            "users",
        ]:
            dataframe = fetch_postgres_table(postgres_engine, table_name)
            upsert_dataframe(
                snowflake_cursor,
                dataframe,
                table_name,
                mode=args.mode,
            )
        print("Postgres → Snowflake ETL complete")

    except Exception as exc:
        print(f"ETL failed: {exc}")
        snowflake_conn.rollback()
        raise

    finally:
        snowflake_cursor.close()
        snowflake_conn.close()


if __name__ == "__main__":
    main()
