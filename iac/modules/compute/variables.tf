#------------------------------------------------------------------------------
# Task Definition Settings
#------------------------------------------------------------------------------
variable "ecr_name" {
  description = "Name of the ECR repository where the container image is stored."
  type        = string
}

variable "ecr_tag" {
  description = "Tag of the image used to deploy the application container"
  type        = string
}

variable "execution_role_arn" {
  description = "ARN of the execution role used by the task."
  type        = string
}

variable "scheduler_role_arn" {
  description = "ARN of the role used by the scheduler."
  type        = string
}

variable "project_name" {
  description = "Name of the project, used as prefix for log stream names."
  type        = string
}

variable "task_definition_environment" {
  description = "Environment variables to pass to the container."
  type        = list(object({ name = string, value = string }))
  default     = []
}

variable "task_definition_secrets" {
  description = "Secrets to pass to the container."
  type        = list(object({ name = string, valueFrom = string }))
  default     = []
}

variable "task_cpu" {
  description = "Amount of CPU used by the task (in CPU units)"
  type        = number
}

variable "task_memory" {
  description = "Amount of memory used by the task (in MiB)"
  type        = number
}

variable "task_role_arn" {
  description = "ARN of the task role used by the task."
  type        = string
}


#------------------------------------------------------------------------------
# Scheduler Settings
#------------------------------------------------------------------------------

variable "network_configuration" {
  description = "Network configuration for the scheduler target."
  type = object({
    security_groups  = list(string)
    subnets          = list(string)
    assign_public_ip = bool
  })
  default = {
    security_groups  = []
    subnets          = []
    assign_public_ip = false
  }
}

variable "scheduler_cron_expression" {
  description = "Cron expression for the scheduler."
  type        = string
  default     = "5 0 * * *"
}

variable "scheduler_flexible_time_window_mode" {
  description = "Flexible time window mode for the scheduler. Valid values are OFF, FLEXIBLE, and UNRESTRICTED."
  type        = string
  default     = "OFF"
}

variable "scheduler_maximum_window_in_minutes" {
  description = "Maximum window in minutes for the scheduler when flexible time window mode is enabled."
  type        = number
  default     = 60
}

variable "scheduler_timezone" {
  description = "Timezone for the scheduler cron expression."
  type        = string
  default     = "UTC"
}
