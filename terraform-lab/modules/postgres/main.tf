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


resource "docker_network" "backend" {
  name = var.network_name
  driver      = "bridge"
  ipam_driver = "default"
  ipam_options = {
    driver = "host-local"
  }
}


resource "docker_image" "postgres" {
  name         = "postgres:17-alpine"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name     = var.container_name
  image    = docker_image.postgres.image_id
  pid_mode = "private"

  networks_advanced {
    name = docker_network.backend.name
  }

  ulimit {
    name = "RLIMIT_NOFILE"
    hard = 1048576
    soft = 1048576
  }

  ulimit {
    name = "RLIMIT_NPROC"
    hard = 85007
    soft = 85007
  }

  ports {
    internal = 5432
    external = var.postgres_external_port
  }

  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}"
  ]
}

