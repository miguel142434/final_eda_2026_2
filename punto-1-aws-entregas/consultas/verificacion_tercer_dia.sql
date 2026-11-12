-- Ejecutar y exportar cada sentencia por separado en Athena.

-- verificacion_tercer_dia.csv
SELECT
    fecha,
    id_envio,
    ciudad,
    transportadora,
    estado,
    duracion_minutos
FROM entregas
WHERE fecha = '2026-10-03'
ORDER BY id_envio ASC;

-- conteos_tercer_dia_por_estado.csv
SELECT
    fecha,
    estado,
    COUNT(*) AS total_intentos
FROM entregas
WHERE fecha = '2026-10-03'
GROUP BY fecha, estado
ORDER BY estado ASC;

-- total_filas_tabla.csv
SELECT COUNT(*) AS total_filas
FROM entregas;
