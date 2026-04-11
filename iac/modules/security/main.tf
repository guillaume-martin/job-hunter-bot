data "aws_default_tags" "this" {}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  name        = data.aws_default_tags.this.tags.Name
  name_hyphen = replace(local.name, "/", "-")
  # Fall back to account root if no specific principals are provided
  cicd_trusted_arns = length(var.cicd_trusted_arns) > 0 ? var.cicd_trusted_arns : ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
}

data "aws_iam_policy_document" "execution_role_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution_role" {
  name               = "${local.name_hyphen}-execution-role"
  assume_role_policy = data.aws_iam_policy_document.execution_role_trust.json
}

resource "aws_iam_role_policy_attachment" "execution_role" {
  role       = aws_iam_role.execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


data "aws_iam_policy_document" "cicd_role_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = local.cicd_trusted_arns
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
  assume_role_policy = data.aws_iam_policy_document.cicd_role_trust.json
}

resource "aws_iam_role_policy" "cicd_role" {
  name   = "${local.name_hyphen}-cicd-policy"
  role   = aws_iam_role.cicd_role.id
  policy = data.aws_iam_policy_document.cicd_role.json
}
