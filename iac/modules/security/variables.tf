variable "ecr_repository_name" {
  description = "Name of the ECR repository the CI/CD role is allowed to push to"
  type        = string
}

variable "cicd_trusted_arns" {
  description = "IAM ARNs allowed to assume the CI/CD role (e.g. GitHub Actions OIDC role). Defaults to the account root if empty."
  type        = list(string)
  default     = []
}
