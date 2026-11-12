SELECT
    fecha,
    estado,
    COUNT(*) AS total_intentos
FROM entregas
GROUP BY fecha, estado
ORDER BY fecha ASC, estado ASC;
