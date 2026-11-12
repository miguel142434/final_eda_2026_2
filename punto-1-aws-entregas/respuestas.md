# Respuestas conceptuales

## 1. ¿Por qué se pudo consultar el día 3 sin registrar una partición nueva?

Athena leyó las reglas de Partition Projection definidas en las propiedades de la tabla externa de Glue. Al ejecutar la consulta, generó los valores de `fecha` entre `2026-10-01` y `2026-10-03`, ambos incluidos, con un intervalo de un día y el formato `yyyy-MM-dd`. Para cada fecha pertinente, sustituyó su valor en la plantilla `s3://<bucket>/entregas/fecha=${fecha}/` y consultó los objetos del prefijo resultante.

El 3 de octubre ya estaba dentro del rango desde el despliegue inicial. Su prefijo estaba vacío en la primera etapa. Después de subir `entregas/fecha=2026-10-03/entregas.csv`, Athena encontró el archivo al consultar la misma tabla, sin ejecutar un crawler ni registrar una partición individual en Glue. La [consulta de detalle](resultados/final/verificacion_tercer_dia.csv) devolvió seis filas del día 3 y el [conteo de la tabla](resultados/final/total_filas_tabla.csv) devolvió 18. Los identificadores de ambas consultas quedaron en el [registro de ejecuciones](evidencias/ejecuciones_athena.csv). [Documentación de Partition Projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html)

## 2. ¿Qué pasaría si se subiera un archivo para el 4 de octubre?

Con la configuración actual, el archivo podría existir en S3, pero Athena no proyectaría el valor `2026-10-04` porque el límite superior es `2026-10-03`. Una consulta de detalle con `WHERE fecha = '2026-10-04'` se ejecutaría correctamente y devolvería cero filas. [Comportamiento de Athena fuera del rango proyectado](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html)

Para incluir ese día, en [infraestructura/principal.tf](infraestructura/principal.tf) se debe ampliar el límite superior de la propiedad `projection.fecha.range` dentro de `parameters` del recurso `aws_glue_catalog_table.entregas`:

```hcl
"projection.fecha.range" = "2026-10-01,2026-10-04"
```

Después de aplicar el cambio con Terraform, Athena podrá resolver el prefijo `entregas/fecha=2026-10-04/` y leer el CSV si conserva el esquema y la ruta esperados. [Propiedades de proyección de fechas](https://docs.aws.amazon.com/athena/latest/ug/partition-projection-supported-types.html#partition-projection-date-type)
