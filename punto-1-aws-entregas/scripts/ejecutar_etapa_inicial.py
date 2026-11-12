"""Carga los días 1 y 2 y guarda las consultas de la etapa inicial."""

import argparse
import csv
import json
import sys
from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urlsplit

import boto3
from botocore.exceptions import BotoCoreError, ClientError


RAIZ = Path(__file__).resolve().parents[1]
DIAS_INICIALES = ("2026-10-01", "2026-10-02")
CONSULTAS = (
    "intentos_por_fecha_estado",
    "porcentaje_exito_por_fecha_ciudad",
    "duracion_promedio_2026-10-02",
)
COLUMNAS_EVIDENCIA = ("etapa", "archivo_sql", "id_ejecucion", "archivo_resultado")


def esperar_resultado(athena, id_ejecucion):
    limite = monotonic() + 300
    while True:
        ejecucion = athena.get_query_execution(
            QueryExecutionId=id_ejecucion
        )["QueryExecution"]
        estado = ejecucion["Status"]
        if estado["State"] == "SUCCEEDED":
            return ejecucion["ResultConfiguration"]["OutputLocation"]
        if estado["State"] in {"FAILED", "CANCELLED"}:
            motivo = estado.get("StateChangeReason", "Sin detalle de Athena")
            raise RuntimeError(f"Athena {id_ejecucion}: {estado['State']}. {motivo}")
        if monotonic() >= limite:
            raise RuntimeError(
                f"Athena {id_ejecucion}: sigue en {estado['State']} tras 300 segundos."
            )
        sleep(2)


def ejecutar(region):
    ruta_outputs = RAIZ / "evidencias/outputs.json"
    salidas = json.loads(ruta_outputs.read_text(encoding="utf-8-sig"))
    bucket = salidas["bucket"]["value"]
    base_datos = salidas["base_datos"]["value"]
    workgroup = salidas["workgroup"]["value"]

    claves = [f"entregas/fecha={dia}/entregas.csv" for dia in DIAS_INICIALES]
    for clave in claves:
        origen = RAIZ / "data" / clave
        if not origen.is_file():
            raise FileNotFoundError(f"No se encontró {origen}")
    consultas = {
        nombre: (RAIZ / "consultas" / f"{nombre}.sql").read_text(encoding="utf-8-sig")
        for nombre in CONSULTAS
    }

    sesion = boto3.Session(region_name=region)
    s3 = sesion.client("s3")
    athena = sesion.client("athena")
    tercer_dia = s3.list_objects_v2(
        Bucket=bucket, Prefix="entregas/fecha=2026-10-03/", MaxKeys=1
    )
    if tercer_dia.get("Contents"):
        raise RuntimeError("La partición del 2026-10-03 ya contiene objetos en S3.")

    for clave in claves:
        s3.upload_file(str(RAIZ / "data" / clave), bucket, clave)
        print(f"Cargado s3://{bucket}/{clave}", flush=True)

    carpeta_resultados = RAIZ / "resultados/inicial"
    carpeta_resultados.mkdir(parents=True, exist_ok=True)
    ruta_evidencia = RAIZ / "evidencias/ejecuciones_athena.csv"

    for nombre, sql in consultas.items():
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

        destino = carpeta_resultados / f"{nombre}.csv"
        s3.download_file(ubicacion.netloc, clave_resultado, str(destino))
        with ruta_evidencia.open("a+", encoding="utf-8", newline="") as archivo:
            registro = csv.writer(archivo)
            if archivo.tell() == 0:
                registro.writerow(COLUMNAS_EVIDENCIA)
            registro.writerow(
                (
                    "inicial",
                    f"consultas/{nombre}.sql",
                    id_ejecucion,
                    destino.relative_to(RAIZ).as_posix(),
                )
            )
        print(f"Guardado {destino.relative_to(RAIZ).as_posix()}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="us-east-1", help="Región usada por Terraform")
    args = parser.parse_args()
    try:
        ejecutar(args.region)
    except (BotoCoreError, ClientError, OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"Error en la etapa inicial: {error}", file=sys.stderr)
        sys.exit(1)
