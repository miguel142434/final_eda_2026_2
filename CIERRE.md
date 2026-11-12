# Capturas y cierre de la entrega

Guarda las capturas en las carpetas indicadas dentro de este repositorio. Conserva visibles el nombre del recurso, la región o el ID de ejecución según corresponda. Recorta la identidad de la cuenta y cualquier credencial, token o dato personal antes de publicar.

## 1. AWS antes de destruir los recursos

Guarda las capturas en `punto-1-aws-entregas/evidencias/`.

| Archivo | Dónde tomar la captura y qué debe verse |
| --- | --- |
| `s3_prefijos_bucket.png` | S3 → bucket → **Objects**. Deben verse `entregas/` y `resultados-athena/`. Puedes recortar y reutilizar `Evidencia_BucketS3_AWS_console.png` del espacio de trabajo. |
| `s3_particiones_finales.png` | S3 → bucket → **Objects** → `entregas/`. Muestra `fecha=2026-10-01/`, `fecha=2026-10-02/` y `fecha=2026-10-03/`. |
| `s3_objeto_dia_3.png` | Dentro de `fecha=2026-10-03/`, muestra `entregas.csv` y la ruta en el encabezado. |
| `s3_bloqueo_acceso_publico.png` | S3 → bucket → **Permissions** → **Block public access**. Muestra que el bloqueo está activado. |
| `glue_tabla_entregas.png` | Glue → **Data Catalog** → **Tables** → `final_entregas.entregas`. Muestra la ubicación S3, las cinco columnas y `fecha` como clave de partición. Si la vista requiere desplazamiento, añade `glue_esquema_entregas.png`. |
| `glue_partition_projection.png` | Detalle de la misma tabla → propiedades. Muestra `projection.enabled`, las propiedades `projection.fecha.*` y `storage.location.template`. Si se dividen en dos vistas, añade `glue_partition_projection_ruta.png`. |
| `athena_workgroup_resultados.png` | Athena → **Workgroups** → `final-entregas`. Muestra el prefijo S3 `resultados-athena/` como ubicación de resultados. |
| `athena_inicial_intentos.png` | Athena → historial de consultas → abre la ejecución **inicial** de intentos usando su ID del CSV de evidencias. Muestra estado exitoso, ID y resultados de los días 1 y 2. |
| `athena_final_dia_3.png` | Abre la ejecución final de detalle del día 3. Muestra estado exitoso, ID y los seis registros. |
| `athena_final_total_18.png` | Abre la ejecución final que generó `total_filas_tabla.csv`. Muestra el ID y `total_filas = 18`. |
| `terminal_terraform_aplicacion.png` | Abre en terminal `evidencias/aplicacion_terraform.txt` y muestra `Apply complete!` y los outputs. Usa el registro ya guardado. |

La evidencia principal de la etapa inicial son sus tres CSV y los IDs de ejecución. Si Athena ya no muestra los resultados históricos, conserva esos archivos y deja constancia de que la captura histórica no está disponible. Una nueva ejecución con los tres archivos cargados corresponde a la etapa final.

## 2. Airflow y terminal antes de detener el entorno

Guarda las capturas en `punto-2-dbt-ventas/evidencias/`.

| Archivo | Dónde tomar la captura y qué debe verse |
| --- | --- |
| `airflow_actualizada_success.png` | Airflow → `examen_ventas` → selecciona la ejecución actualizada → **Grid** o **Graph**. Muestra el ID de la ejecución y ambas tareas en `success`. |
| `airflow_desactualizada_bloqueada.png` | Selecciona la ejecución desactualizada y muestra su ID, `verificar_freshness` en `failed` y `construir_resumen` en `upstream_failed`. La vista general existente está en `airflow_ejecuciones.png`. |
| `airflow_freshness_log.png` | En la ejecución desactualizada, abre `verificar_freshness` → **Logs**. Captura la línea de error de dbt si aparece y el código de salida. Las capturas existentes `Evidencia_fail_freshness.png` y `airflow_evento_fallido.png` corresponden al historial de eventos. Si el log de tarea solo muestra el código de salida, usa el log de dbt de esa ejecución como respaldo y conserva el resumen en `respuestas.md`. |
| `Resumen_antes_del_bloqueo.png` | Ya existe. Muestra el comando de consulta y las tres filas del resumen previo. |
| `Evidencia_datos_intactos.png` | Ya existe. Muestra la preparación del escenario desactualizado y las mismas tres filas al consultar el resumen. |

## 3. Limpieza y entrega

1. Guarda las capturas y revisa que se abran. Confirma que están los resultados de las dos etapas, los IDs, los outputs de Terraform y las respuestas de ambos puntos. Pega en el README principal el enlace al hilo y verifica que el docente pueda consultarlo.
2. Desde el directorio original `DE-Final-Entregas`, usa el perfil de AWS del despliegue. Ese directorio conserva `infraestructura/terraform.tfvars` y el estado de Terraform. Revisa el plan que imprime `destroy` y confirma con `yes`. El bucket tiene `force_destroy = true` y se eliminarán también sus objetos.

   ```powershell
   terraform -chdir=infraestructura destroy -no-color 2>&1 |
     Tee-Object -FilePath evidencias/eliminacion_terraform.txt
   if ($LASTEXITCODE -ne 0) { throw 'Terraform destroy falló. Revisa el registro.' }
   Copy-Item -LiteralPath evidencias/eliminacion_terraform.txt -Destination ../entrega-final/punto-1-aws-entregas/evidencias/
   ```

3. Verifica que el registro de eliminación contenga `Destroy complete!`. Guarda también una captura de esa salida como `punto-1-aws-entregas/evidencias/terminal_terraform_eliminacion.png` si quieres acompañar el registro de texto.
4. Para apagar Airflow, ejecuta `docker compose stop` desde el directorio original `DE-Final-Ventas`. Esto conserva los volúmenes.
5. En `entrega-final/`, revisa `git status --short --untracked-files=all` antes de publicar. Entrega el enlace del repositorio y comprueba el acceso del docente.
