# This file defines the ECS task definition for the service. It specifies the
# container image, resource requirements, environment variables, and logging
# configuration.

locals {
  image = "${local.aws_account_id}.dkr.ecr.${data.aws_region.current.region}.amazonaws.com/${var.ecr_name}"
}

resource "aws_ecs_task_definition" "this" {
  family                   = local.name_hyphen
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  container_definitions = jsonencode([
    {
      name      = local.name_hyphen
      image     = "${local.image}:${var.ecr_tag}"
      essential = true

      environment = var.task_definition_environment
      secrets = [
        { name = "AI_API_KEY", valueFrom = aws_ssm_parameter.ai_api_key.arn },
      ]

      logConfiguration = {
        "logDriver" = "awslogs"
        "options" = {
          "awslogs-group"         = var.cloudwatch_log_group_name
          "awslogs-region"        = data.aws_region.current.region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}
