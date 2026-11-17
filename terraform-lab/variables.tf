
variable "container_name" {
  description = "PostgreSQL container name"
  type        = string
  default     = "terraform-postgres"
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  default     = "ocado"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "orders"
}

variable "postgres_external_port" {
  description = "Host port exposed by PostgreSQL"
  type        = number
  default     = 5433
}

variable "network_name" {
  type = string
}

