locals {
  component = basename(get_terragrunt_dir())
}

include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

include "component_vars" {
    path   = find_in_parent_folders("component_vars/networking.hcl")
    expose = true
}

terraform {
    source = include.component_vars.locals.source_loc
}

inputs = {
    vpc_cidr           = "10.0.0.0/16"
    public_subnet_cidr = "10.0.1.0/24"
}
