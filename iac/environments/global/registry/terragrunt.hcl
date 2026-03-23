include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

include "component_vars" {
  path = "${dirname(find_in_parent_folders("root.hcl"))}/component_vars/registry.hcl"
  # Expose component vars so inputs are included in the module inputs below
  expose = true
}

locals {
  # Version of the terraform module to use
  ref = "2.3.0"

  component    = basename(get_terragrunt_dir())
}

terraform {
  source = "${include.component_vars.locals.source_loc}?ref=v${local.ref}"
}

dependency "security" {
  config_path = "${dirname(get_terragrunt_dir())}/security"
  mock_outputs_allowed_terraform_commands = ["validate", "init", "plan"]
  mock_outputs = {
    task_execution_role_arn = "arn:aws:iam::123456789012:role/EcsTaskExecutionRole"
    terraform_role_arn      = "arn:aws:iam::123456789012:role/TerraformRole"
  }
}

inputs = {
  region          = include.root.locals.aws_region
  repository_name = include.root.locals.project
  repository_type = "private"

  # Image mutability (prevent tag overwriting)
  repository_image_tag_mutability = "IMMUTABLE"

  # Scan images on push
  repository_image_scan_on_push = true

  # Encryption
  repository_encryption_type = "AES256"

  # Access control (ARNs of roles that can push/pull images)
  repository_read_write_access_arns = [
    dependency.security.outputs.task_execution_role_arn,
    dependency.security.outputs.terraform_role_arn,
  ]

  # Lifecycle policy (cleanup old images)
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
