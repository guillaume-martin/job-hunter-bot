include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

locals {
  # Set the environment variables end secrets to insert in task definition
  td_env = {
    aws_region = include.root.locals.aws_region
    jobs_table = "${include.root.locals.project}-${include.root.locals.environment}-jobs-cache"
    retention_days = 30
  }

  td_secrets = {}
}

terraform {
  source = "${get_path_to_repo_root()}/iac/modules/compute"
}

dependency "networking" {
  config_path = "${dirname(get_terragrunt_dir())}/networking"
    mock_outputs_allowed_terraform_commands = ["validate", "init", "plan"]
    mock_outputs = {
        security_group_id = "sg-0123456789abcdef0"
        public_subnet_id = "subnet-0123456789abcdef0"
    }
}

dependency "registry" {
    config_path = "../../global/registry"
    mock_outputs_allowed_terraform_commands = ["validate", "init", "plan"]
    mock_outputs = {
        ecr_name = "my-repo"
    }
}

dependency "security" {
    config_path = "../../global/security"
    mock_outputs_allowed_terraform_commands = ["validate", "init", "plan"]
    mock_outputs = {
        execution_role_arn = "arn:aws:iam::123456789012:role/EcsTaskExecutionRole"
        task_role_arn      = "arn:aws:iam::123456789012:role/TaskRole"
        scheduler_role_arn = "arn:aws:iam::123456789012:role/SchedulerRole"
    }
}

dependency "logging" {
  config_path = "../logging"
  mock_outputs_allowed_terraform_commands = ["validate", "init", "plan"]
  mock_outputs = {
    cloudwatch_log_group_name = "log-group-name"
  }
}

inputs = {
    # Task Definition Settings
    ecr_name                     = dependency.registry.outputs.ecr_name
    ecr_tag                      = "staging"

    task_cpu                    = 512
    task_definition_environment = templatefile("${dirname(find_in_parent_folders("root.hcl"))}/component_vars/task_definition_env.json", { env = local.td_env })
    task_definition_secrets     = templatefile("${dirname(find_in_parent_folders("root.hcl"))}/component_vars/task_definition_secrets.json", { env = local.td_secrets })
    task_memory                 = 1024

    execution_role_arn  = dependency.security.outputs.execution_role_arn
    task_role_arn       = dependency.security.outputs.task_role_arn

    # Scheduler settings
    network_configuration = {
        security_groups  = [dependency.networking.outputs.security_group_id]
        subnets          = [dependency.networking.outputs.public_subnet_id]
        assign_public_ip = true
    }
    scheduler_role_arn = dependency.security.outputs.scheduler_role_arn
    scheduler_cron_expression = "5 0 * * *"
    scheduler_flexible_time_window_mode = "OFF"
    scheduler_maximum_window_in_minutes = null
    scheduler_timezone = "UTC"

    # Logging settings
    cloudwatch_log_group_name = dependency.logging.outputs.cloudwatch_log_group_name
}
