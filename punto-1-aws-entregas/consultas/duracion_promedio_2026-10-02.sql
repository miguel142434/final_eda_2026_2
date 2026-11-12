SELECT
    fecha,
    CAST(ROUND(AVG(duracion_minutos), 2) AS DECIMAL(12, 2)) AS duracion_promedio_minutos
FROM entregas
WHERE fecha = '2026-10-02'
    AND estado = 'entregado'
GROUP BY fecha;
