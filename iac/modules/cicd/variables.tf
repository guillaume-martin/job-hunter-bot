variable "ecr_repository_name" {
  description = "Name of the ECR repository the CI/CD role is allowed to push to"
  type        = string
}

variable "github_user" {
  description = "GitHub username for GitHub Actions OIDC trust relationship"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name (e.g. 'owner/repo') for GitHub Actions OIDC trust relationship"
  type        = string
}

variable "github_allowed_subs" {
  description = "OIDC sub-claim suffixes allowed (e.g., ref:refs/heads/main, environment:production)"
  type        = list(string)
  default     = ["ref:refs/heads/main"]
}
