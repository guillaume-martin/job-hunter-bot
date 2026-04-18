include "root" {
    path   = find_in_parent_folders("root.hcl")
    expose = true
}

terraform {
    source = "${get_path_to_repo_root()}/iac/modules/networking"
}

inputs = {
    vpc_cidr           = "10.1.0.0/16"
    public_subnet_cidr = "10.1.1.0/24"
}
