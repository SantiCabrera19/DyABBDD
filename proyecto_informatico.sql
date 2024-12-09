-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS proyecto_informatico;
USE proyecto_informatico;

-- Tabla asignacionempleadoproyecto
CREATE TABLE asignacionempleadoproyecto (
    CodigoProyecto INT,
    CosteParticipacion DECIMAL(10, 2),
    DNIEmpleado VARCHAR(20),
    HorasDedicadas INT,
    RolEmpleado ENUM('Analista', 'Programador'),
    PRIMARY KEY (CodigoProyecto, DNIEmpleado)
);

-- Tabla desarrolloproducto
CREATE TABLE desarrolloproducto (
    CodigoProducto INT,
    HorasDedicadas INT,
    NroSecuenciaFase INT,
    PRIMARY KEY (CodigoProducto, NroSecuenciaFase)
);

-- Tabla empleado
CREATE TABLE empleado (
    DNI VARCHAR(20) PRIMARY KEY,
    Nombre VARCHAR(100),
    Direccion VARCHAR(200),
    Titulacion VARCHAR(100),
    AñosExp INT
);

-- Tabla empleados_productos
CREATE TABLE empleados_productos (
    cod_empleado VARCHAR(20),
    cod_producto INT,
    PRIMARY KEY (cod_empleado, cod_producto)
);

-- Tabla fase
CREATE TABLE fase (
    CodigoProyecto INT,
    NroSecuencia INT AUTO_INCREMENT,
    Nombre VARCHAR(100),
    FechaComienzo DATE,
    FechaFinalizacion DATE,
    Estado ENUM('En curso', 'Finalizada'),
    PRIMARY KEY (CodigoProyecto, NroSecuencia)
);

-- Tabla gastos
CREATE TABLE gastos (
    Codigo INT AUTO_INCREMENT PRIMARY KEY,
    cod_tipo_gasto INT,
    CodigoProyecto INT,
    Descripcion TEXT,
    DniEmpleado VARCHAR(20),
    Fecha DATE,
    Importe DECIMAL(10, 2),
    TipoGasto VARCHAR(100)
);

-- Tabla gastos_altos
CREATE TABLE gastos_altos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_proyecto INT,
    dni_empleado VARCHAR(20),
    fecha DATE,
    fecha_registro TIMESTAMP,
    monto DECIMAL(10, 2)
);

-- Tabla historial_jefe_proyecto
CREATE TABLE historial_jefe_proyecto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    CodigoProyecto INT,
    DNIEmpleado VARCHAR(20),
    FechaAsignacion DATE,
    FechaBaja DATE,
    Activo TINYINT(1)
);

-- Tabla jefe_proyecto
CREATE TABLE jefe_proyecto (
    cod_empleado VARCHAR(20) PRIMARY KEY
);

-- Tabla lenguajes_programador
CREATE TABLE lenguajes_programador (
    DNIEmpleado VARCHAR(20),
    Lenguaje VARCHAR(100),
    PRIMARY KEY (DNIEmpleado, Lenguaje)
);

-- Tabla productos
CREATE TABLE productos (
    Codigo INT AUTO_INCREMENT PRIMARY KEY,
    Descripcion TEXT,
    Estado ENUM('En desarrollo', 'Finalizado'),
    Nombre VARCHAR(100),
    ResponsableDNI VARCHAR(20),
    Tipo VARCHAR(50),
    VersionUbicacion VARCHAR(100)
);

-- Tabla productos_fases
CREATE TABLE productos_fases (
    cod_producto INT,
    cod_fase INT,
    PRIMARY KEY (cod_producto, cod_fase)
);

-- Tabla proyecto
CREATE TABLE proyecto (
    Codigo INT AUTO_INCREMENT PRIMARY KEY,
    Cliente VARCHAR(100),
    Descripcion TEXT,
    FechaFin DATE,
    FechaInicio DATE,
    Nombre VARCHAR(100),
    NroHorasEstimadas INT,
    Presupuesto DECIMAL(15, 2)
);

-- Tabla proyectosrelacionados
CREATE TABLE proyectosrelacionados (
    IDRelacion INT AUTO_INCREMENT PRIMARY KEY,
    CodigoProyectoMain INT,
    CodigoProyectoRelacionado INT,
    PalabrasClaves VARCHAR(255)
);

-- Tabla recursos
CREATE TABLE recursos (
    Codigo INT AUTO_INCREMENT PRIMARY KEY,
    Descripcion TEXT,
    Nombre VARCHAR(100),
    PeriodoUso VARCHAR(50),
    Tipo ENUM('HW', 'SW')
);

-- Tabla tipo_gasto
CREATE TABLE tipo_gasto (
    cod_tipo_gasto INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(255)
);

-- Tabla usorecursos
CREATE TABLE usorecursos (
    cod_fase INT,
    cod_recurso INT,
    CodigoProyecto INT,
    PeriodoUso VARCHAR(100),
    PRIMARY KEY (cod_fase, cod_recurso, CodigoProyecto)
);

-- Vistas (sugerencia de definición; pueden ser adaptadas)
-- Vista v_analistas_sin_diagramas
CREATE VIEW v_analistas_sin_diagramas AS
SELECT DNI, Nombre, AñosExp
FROM empleado;

-- Vista v_empleados_todos_proyectos
CREATE VIEW v_empleados_todos_proyectos AS
SELECT DNI, Nombre, Titulacion, COUNT(*) AS cantidad_proyectos
FROM asignacionempleadoproyecto
GROUP BY DNI;

-- Vista v_jefes_actuales
CREATE VIEW v_jefes_actuales AS
SELECT CodigoProyecto, DNIEmpleado AS DNIJefe, FechaAsignacion, Nombre AS NombreJefe, Nombre AS NombreProyecto
FROM historial_jefe_proyecto
WHERE Activo = 1;

-- Vista v_promedio_gastos_empleado
CREATE VIEW v_promedio_gastos_empleado AS
SELECT CodigoProyecto, DNI, Nombre, AVG(Importe) AS promedio_gastos
FROM gastos
GROUP BY CodigoProyecto, DNI;

-- Vista v_proyectos_activos
CREATE VIEW v_proyectos_activos AS
SELECT Codigo, Nombre, COUNT(DNIEmpleado) AS cantidad_empleados, SUM(Importe) AS total_gastos
FROM proyecto
JOIN gastos ON proyecto.Codigo = gastos.CodigoProyecto
GROUP BY Codigo;
