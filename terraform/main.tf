resource "snowflake_warehouse" "etl_wh" {
  name           = "ETL_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60
}

resource "snowflake_database" "fraud_analytics" {
  name = "FRAUD_ANALYTICS"
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.fraud_analytics.name
  name     = "RAW"
}

resource "snowflake_schema" "analytics" {
  database = snowflake_database.fraud_analytics.name
  name     = "ANALYTICS"
}