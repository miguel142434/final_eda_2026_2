output "bucket" {
  description = "Nombre del bucket S3 del ejercicio."
  value       = aws_s3_bucket.entregas.bucket
}

output "base_datos" {
  description = "Nombre de la base de datos en Glue Data Catalog."
  value       = aws_glue_catalog_database.entregas.name
}

output "tabla" {
  description = "Nombre de la tabla externa de entregas."
  value       = aws_glue_catalog_table.entregas.name
}

output "workgroup" {
  description = "Nombre del workgroup de Athena."
  value       = aws_athena_workgroup.entregas.name
}
