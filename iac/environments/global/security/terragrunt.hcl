include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

terraform {
    source = "${include.root.locals.modules_path}/security"
}

inputs = {
  ecr_repository_name = include.root.locals.project
  # cicd_trusted_arns = ["arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole"]
}
