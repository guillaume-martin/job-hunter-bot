include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

terraform {
    source = "${include.root.locals.modules_path}/security"
}

inputs = {
  ecr_repository_name = include.root.locals.project
  github_user         = "guillaume-martin"
  github_repo         = "job-hunter-bot"
  # The default allowed subs are `refs/heads/main` to allow GitHub Actions
  # workflows running on the main branch to assume the role. You can add
  # additional subs (e.g., for other branches or environments) as needed.
  # github_allowed_subs = []
}
