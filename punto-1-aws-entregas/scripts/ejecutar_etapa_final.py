"""Carga el tercer día y guarda las consultas de la etapa final."""

import argparse
import csv
import json
import sys
from collections import Counter
from urllib.parse import urlsplit

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ejecutar_etapa_inicial import COLUMNAS_EVIDENCIA, RAIZ, esperar_resultado


FECHA = "2026-10-03"
ARCHIVO_VERIFICACION = "consultas/verificacion_tercer_dia.sql"
RESULTADOS_VERIFICACION = (
    "verificacion_tercer_dia",
    "conteos_tercer_dia_por_estado",
    "total_filas_tabla",
)
AGREGADOS = ("intentos_por_fecha_estado", "porcentaje_exito_por_fecha_ciudad")


def verificar_resultados(carpeta, conteos_esperados):
    detalle, conteos, total = (
        leer_csv(carpeta / f"{nombre}.csv") for nombre in RESULTADOS_VERIFICACION
    )
    if len(detalle) != 6 or any(fila["fecha"] != FECHA for fila in detalle):
        raise RuntimeError(f"Se esperaban seis registros del {FECHA} en Athena.")
    if Counter(fila["estado"] for fila in detalle) != conteos_esperados:
        raise RuntimeError("Los estados del detalle no coinciden con el CSV de entrada.")
    conteos_obtenidos = {fila["estado"]: int(fila["total_intentos"]) for fila in conteos}
    if len(conteos) != len(conteos_esperados) or conteos_obtenidos != conteos_esperados:
        raise RuntimeError("Los conteos por estado del tercer día son incorrectos.")
    if len(total) != 1 or int(total[0]["total_filas"]) != 18:
        raise RuntimeError("Se esperaban 18 registros en total en Athena.")
    print("Verificación correcta: seis registros del tercer día y 18 en total.", flush=True)


def leer_csv(ruta):
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def ejecutar(region):
    salidas = json.loads((RAIZ / "evidencias/outputs.json").read_text(encoding="utf-8-sig"))
    bucket = salidas["bucket"]["value"]
    base_datos = salidas["base_datos"]["value"]
    workgroup = salidas["workgroup"]["value"]

    clave = f"entregas/fecha={FECHA}/entregas.csv"
    origen = RAIZ / "data" / clave
    conteos_esperados = Counter(fila["estado"] for fila in leer_csv(origen))
    if sum(conteos_esperados.values()) != 6:
        raise RuntimeError(f"El CSV de entrada del {FECHA} debe contener seis registros.")

    # El archivo del ejercicio contiene tres SELECT, sin punto y coma interno.
    sql_verificacion = (RAIZ / ARCHIVO_VERIFICACION).read_text(encoding="utf-8-sig")
    sentencias = [parte.strip() for parte in sql_verificacion.split(";") if parte.strip()]
    if len(sentencias) != len(RESULTADOS_VERIFICACION):
        raise RuntimeError(f"Se esperaban tres sentencias en {ARCHIVO_VERIFICACION}.")
    verificaciones = [
        (ARCHIVO_VERIFICACION, nombre, sql)
        for nombre, sql in zip(RESULTADOS_VERIFICACION, sentencias)
    ]
    agregados = []
    for nombre in AGREGADOS:
        ruta = f"consultas/{nombre}.sql"
        agregados.append((ruta, nombre, (RAIZ / ruta).read_text(encoding="utf-8-sig")))

    sesion = boto3.Session(region_name=region)
    s3 = sesion.client("s3")
    athena = sesion.client("athena")
    s3.upload_file(str(origen), bucket, clave)
    print(f"Cargado s3://{bucket}/{clave}", flush=True)

    carpeta = RAIZ / "resultados/final"
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_evidencia = RAIZ / "evidencias/ejecuciones_athena.csv"

    for consultas in (verificaciones, agregados):
        for archivo_sql, nombre, sql in consultas:
            respuesta = athena.start_query_execution(
                QueryString=sql,
                QueryExecutionContext={"Catalog": "AwsDataCatalog", "Database": base_datos},
                WorkGroup=workgroup,
            )
            id_ejecucion = respuesta["QueryExecutionId"]
            print(f"{nombre}: {id_ejecucion}", flush=True)
            ubicacion = urlsplit(esperar_resultado(athena, id_ejecucion))
            clave_resultado = ubicacion.path.lstrip("/")
            if ubicacion.scheme != "s3" or not ubicacion.netloc or not clave_resultado.endswith(".csv"):
                raise RuntimeError(f"Athena {id_ejecucion}: ubicación de CSV inesperada.")

            destino = carpeta / f"{nombre}.csv"
            s3.download_file(ubicacion.netloc, clave_resultado, str(destino))
            ruta_resultado = destino.relative_to(RAIZ).as_posix()
            with ruta_evidencia.open("a+", encoding="utf-8", newline="") as archivo:
                registro = csv.writer(archivo)
                if archivo.tell() == 0:
                    registro.writerow(COLUMNAS_EVIDENCIA)
                registro.writerow(("final", archivo_sql, id_ejecucion, ruta_resultado))
            print(f"Guardado {ruta_resultado}", flush=True)

        if consultas is verificaciones:
            verificar_resultados(carpeta, conteos_esperados)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="us-east-1", help="Región usada por Terraform")
    args = parser.parse_args()
    try:
        ejecutar(args.region)
    except (BotoCoreError, ClientError, OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"Error en la etapa final: {error}", file=sys.stderr)
        sys.exit(1)
