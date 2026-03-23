include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

locals {
  component    = basename(get_terragrunt_dir())
}

terraform {
    source = "../../modules/security"
}

inputs = {

}
