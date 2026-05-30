resource "snowflake_warehouse" "fraud_wh" {
  name           = "FRAUD_WH"
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

resource "snowflake_account_role" "dbt_role" {
  name = "DBT_ROLE"
}

resource "snowflake_grant_privileges_to_account_role" "warehouse_usage" {
  privileges        = ["USAGE"]
  account_role_name = snowflake_account_role.dbt_role.name

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.fraud_wh.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "database_usage" {
  privileges        = ["USAGE", "CREATE SCHEMA"]
  account_role_name = snowflake_account_role.dbt_role.name

  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.fraud_analytics.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "raw_schema_grants" {
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]
  account_role_name = snowflake_account_role.dbt_role.name

  on_schema {
    schema_name = "\"FRAUD_ANALYTICS\".\"RAW\""
  }
}


resource "snowflake_grant_privileges_to_account_role" "analytics_schema_grants" {
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]
  account_role_name = snowflake_account_role.dbt_role.name

  on_schema {
    schema_name = "\"FRAUD_ANALYTICS\".\"ANALYTICS\""
  }
}