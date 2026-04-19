ENV ?= staging
VALID_ENVS := global staging production

.PHONY: help state plan outputs _check_env

help:
	@echo "Usage: make <target> [ENV=<global|staging|production>]"
	@echo ""
	@echo "Targets:"
	@echo "  state    List resources tracked in Terraform state for ENV"
	@echo "  plan     Run terragrunt plan across all stacks in ENV"
	@echo "  outputs  Show outputs of every stack in ENV"
	@echo ""
	@echo "ENV defaults to 'staging' if not set."

_check_env:
	@echo "$(VALID_ENVS)" | tr ' ' '\n' | grep -qx "$(ENV)" || \
		(echo "ENV must be one of: $(VALID_ENVS)" >&2; exit 1)

state: _check_env
	@terragrunt state --all list \
		--working-dir environments/$(ENV) \
		--non-interactive

plan: _check_env
	@terragrunt plan --all --working-dir environments/$(ENV)

outputs: _check_env
	@terragrunt output --all --working-dir environments/$(ENV)
