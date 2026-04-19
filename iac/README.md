# Infrastructure (IaC)

This folder contains the Terraform/OpenTofu code, orchestrated by Terragrunt, that
provisions everything needed to run Job Hunter Bot on AWS: the ECR registry,
IAM roles, DynamoDB cache, VPC, ECS Fargate task, EventBridge schedule and
CloudWatch log group.

## Layout

```
iac/
├── modules/            # Reusable Terraform modules (application-specific)
│   ├── compute/        # ECS cluster, task definition, EventBridge scheduler
│   ├── networking/     # VPC, public subnet, route table, security group
│   ├── security-env/   # Per-environment IAM: execution, task, scheduler roles
│   ├── security-global/# Global IAM: GitHub OIDC provider, CI/CD role
│   └── ses/            # SES verified identity for outbound email
│
└── environments/       # Terragrunt stacks — one deployable unit per folder
    ├── root.hcl        # Shared backend, provider, and default tags
    ├── common_vars.hcl # AWS region, profile, project name, cost center
    ├── component_vars/ # Shared module source + inputs (storage, logging, ...)
    │
    ├── global/         # Cross-environment resources (one copy for the account)
    │   ├── registry/   # ECR repository (uses upstream terraform-aws-ecr)
    │   ├── security/   # OIDC provider + CI/CD role (security-global)
    │   └── ses/        # SES sender identity
    │
    ├── staging/
    │   ├── environment.hcl
    │   ├── networking/
    │   ├── security/   # Execution, task, scheduler roles (security-env)
    │   ├── storage/    # DynamoDB job-cache table (upstream dynamodb module)
    │   ├── logging/    # CloudWatch log group (upstream cloudwatch module)
    │   └── compute/    # ECS task + scheduler
    │
    └── production/     # Same layout as staging
```

`modules/` holds Terraform code; `environments/` holds Terragrunt configuration
that wires modules into a concrete deployment. Some stacks source modules from
this repo (`compute`, `networking`, `security-*`, `ses`), others pull community
modules from GitHub (`registry` uses terraform-aws-ecr, `storage` uses
terraform-aws-dynamodb-table, `logging` uses terraform-aws-cloudwatch).

The split between `security-global` (GitHub OIDC + CI/CD role) and
`security-env` (ECS roles scoped to a single environment) is intentional: it
keeps the blast radius of per-env IAM contained to that environment.

## Prerequisites

