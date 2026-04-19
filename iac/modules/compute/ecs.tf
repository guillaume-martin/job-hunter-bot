# This module creates an ECS cluster for the Job Hunter Bot application.

resource "aws_ecs_cluster" "this" {
  name = "${local.name_hyphen}-ecs-cluster"
}

resource "aws_ecs_cluster_capacity_providers" "this" {
  cluster_name       = aws_ecs_cluster.this.name
  capacity_providers = ["FARGATE"]
}
