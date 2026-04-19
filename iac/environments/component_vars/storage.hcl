locals {
  # Define the source location so different versions of the module can be
  # deployed in different environments.
  repo       = "git::https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table.git"
  source_loc = "${local.repo}"
}
