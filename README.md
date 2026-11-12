# Examen final de Ingeniería de Datos · 2026-2

**Estudiante:** Miguel Ángel Zuleta Zuleta

**Hilo de trabajo con IA:** https://chatgpt.com/s/cx_6af5b574d8908191a08b474a3fb69c62

## Punto 1 · AWS Entregas

Los CSV diarios se almacenan en un bucket S3 privado bajo `entregas/fecha=YYYY-MM-DD/`. Glue Data Catalog define el esquema de la tabla externa. Athena usa Partition Projection para resolver los prefijos de las fechas del 1 al 3 de octubre de 2026 y guarda las salidas del workgroup en `resultados-athena/`.

1. Entra a [punto-1-aws-entregas](punto-1-aws-entregas/) y sigue el [README de AWS](punto-1-aws-entregas/README.md#reproducción-de-la-entrega) para configurar `infraestructura/terraform.tfvars`, validar, revisar el plan y desplegar.
2. Con las credenciales y región del despliegue, ejecuta `uv run --with boto3 scripts/ejecutar_etapa_inicial.py` para cargar los días 1 y 2. Revisa los resultados iniciales antes de ejecutar `uv run --with boto3 scripts/ejecutar_etapa_final.py` para cargar el día 3 y verificar seis registros de ese día y 18 filas totales.
3. Consulta el [registro de Athena](punto-1-aws-entregas/evidencias/ejecuciones_athena.csv), los [resultados iniciales](punto-1-aws-entregas/resultados/inicial/), los [finales](punto-1-aws-entregas/resultados/final/) y las [respuestas conceptuales](punto-1-aws-entregas/respuestas.md).

## Punto 2 · dbt, Airflow y DuckDB

Airflow ejecuta `dbt source freshness` sobre la fuente de ventas usando `_loaded_at`. El umbral de advertencia es 12 horas y el de error es 24 horas. Cuando la comprobación permite continuar, dbt construye `analytics.ventas_diarias` en DuckDB con una fila por fecha de negocio. Si freshness falla, Airflow deja `construir_resumen` en `upstream_failed` y conserva la tabla previa.

1. Entra a [punto-2-dbt-ventas](punto-2-dbt-ventas/) y sigue el [README de ventas](punto-2-dbt-ventas/README.md) para iniciar Docker Compose y abrir Airflow en `http://localhost:8080`.
2. Prepara `bash scripts/examen.sh scenario actualizada`, dispara el DAG `examen_ventas` y consulta el resumen. Después prepara `bash scripts/examen.sh scenario desactualizada`, dispara una nueva ejecución y vuelve a consultar la tabla.
3. Revisa las [evidencias de Airflow y de las consultas](punto-2-dbt-ventas/evidencias/) y las [respuestas conceptuales](punto-2-dbt-ventas/respuestas.md).

## Capturas y cierre

La [guía de cierre](CIERRE.md) indica qué capturas guardar, cuáles ya existen y cómo registrar la eliminación desde el directorio original de Terraform.
