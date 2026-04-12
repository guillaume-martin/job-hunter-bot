data "aws_default_tags" "this" {}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  name        = data.aws_default_tags.this.tags.Name
  name_hyphen = replace(local.name, "/", "-")
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
resource "aws_iam_role" "execution_role" {
  name               = "${local.name_hyphen}-execution-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
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
    resources = ["arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${var.jobs_table_name}"]
  }

  statement {
    sid       = "SES"
    actions   = ["ses:SendEmail", "ses:SendRawEmail"]
    resources = ["*"]
  }

  statement {
    sid       = "STS"
    actions   = ["sts:AssumeRole"]
    resources = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.task_assume_role_name}"]
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
    resources = ["arn:aws:ecs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:task-definition/*"]
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

#------------------------------------------------------------------------------
# CICD Role and Policy
#------------------------------------------------------------------------------
data "aws_iam_policy_document" "cicd_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = var.cicd_trusted_arns
    }
  }
}

data "aws_iam_policy_document" "cicd_role" {
  statement {
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage",
    ]
    resources = ["arn:aws:ecr:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_repository_name}"]
  }
}

resource "aws_iam_role" "cicd_role" {
  name               = "${local.name_hyphen}-cicd-role"
  assume_role_policy = data.aws_iam_policy_document.cicd_assume_role_policy.json
}

resource "aws_iam_role_policy" "cicd_role" {
  name   = "${local.name_hyphen}-cicd-policy"
  role   = aws_iam_role.cicd_role.id
  policy = data.aws_iam_policy_document.cicd_role.json
}
