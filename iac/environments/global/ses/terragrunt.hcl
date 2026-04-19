include "root" {
  path   = find_in_parent_folders("root.hcl")
  expose = true
}


terraform {
  source = "${include.root.locals.modules_path}/ses"
}

inputs = {
  sender_email   = get_env("SENDER")
}
