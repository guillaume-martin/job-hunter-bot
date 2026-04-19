include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

include "component_vars" {
  path = "${dirname(find_in_parent_folders("root.hcl"))}/component_vars/logging.hcl"
  # Expose component vars so inputs are included in the module inputs below
  expose = true
}

locals {
  # Version of the terraform module to use
  ref = "5.7.2"

  name_hyphen = replace(include.root.locals.name, "/", "-")
}

terraform {
  source = "${include.component_vars.locals.source_loc}?ref=v${local.ref}"
}

inputs = {
  name              = "/ecs/${local.name_hyphen}"
  retention_in_days = 7
}
