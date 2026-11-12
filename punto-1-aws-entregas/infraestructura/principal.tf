terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region_aws
}

locals {
  ubicacion_entregas   = "s3://${aws_s3_bucket.entregas.bucket}/entregas/"
  ubicacion_resultados = "s3://${aws_s3_bucket.entregas.bucket}/resultados-athena/"
}

resource "aws_s3_bucket" "entregas" {
  bucket        = var.nombre_bucket
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "entregas" {
  bucket = aws_s3_bucket.entregas.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_glue_catalog_database" "entregas" {
  name = var.nombre_base_datos
}

resource "aws_glue_catalog_table" "entregas" {
  name          = "entregas"
  database_name = aws_glue_catalog_database.entregas.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL                         = "TRUE"
    classification                   = "csv"
    "skip.header.line.count"         = "1"
    "projection.enabled"             = "true"
    "projection.fecha.type"          = "date"
    "projection.fecha.format"        = "yyyy-MM-dd"
    "projection.fecha.interval"      = "1"
    "projection.fecha.interval.unit" = "DAYS"
    "projection.fecha.range"         = "2026-10-01,2026-10-03"
    "storage.location.template"      = "${local.ubicacion_entregas}fecha=$${fecha}/"
  }

  partition_keys {
    name = "fecha"
    type = "string"
  }

  storage_descriptor {
    location      = local.ubicacion_entregas
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"

      parameters = {
        "field.delim"          = ","
        "serialization.format" = ","
      }
    }

    columns {
      name = "id_envio"
      type = "string"
    }

    columns {
      name = "ciudad"
      type = "string"
    }

    columns {
      name = "transportadora"
      type = "string"
    }

    columns {
      name = "estado"
      type = "string"
    }

    columns {
      name = "duracion_minutos"
      type = "int"
    }
  }
}

resource "aws_athena_workgroup" "entregas" {
  name          = var.nombre_workgroup
  force_destroy = true

  configuration {
    enforce_workgroup_configuration = true

    result_configuration {
      output_location = local.ubicacion_resultados
    }
  }
}
