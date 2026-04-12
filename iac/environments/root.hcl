locals {
  common_vars      = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
  environment_vars = read_terragrunt_config(find_in_parent_folders("environment.hcl"))

  # Extract variables to top level
  environment = local.environment_vars.locals.environment
  aws_region  = local.common_vars.locals.aws_region
  aws_profile = local.common_vars.locals.aws_profile
  project     = local.common_vars.locals.aws_project
  cost_center = local.common_vars.locals.cost_center

  # Define the path to the Terraform modules
  modules_path = "${get_repo_root()}/iac/modules"

  component = basename(get_terragrunt_dir())

  name = replace("${local.project}/${local.environment}/${local.component}", "_", "-")

  state_bucket = "iac-tfstate-files"
  statefile = "${local.name}/terraform.tfstate"

  default_tags = {
    "Name"        = local.name
    "project"     = local.project
    "env"         = local.environment
    "component"   = local.component
    "managed-by"  = "iac"
    "cost-center" = local.cost_center
    "owner"       = regex(".*/(.+)$", get_aws_caller_identity_arn())[0]
  }
}

remote_state {
  backend = "s3"

  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }

  config = {
    bucket       = local.state_bucket
    key          = local.statefile
    region       = "us-east-1"
    profile      = local.aws_profile
    encrypt      = true
    use_lockfile = true
    # false = Terragrunt actively enforces these controls on the state bucket
    skip_bucket_root_access  = false
    skip_bucket_enforced_tls = false
  }
}

generate "versions" {
  path      = "versions.tf"
  if_exists = "overwrite"
  contents  = <<EOF
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
EOF
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
