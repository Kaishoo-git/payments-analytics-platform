terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.98"
    }
  }
}

provider "snowflake" {
  account                = var.snowflake_account
  user                   = var.snowflake_user
  private_key_path       = var.private_key_path
  private_key_passphrase = var.private_key_passphrase
  role                   = "TERRAFORM_ROLE"
}