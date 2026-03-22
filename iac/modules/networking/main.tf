data "aws_default_tags" "this" {}

locals {
  name = data.aws_default_tags.this.tags.Name
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  instance_tenancy     = "default"
  enable_dns_support   = true # default is true, but explicit is better
  enable_dns_hostnames = true

  tags = {
    Name = "${local.name}-vpc"
  }
}

resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "${local.name}-private-subnet"
  }
}

#------------------------------------------------------------------------------
# Instance settings
#------------------------------------------------------------------------------
resource "aws_security_group" "task" {
  name        = "${local.name}-task"
  description = "Security group for Fargate task"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "${local.name}-sg"
  }
}

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.task.id

  description = "All egress from task"
  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"

  tags = {
    Name = "${local.name}-egress-all"
  }
}
