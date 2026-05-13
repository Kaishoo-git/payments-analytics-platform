                ┌────────────────────┐
                │ Transaction Client │
                └─────────┬──────────┘
                          │ REST
                    ┌─────▼─────┐
                    │ FastAPI   │
                    │ API Layer │
                    └─────┬─────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   PostgreSQL       Kafka Producer    Fraud Engine
   OLTP Storage      (planned)         Rules/Scoring

                          │
                          ▼
                    Kafka Topics
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
      Stream Consumers            Airflow Jobs
            │                           │
            ▼                           ▼
      Snowflake Warehouse  <──── dbt Transformations
            │
            ▼
     Superset / Metabase
            │
            ▼
      Fraud Analytics Dashboard