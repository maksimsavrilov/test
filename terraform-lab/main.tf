
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///run/user/1000/podman/podman.sock"
}


module "postgres" {
  source = "./modules/postgres"

  container_name         = var.container_name
  postgres_user          = var.postgres_user
  postgres_password      = var.postgres_password
  postgres_db            = var.postgres_db
  postgres_external_port = var.postgres_external_port
  network_name 		 = var.network_name
}

