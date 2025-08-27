locals {
  common_vars      = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
  environment_vars = read_terragrunt_config(find_in_parent_folders("environment.hcl"))

  # Extract variables to top level
  environment = local.environment_vars.locals.environment
  aws_region  = local.environment_vars.locals.aws_region
  aws_profile = local.common_vars.locals.aws_profile
  project     = local.common_vars.locals.aws_project

  name = replace("${local.project}/${local.environment}/${local.component}", "_", "-")

  component = replace(regex("^.*${local.environment}/(.*)$", path_relative_to_include())[0], "/[^a-zA-Z0-9]/", "-")

  statefile = "${local.name}/terraform.tfstate"

  default_tags = {
    "Name"      = local.name
    "project"   = local.project
    "component" = local.component
    "statefile" = local.statefile
  }
}

remote_state {
 backend = "local"

 generate = {
    path = "backend.tf"
    if_exists = "overwrite_terragrunt"
 }

  config = {
    path = "${get_parent_terragrunt_dir()}/${path_relative_to_include()}/terraform.tfstate"
  }
}

generate "aws_provider" {
  path = "aws_provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region  = "${local.aws_region}"
  profile = "${local.aws_profile}"

  default_tags {
    tags = ${jsonencode(local.default_tags)}
  }
}
EOF
}

inputs = merge(
  local.common_vars.locals,
  local.environment_vars.locals,
)
