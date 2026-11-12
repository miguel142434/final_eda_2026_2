import json
import sqlite3
import urllib.request

with urllib.request.urlopen("http://localhost:8080/health", timeout=5) as response:
    health = json.load(response)
assert health["metadatabase"]["status"] == "healthy", health
assert health["scheduler"]["status"] == "healthy", health
with sqlite3.connect("/state/airflow.db", timeout=5) as connection:
    assert connection.execute(
        "select 1 from serialized_dag where dag_id = ?", ("examen_ventas",)
    ).fetchone(), "El scheduler todavía no ha registrado el DAG del examen"
