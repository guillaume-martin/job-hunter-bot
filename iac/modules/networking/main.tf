data "aws_default_tags" "this" {}

locals {
  name        = data.aws_default_tags.this.tags.Name
  name_hyphen = replace(local.name, "/", "-")
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
    Name = "${local.name_hyphen}-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "${local.name_hyphen}-public-subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${local.name_hyphen}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${local.name_hyphen}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}


#------------------------------------------------------------------------------
# Instance settings
#------------------------------------------------------------------------------
resource "aws_security_group" "task" {
  name        = "${local.name_hyphen}-task"
  description = "Security group for Fargate task"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "${local.name_hyphen}-sg"
  }
}

resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.task.id

  description = "HTTPS egress from task"
  ip_protocol = "tcp"
  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 443
  to_port     = 443

  tags = {
    Name = "${local.name_hyphen}-egress-https"
  }
}
