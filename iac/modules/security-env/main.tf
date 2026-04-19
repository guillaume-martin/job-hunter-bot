data "aws_default_tags" "this" {}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  account_id      = data.aws_caller_identity.current.account_id
  region          = data.aws_region.current.region
  project         = data.aws_default_tags.this.tags.project
  env             = data.aws_default_tags.this.tags.env
  name            = data.aws_default_tags.this.tags.Name
  name_hyphen     = replace(local.name, "/", "-")
  jobs_table_name = "${local.project}-${local.env}-jobs-cache"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

#------------------------------------------------------------------------------
# Execution Role for ECS Tasks
#------------------------------------------------------------------------------
data "aws_iam_policy_document" "execution_role_policy" {
  statement {
    sid = "SSM"
    actions = [
      "ssm:GetParameters",
    ]
    resources = [
      "arn:aws:ssm:${local.region}:${local.account_id}:parameter/${local.project}/${local.env}/*",
    ]
  }
}

resource "aws_iam_role" "execution_role" {
  name               = "${local.name_hyphen}-execution-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

resource "aws_iam_role_policy" "execution_role" {
  name   = "${local.name_hyphen}-execution-policy"
  role   = aws_iam_role.execution_role.id
  policy = data.aws_iam_policy_document.execution_role_policy.json
}

resource "aws_iam_role_policy_attachment" "execution_role" {
  role       = aws_iam_role.execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


#------------------------------------------------------------------------------
# Task Role for ECS Tasks (application permissions)
#------------------------------------------------------------------------------
data "aws_iam_policy_document" "task_role_policy" {
  statement {
    sid = "DynamoDB"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query",
    ]
    resources = ["arn:aws:dynamodb:${local.region}:${local.account_id}:table/${local.jobs_table_name}"]
  }

  statement {
    sid       = "SES"
    actions   = ["ses:SendEmail", "ses:SendRawEmail"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "task_role" {
  name               = "${local.name_hyphen}-task-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

resource "aws_iam_role_policy" "task_role" {
  name   = "${local.name_hyphen}-task-policy"
  role   = aws_iam_role.task_role.id
  policy = data.aws_iam_policy_document.task_role_policy.json
}


#------------------------------------------------------------------------------
# Scheduler Role and Policy
#------------------------------------------------------------------------------
data "aws_iam_policy_document" "scheduler_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler_role" {
  name               = "${local.name_hyphen}-scheduler-role"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_role_policy.json
}

data "aws_iam_policy_document" "scheduler_role_policy" {
  statement {
    actions   = ["ecs:RunTask"]
    resources = ["arn:aws:ecs:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:task-definition/*"]
  }
  statement {
    actions   = ["iam:PassRole"]
    resources = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*"]
  }
}

resource "aws_iam_role_policy" "scheduler_role" {
  name   = "${local.name_hyphen}-scheduler-policy"
  role   = aws_iam_role.scheduler_role.id
  policy = data.aws_iam_policy_document.scheduler_role_policy.json
}
