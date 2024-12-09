use proyectos_informaticos;

-- =============================================
-- TRIGGERS
-- =============================================

-- 1. Trigger para registrar gastos altos
DROP TRIGGER IF EXISTS tr_registrar_gastos_altos;
DROP TABLE IF EXISTS gastos_altos;

CREATE TABLE gastos_altos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni_empleado VARCHAR(20),
    codigo_proyecto INT,
    fecha DATE,
    monto DECIMAL(15,2),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dni_empleado) REFERENCES empleado(DNI),
    FOREIGN KEY (codigo_proyecto) REFERENCES proyecto(Codigo)
);

DELIMITER //
CREATE TRIGGER tr_registrar_gastos_altos
AFTER INSERT ON gastos
FOR EACH ROW
BEGIN
    IF NEW.Importe > 100000 THEN
        INSERT INTO gastos_altos (dni_empleado, codigo_proyecto, fecha, monto)
        VALUES (
            NEW.DniEmpleado,
            NEW.CodigoProyecto,
            NEW.Fecha,
            NEW.Importe
        );
    END IF;
END//
DELIMITER ;

-- 2. Trigger para verificar experiencia de analistas
DELIMITER //
CREATE TRIGGER tr_verificar_experiencia_analista
BEFORE UPDATE ON productos
FOR EACH ROW
BEGIN
    DECLARE años_exp INT;
    
    -- Obtener años de experiencia del nuevo responsable
    SELECT AñosExp INTO años_exp
    FROM empleado e
    WHERE e.DNI = NEW.ResponsableDNI;
    
    -- Verificar si tiene menos de 2 años de experiencia
    IF años_exp < 2 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'El analista debe tener al menos 2 años de experiencia';
    END IF;
END//
DELIMITER ;

-- =============================================
-- RUTINAS ALMACENADAS
-- =============================================

-- 1. Procedimiento para carga masiva de empleados por rol
DELIMITER //
CREATE PROCEDURE sp_cargar_empleados_por_rol(
    IN p_dni VARCHAR(20),
    IN p_nombre VARCHAR(100),
    IN p_direccion VARCHAR(200),
    IN p_titulacion VARCHAR(50),
    IN p_años_exp INT,
    IN p_rol VARCHAR(20),
    IN p_codigo_proyecto INT
)
BEGIN
    -- Insertar empleado
    INSERT INTO empleado (DNI, Nombre, Direccion, Titulacion, AñosExp)
    VALUES (p_dni, p_nombre, p_direccion, p_titulacion, p_años_exp);
    
    -- Asignar a proyecto con rol específico
    INSERT INTO asignacionempleadoproyecto 
    (DNIEmpleado, CodigoProyecto, RolEmpleado)
    VALUES (p_dni, p_codigo_proyecto, p_rol);
    
    -- Si es jefe, agregarlo a la tabla de jefes
    IF p_rol = 'Jefe' THEN
        INSERT INTO jefe_proyecto (cod_empleado) 
        VALUES (p_dni);
    END IF;
END//
DELIMITER ;

-- 2. Función para contar recursos de un proyecto
DELIMITER //
CREATE FUNCTION fn_contar_recursos_proyecto(p_codigo_proyecto INT) 
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_recursos INT;
    
    SELECT COUNT(DISTINCT ur.cod_recurso)
    INTO total_recursos
    FROM usorecursos ur
    WHERE ur.CodigoProyecto = p_codigo_proyecto;
    
    RETURN COALESCE(total_recursos, 0);
END//
DELIMITER ;

-- =============================================
-- EJEMPLOS DE USO
-- =============================================

/*
-- Probar trigger de gastos altos
INSERT INTO gastos (Descripcion, Fecha, Importe, DniEmpleado, CodigoProyecto) 
VALUES ('Gasto de prueba', CURRENT_DATE, 150000, 
    (SELECT DNI FROM empleado LIMIT 1), 
    (SELECT Codigo FROM proyecto LIMIT 1));

-- Probar trigger de experiencia analista
SET @dni_empleado_junior = (SELECT DNI FROM empleado WHERE AñosExp < 2 LIMIT 1);
UPDATE productos 
SET ResponsableDNI = @dni_empleado_junior
WHERE Codigo = (SELECT MIN(Codigo) FROM (SELECT Codigo FROM productos) AS p);

-- Probar procedimiento de carga de empleados
CALL sp_cargar_empleados_por_rol(
    '11111111A', 
    'Juan Pérez', 
    'Calle 123', 
    'Ingeniero en Sistemas',
    5,
    'Analista',
    1
);

-- Probar función de conteo de recursos
SELECT fn_contar_recursos_proyecto(1) as total_recursos;
*/