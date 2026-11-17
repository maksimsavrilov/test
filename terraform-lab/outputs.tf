output "container_name" {
  description = "PostgreSQL container name"
  value       = module.postgres.container_name
}

output "container_id" {
  description = "PostgreSQL container ID"
  value       = module.postgres.container_id
}

output "postgres_connection" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.postgres_user}:<password>@localhost:${var.postgres_external_port}/${var.postgres_db}"
}

