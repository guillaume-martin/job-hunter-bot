locals {
  # Define the source location so different versions of the module can be
  # deployed in different environments.
  repo       = "../../../modules/security-env"
  source_loc = local.repo
}
