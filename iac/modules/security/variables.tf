variable "ecr_repository_name" {
  description = "Name of the ECR repository the CI/CD role is allowed to push to"
  type        = string
}

variable "cicd_trusted_arns" {
  description = "IAM ARNs allowed to assume the CI/CD role (e.g. GitHub Actions OIDC role)."
  type        = list(string)
}

variable "jobs_table_name" {
  description = "Name of the DynamoDB table the task role is allowed to read/write"
  type        = string
}

variable "task_assume_role_name" {
  description = "Name of the IAM role the task is allowed to assume via STS (e.g. for cross-account access)"
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
