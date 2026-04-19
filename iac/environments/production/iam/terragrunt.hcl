include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

include "component_vars" {
  path = "${dirname(find_in_parent_folders("root.hcl"))}/component_vars/iam.hcl"
  # Expose component vars so inputs are included in the module inputs below
  expose = true
}

terraform {
    source = include.component_vars.locals.source_loc
}
