terraform {
  required_version = ">= 1.5"
}
variable "cluster_name" { default = "cnf-lab" }
variable "kind_config" { default = "../kind-config.yaml" }

resource "null_resource" "kind" {
  provisioner "local-exec" {
    command = "kind create cluster --name ${var.cluster_name} --config ${var.kind_config} || true"
  }
  provisioner "local-exec" {
    when    = destroy
    command = "kind delete cluster --name cnf-lab || true"
  }
}
output "next" { value = "kind load docker-image cnf:local cnf-healer:local --name cnf-lab" }
