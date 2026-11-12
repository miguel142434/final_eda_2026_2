variable "region_aws" {
  description = "Región de AWS para S3, Glue Data Catalog y Athena."
  type        = string
  default     = "us-east-1"
}

variable "nombre_bucket" {
  description = "Nombre globalmente único del bucket S3 del ejercicio."
  type        = string
}

variable "nombre_base_datos" {
  description = "Nombre de la base de datos en Glue Data Catalog."
  type        = string
  default     = "final_entregas"
}

variable "nombre_workgroup" {
  description = "Nombre del workgroup de Athena."
  type        = string
  default     = "final-entregas"
}
