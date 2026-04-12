data "aws_caller_identity" "this" {}
data "aws_default_tags" "this" {}
data "aws_region" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.this.account_id
  name           = data.aws_default_tags.this.tags.Name
  name_hyphen    = replace(local.name, "/", "-")
}
