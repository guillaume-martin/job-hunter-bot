output "cicd_role_arn" {
  description = "ARN of the CI/CD role"
  value       = aws_iam_role.cicd_role.arn
}
