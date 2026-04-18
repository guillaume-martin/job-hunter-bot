locals {
  # Define the source location so different versions of the module can be
  # deployed in different environments.
  repo       = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudwatch.git"
  module_loc = "modules/log-group"
  source_loc = "${local.repo}//${local.module_loc}"
}

inputs = {

}
