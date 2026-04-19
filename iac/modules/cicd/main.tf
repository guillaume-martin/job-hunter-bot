data "aws_default_tags" "this" {}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  project     = data.aws_default_tags.this.tags.project
  name        = data.aws_default_tags.this.tags.Name
  name_hyphen = replace(local.name, "/", "-")
}


#------------------------------------------------------------------------------
# AWS Service-Linked Roles
# SLRs are account-wide prerequisites that must exist before their services
# can be used. Provisioned here since the CI/CD stack is also account-scoped.
#------------------------------------------------------------------------------
resource "aws_iam_service_linked_role" "ecs" {
  aws_service_name = "ecs.amazonaws.com"
}


#------------------------------------------------------------------------------
# CICD Role and Policy
#------------------------------------------------------------------------------
data "aws_iam_policy_document" "cicd_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        for s in var.github_allowed_subs :
        "repo:${var.github_user}/${var.github_repo}:${s}"
      ]
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
    resources = ["arn:aws:ecr:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:repository/${var.ecr_repository_name}"]
  }
}

resource "aws_iam_role" "cicd_role" {
  name               = "${local.name_hyphen}-role"
  assume_role_policy = data.aws_iam_policy_document.cicd_assume_role_policy.json
}

resource "aws_iam_role_policy" "cicd_role" {
  name   = "${local.name_hyphen}-policy"
  role   = aws_iam_role.cicd_role.id
  policy = data.aws_iam_policy_document.cicd_role.json
}


#------------------------------------------------------------------------------
# GitHubActions
#------------------------------------------------------------------------------
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}