- [OpenTofu](https://opentofu.org/) >= 1.0 (or Terraform >= 1.0)
- [Terragrunt](https://terragrunt.gruntwork.io/)
- [AWS CLI](https://aws.amazon.com/cli/) v2
- An AWS account and an IAM user/role with permissions to create the resources
  listed above
- A named AWS CLI profile matching `aws_profile` in
  [`environments/common_vars.hcl`](environments/common_vars.hcl) (default:
  `iac-job-hunter-bot`)

Required environment variables (read via `get_env` at plan/apply time):

| Variable     | Used by                              | Example                   |
| ------------ | ------------------------------------ | ------------------------- |
| `SENDER`     | `global/ses`, `<env>/compute`        | `bot@your-domain.com`     |
| `RECIPIENT`  | `<env>/compute`                      | `you@your-domain.com`     |
| `AI_API_KEY` | `<env>/compute` (stored in SSM)      | your Mistral API key      |

Export them in your shell (or use `direnv`) before any `terragrunt` command.

## Configuration

Three layers of configuration, from most global to most specific:

1. **[`environments/common_vars.hcl`](environments/common_vars.hcl)** — AWS
   region, profile, project name, cost center. Shared by every stack.
2. **`environments/<env>/environment.hcl`** — the environment name
   (`global`, `staging`, `production`). This value feeds resource names, IAM
   scoping, tags, and the state bucket.
3. **Per-stack `terragrunt.hcl`** — module source, inputs, dependencies on
   other stacks.

Resources follow the convention `${project}-${environment}-${component}-*`
(e.g. `job-hunter-bot-staging-compute-ecs-cluster`). The DynamoDB table and
SSM parameter paths are scoped the same way and referenced by the task role.

## First-time setup

### 1. State bucket

Each environment writes its state to its own S3 bucket, named
`iac-tfstate-<environment>` (see [root.hcl](environments/root.hcl)). The
buckets must exist **before** the first `terragrunt` run — the backend is not
auto-bootstrapped.

```bash
aws s3api create-bucket \
  --bucket iac-tfstate-global \
  --region us-east-1 \
  --profile iac-job-hunter-bot
aws s3api put-bucket-versioning \
  --bucket iac-tfstate-global \
  --versioning-configuration Status=Enabled \
  --profile iac-job-hunter-bot
```

Repeat for `iac-tfstate-staging` and `iac-tfstate-production`.

### 2. Configure the AWS profile

```bash
aws configure --profile iac-job-hunter-bot
```

Or rename the profile by editing `aws_profile` in
[`common_vars.hcl`](environments/common_vars.hcl).

### 3. Verify SES sending domain

Email delivery requires a verified SES identity. After the first apply of
`global/ses`, finalize the DKIM/DMARC records at your DNS provider before the
bot can send.

## Deployment

Stacks have dependencies, resolved automatically by Terragrunt. The order
below is the natural DAG of the project.

### Deploy everything in one environment

```bash
# From iac/environments/global — deploy the shared pieces first
terragrunt run-all plan  --working-dir environments/global
terragrunt run-all apply --working-dir environments/global

# Then the target environment
terragrunt run-all plan  --working-dir environments/staging
terragrunt run-all apply --working-dir environments/staging
```

`run-all` walks the dependency graph: `security` before `compute`, `networking`
before `compute`, etc. During `plan` the downstream stacks see
[`mock_outputs`](https://terragrunt.gruntwork.io/docs/reference/config-blocks-and-attributes/#mock_outputs)
for any dep that hasn't been applied yet — this is expected, the real values
flow through at apply time.

### Deploy or re-plan a single stack

```bash
terragrunt --working-dir environments/staging/compute plan
terragrunt --working-dir environments/staging/compute apply
```

### After the first apply

1. Push a container image tagged `staging` (or `production`) to the ECR repo
   created by `global/registry`. The CI/CD role ARN exported by
   `global/security` is used by the GitHub Actions workflow.
2. Confirm the EventBridge schedule exists and triggers the task on the cron
   expression set in `<env>/compute/terragrunt.hcl` (default: `5 0 * * *`).
3. Tail the CloudWatch log group to watch the first run.

## Inspecting deployed resources

```bash
# State-side view
terragrunt --working-dir environments/staging/<stack> state list
terragrunt --working-dir environments/staging/<stack> output

# AWS-side view (all tagged resources)
aws resourcegroupstaggingapi get-resources \
  --tag-filters "Key=project,Values=job-hunter-bot" \
  --query 'ResourceTagMappingList[].ResourceARN' --output table
```

## Teardown

Destroy in reverse dependency order: per-env first, then global.

```bash
terragrunt run-all destroy --working-dir environments/staging
terragrunt run-all destroy --working-dir environments/global
```

The state buckets are **not** managed by Terragrunt — remove them manually if
you want to wipe everything.

## Conventions

- **Naming**: `${project}-${environment}-${component}-*` for AWS resources;
  default tags `project`, `env`, `component`, `managed-by`, `cost-center`,
  `owner` applied by [root.hcl](environments/root.hcl).
- **Versions**: the AWS provider is pinned to `~> 6.0`. Community modules are
  pinned by tag (`ref=v<version>`) in their `terragrunt.hcl`.
- **Secrets**: never committed. `SENDER`, `RECIPIENT`, `AI_API_KEY` come from
  the shell; `AI_API_KEY` is written to SSM Parameter Store by the compute
  stack and injected into the ECS task at runtime.
