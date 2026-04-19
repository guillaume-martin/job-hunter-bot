# This module defines the SSM parameters for the compute resources.

resource "aws_ssm_parameter" "ai_api_key" {
  name  = "/${local.name}/ai-api-key"
  type  = "SecureString"
  value = "PLACEHOLDER"
  lifecycle {
    ignore_changes = [value]
  }
}
