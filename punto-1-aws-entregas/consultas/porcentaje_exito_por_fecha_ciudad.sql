SELECT
    fecha,
    ciudad,
    CAST(
        ROUND(100e0 * SUM(CASE WHEN estado = 'entregado' THEN 1 ELSE 0 END) / COUNT(*), 2)
        AS DECIMAL(5, 2)
    ) AS porcentaje_exito
FROM entregas
GROUP BY fecha, ciudad
ORDER BY fecha ASC, ciudad ASC;
