terraform {
  required_providers {
    snowflake = {
      source = "snowflakedb/snowflake"
    }
  }
}

provider "snowflake" {
    organization_name      = var.organization_name
    account_name           = var.snowflake_account_name
    user                   = var.snowflake_user
    role                   = "ACCOUNTADMIN"
    authenticator          = "SNOWFLAKE_JWT"
    private_key            = file(var.private_key_path)
    private_key_passphrase = var.private_key_passphrase
}