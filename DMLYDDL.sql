use proyectos_informaticos;

-- =============================================
-- CONSULTAS DE INSERCIÓN
-- =============================================
INSERT INTO gastos (Descripcion, Fecha, Importe, DniEmpleado, TipoGasto, CodigoProyecto, cod_tipo_gasto)
SELECT 
    'Gasto de capacitación',
    CURRENT_DATE,
    2500.00,
    e.DNI,
    'Capacitación',
    aep.CodigoProyecto,
    (SELECT cod_tipo_gasto FROM tipo_gasto WHERE descripcion LIKE '%capacitacion%' LIMIT 1)
FROM empleado e
INNER JOIN asignacionempleadoproyecto aep ON e.DNI = aep.DNIEmpleado
WHERE e.AñosExp > 5 
AND aep.RolEmpleado = 'Analista'
AND NOT EXISTS (
    SELECT 1 FROM gastos g 
    WHERE g.DniEmpleado = e.DNI 
    AND g.TipoGasto = 'Capacitación'
);

INSERT INTO productos (Nombre, Descripcion, Estado, ResponsableDNI, Tipo)
SELECT 
    CONCAT('Documentación Fase ', f.NroSecuencia),
    CONCAT('Documentación generada para la fase ', f.Nombre),
    'No finalizado',
    (SELECT DNI 
     FROM empleado e 
     INNER JOIN asignacionempleadoproyecto aep ON e.DNI = aep.DNIEmpleado
     WHERE aep.RolEmpleado = 'Analista'
     AND e.AñosExp > 3
     LIMIT 1),
    'Documentación'
FROM fase f
WHERE f.Estado = 'Finalizada'
AND NOT EXISTS (
    SELECT 1 FROM productos_fases pf 
    WHERE pf.cod_fase = f.NroSecuencia
);

INSERT INTO usorecursos (cod_recurso, cod_fase, CodigoProyecto, PeriodoUso)
SELECT 
    r.Codigo,
    f.NroSecuencia,
    f.CodigoProyecto,
    'Mensual'
FROM fase f
CROSS JOIN (
    SELECT Codigo 
    FROM recursos 
    WHERE Tipo = 'SW' 
    AND NOT EXISTS (
        SELECT 1 FROM usorecursos ur 
        WHERE ur.cod_recurso = recursos.Codigo
    )
    LIMIT 3
) r
WHERE f.Estado = 'En curso'
AND NOT EXISTS (
    SELECT 1 FROM usorecursos ur 
    WHERE ur.cod_fase = f.NroSecuencia
    AND ur.CodigoProyecto = f.CodigoProyecto
);

-- =============================================
-- CONSULTAS DE MODIFICACIÓN
-- =============================================
UPDATE asignacionempleadoproyecto aep
INNER JOIN empleado e ON aep.DNIEmpleado = e.DNI
SET aep.CosteParticipacion = aep.HorasDedicadas * 50
WHERE e.AñosExp > 3;

UPDATE fase f
INNER JOIN productos_fases pf ON f.NroSecuencia = pf.cod_fase
INNER JOIN productos p ON pf.cod_producto = p.Codigo
SET f.Estado = 'Finalizada'
WHERE p.Estado = 'Finalizado';

UPDATE proyecto p
INNER JOIN (
    SELECT 
        CodigoProyecto,
        ROUND(SUM(Importe) * 1.2, 2) as nuevo_presupuesto
    FROM gastos
    GROUP BY CodigoProyecto
) g ON p.Codigo = g.CodigoProyecto
SET p.Presupuesto = g.nuevo_presupuesto
WHERE p.Codigo = g.CodigoProyecto
AND (p.Presupuesto IS NULL OR ABS(COALESCE(p.Presupuesto, 0) - g.nuevo_presupuesto) > 0.01);

-- =============================================
-- CONSULTAS DE BORRADO
-- =============================================
DELETE aep FROM asignacionempleadoproyecto aep
INNER JOIN proyecto p ON aep.CodigoProyecto = p.Codigo
WHERE p.FechaFin IS NOT NULL 
AND p.FechaFin < DATE_SUB(CURRENT_DATE, INTERVAL 6 MONTH)
AND NOT EXISTS (
    SELECT 1 FROM historial_jefe_proyecto hjp
    WHERE hjp.CodigoProyecto = p.Codigo
);

DELETE p FROM productos p
WHERE NOT EXISTS (
    SELECT 1 FROM productos_fases pf 
    WHERE pf.cod_producto = p.Codigo
);

DELETE FROM gastos 
WHERE Importe < (
    SELECT avg_importe 
    FROM (
        SELECT AVG(Importe) as avg_importe 
        FROM gastos
    ) as t
) 
AND Fecha < DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR);

-- =============================================
-- VISTAS
-- =============================================
CREATE OR REPLACE VIEW v_proyectos_activos AS
SELECT 
    p.Codigo,
    p.Nombre,
    COUNT(DISTINCT f.NroSecuencia) as cantidad_fases,
    COALESCE(SUM(g.Importe), 0) as total_gastos,
    COUNT(DISTINCT aep.DNIEmpleado) as cantidad_empleados
FROM proyecto p
LEFT JOIN fase f ON p.Codigo = f.CodigoProyecto
LEFT JOIN gastos g ON p.Codigo = g.CodigoProyecto
LEFT JOIN asignacionempleadoproyecto aep ON p.Codigo = aep.CodigoProyecto
WHERE p.FechaFin IS NULL 
   OR p.FechaFin >= CURRENT_DATE
