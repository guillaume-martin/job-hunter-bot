# This file defines the AWS Scheduler schedule resource for the compute module.
# It creates a schedule that triggers an ECS task based on a cron expression and
# flexible time window settings.

resource "aws_scheduler_schedule_group" "this" {
  name = "${local.name_hyphen}-scheduler-group"
}

resource "aws_scheduler_schedule" "this" {
  name       = "${local.name_hyphen}-scheduler"
  group_name = aws_scheduler_schedule_group.this.name

  flexible_time_window {
    mode                      = var.scheduler_flexible_time_window_mode
    maximum_window_in_minutes = var.scheduler_flexible_time_window_mode == "OFF" ? null : var.scheduler_maximum_window_in_minutes
  }

  schedule_expression          = "cron(${var.scheduler_cron_expression})"
  schedule_expression_timezone = var.scheduler_timezone

  target {
    arn      = aws_ecs_cluster.this.arn
    role_arn = var.scheduler_role_arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.this.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets          = var.network_configuration.subnets
        security_groups  = var.network_configuration.security_groups
        assign_public_ip = var.network_configuration.assign_public_ip
      }
    }
  }
}
