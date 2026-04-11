output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.execution_role.arn
}

output "cicd_role_arn" {
  description = "ARN of the CI/CD role"
  value       = aws_iam_role.cicd_role.arn
}