GROUP BY p.Codigo, p.Nombre;

CREATE OR REPLACE VIEW v_promedio_gastos_empleado AS
SELECT 
    e.DNI,
    e.Nombre,
    p.Codigo as CodigoProyecto,
    p.Nombre as NombreProyecto,
    AVG(g.Importe) as promedio_gastos
FROM empleado e
JOIN gastos g ON e.DNI = g.DniEmpleado
JOIN proyecto p ON g.CodigoProyecto = p.Codigo
GROUP BY e.DNI, e.Nombre, p.Codigo, p.Nombre;

CREATE OR REPLACE VIEW v_jefes_horas AS
SELECT 
    e.DNI,
    e.Nombre,
    SUM(aep.HorasDedicadas) as total_horas
FROM empleado e
INNER JOIN jefe_proyecto jp ON e.DNI = jp.cod_empleado
INNER JOIN asignacionempleadoproyecto aep ON e.DNI = aep.DNIEmpleado
GROUP BY e.DNI, e.Nombre
ORDER BY total_horas DESC;

CREATE OR REPLACE VIEW v_proyectos_tres_productos AS
SELECT 
    p.Codigo,
    p.Nombre,
    COUNT(DISTINCT pr.Codigo) as cantidad_productos
FROM proyecto p
INNER JOIN fase f ON p.Codigo = f.CodigoProyecto
INNER JOIN productos_fases pf ON f.NroSecuencia = pf.cod_fase
INNER JOIN productos pr ON pf.cod_producto = pr.Codigo
GROUP BY p.Codigo, p.Nombre
HAVING COUNT(DISTINCT pr.Codigo) >= 3;

CREATE OR REPLACE VIEW v_analistas_sin_diagramas AS
SELECT DISTINCT
    e.DNI,
    e.Nombre,
    e.AñosExp
FROM empleado e
WHERE e.AñosExp > 5 
AND EXISTS (
    SELECT 1 
    FROM asignacionempleadoproyecto aep 
    WHERE aep.DNIEmpleado = e.DNI 
    AND aep.RolEmpleado = 'Analista'
)
AND NOT EXISTS (
    SELECT 1 
    FROM productos p
    WHERE p.ResponsableDNI = e.DNI 
    AND p.Tipo = 'diagrama'
)
ORDER BY e.AñosExp DESC;

CREATE OR REPLACE VIEW v_empleados_todos_proyectos AS
SELECT 
    e.DNI,
    e.Nombre,
    e.Titulacion,
    COUNT(DISTINCT aep.CodigoProyecto) as cantidad_proyectos,
    ROUND(COUNT(DISTINCT aep.CodigoProyecto) * 100.0 / (SELECT COUNT(*) FROM proyecto), 2) as porcentaje_proyectos
FROM empleado e
JOIN asignacionempleadoproyecto aep ON e.DNI = aep.DNIEmpleado
WHERE e.Titulacion LIKE '%Informatic%' 
   OR e.Titulacion LIKE '%Computaci%'
   OR e.Titulacion LIKE '%Programaci%'
GROUP BY e.DNI, e.Nombre, e.Titulacion
HAVING COUNT(DISTINCT aep.CodigoProyecto) >= 7
ORDER BY cantidad_proyectos DESC, porcentaje_proyectos DESC;

-- =============================================
-- MODIFICACIÓN DEL ESQUEMA - HISTORIAL DE JEFES
-- =============================================
CREATE TABLE historial_jefe_proyecto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    DNIEmpleado VARCHAR(20) NOT NULL,
    CodigoProyecto INT NOT NULL,
    FechaAsignacion DATE DEFAULT (CURRENT_DATE),
    FechaBaja DATE NULL,
    Activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (DNIEmpleado) REFERENCES empleado(DNI),
    FOREIGN KEY (CodigoProyecto) REFERENCES proyecto(Codigo)
);

DELIMITER //
CREATE PROCEDURE cambiar_jefe_proyecto(
    IN p_proyecto_id INT,
    IN p_nuevo_jefe_dni VARCHAR(20),
    IN p_fecha_cambio DATE
)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM jefe_proyecto WHERE cod_empleado = p_nuevo_jefe_dni) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El empleado no es jefe de proyecto';
    END IF;

    START TRANSACTION;
        UPDATE historial_jefe_proyecto 
        SET FechaBaja = p_fecha_cambio,
            Activo = FALSE
        WHERE CodigoProyecto = p_proyecto_id 
        AND Activo = TRUE;

        INSERT INTO historial_jefe_proyecto 
        (DNIEmpleado, CodigoProyecto, FechaAsignacion, Activo)
        VALUES 
        (p_nuevo_jefe_dni, p_proyecto_id, p_fecha_cambio, TRUE);
    COMMIT;
END//
DELIMITER ;

CREATE OR REPLACE VIEW v_jefes_actuales AS
SELECT 
    p.Codigo as CodigoProyecto,
    p.Nombre as NombreProyecto,
    e.DNI as DNIJefe,
    e.Nombre as NombreJefe,
    hjp.FechaAsignacion
FROM proyecto p
LEFT JOIN historial_jefe_proyecto hjp ON p.Codigo = hjp.CodigoProyecto AND hjp.Activo = TRUE
LEFT JOIN empleado e ON hjp.DNIEmpleado = e.DNI;