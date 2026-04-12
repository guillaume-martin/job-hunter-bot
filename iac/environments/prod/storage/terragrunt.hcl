include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}

include "component_vars" {
  path = "${dirname(find_in_parent_folders("root.hcl"))}/component_vars/storage.hcl"
  # Expose component vars so inputs are included in the module inputs below
  expose = true
}


locals {
  # Version of the terraform module to use
  ref = "5.5.0"

  component = basename(get_terragrunt_dir())
}

terraform {
  source = "${include.component_vars.locals.source_loc}?ref=v${local.ref}"
}

inputs = {
  name         = "${include.root.locals.project}-${include.root.locals.environment}-job-cache"
  hash_key     = "job_id"
  billing_mode = "PAY_PER_REQUEST"

  server_side_encryption_enabled = true

  attributes = [
    { name = "job_id", type = "S" },
    { name = "site",   type = "S" },
  ]

  ttl_enabled        = true
  ttl_attribute_name = "expires_at"

  global_secondary_indexes = [
    {
      name            = "site-index"
      hash_key        = "site"
      projection_type = "ALL"
    }
  ]

}
