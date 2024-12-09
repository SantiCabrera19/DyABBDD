import pymysql
from faker import Faker
import random

# Configuración de conexión a la base de datos
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='42331',
    database='proyectos_informaticos'
)
cursor = conn.cursor()

# Inicializamos Faker
faker = Faker()

def obtener_empleados():
    cursor.execute("SELECT DNI FROM empleado")
    return [row[0] for row in cursor.fetchall()]

def obtener_proyectos():
    cursor.execute("SELECT Codigo FROM proyecto")
    return [row[0] for row in cursor.fetchall()]

def insertar_asignaciones(conexion, cursor):
    empleados = obtener_empleados()
    proyectos = obtener_proyectos()
    
    # Dividir empleados en roles
    num_jefes = len(empleados) // 10
    num_analistas = len(empleados) * 4 // 10
    
    jefes = empleados[:num_jefes]
    analistas = empleados[num_jefes:num_jefes + num_analistas]
    programadores = empleados[num_jefes + num_analistas:]
    
    # Conjunto para trackear asignaciones únicas
    asignaciones_unicas = set()
    asignaciones = []
    
    # Asignar jefes de proyecto (un jefe por proyecto)
    for proyecto in proyectos:
        jefe = random.choice(jefes)
        if (proyecto, jefe) not in asignaciones_unicas:
            horas = random.randint(100, 500)
            asignaciones.append((proyecto, jefe, horas, 'Analista'))
            asignaciones_unicas.add((proyecto, jefe))
    
    # Asignar analistas
    for proyecto in proyectos:
        analistas_disponibles = [a for a in analistas if (proyecto, a) not in asignaciones_unicas]
        for _ in range(min(random.randint(2, 3), len(analistas_disponibles))):
            analista = random.choice(analistas_disponibles)
            analistas_disponibles.remove(analista)
            horas = random.randint(200, 800)
            asignaciones.append((proyecto, analista, horas, 'Analista'))
            asignaciones_unicas.add((proyecto, analista))
    
    # Asignar programadores
    for proyecto in proyectos:
        programadores_disponibles = [p for p in programadores if (proyecto, p) not in asignaciones_unicas]
        for _ in range(min(random.randint(3, 5), len(programadores_disponibles))):
            programador = random.choice(programadores_disponibles)
            programadores_disponibles.remove(programador)
            horas = random.randint(300, 1000)
            asignaciones.append((proyecto, programador, horas, 'Programador'))
            asignaciones_unicas.add((proyecto, programador))

    # Insertar asignaciones
    query = """
    INSERT INTO asignacionempleadoproyecto 
    (CodigoProyecto, DNIEmpleado, HorasDedicadas, RolEmpleado)
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(query, asignaciones)
        conexion.commit()
        print(f"Se han insertado {len(asignaciones)} asignaciones de empleados a proyectos.")
    except pymysql.Error as e:
        print(f"Error al insertar asignaciones: {e}")
        conexion.rollback()

def main():
    insertar_asignaciones(conn, cursor)

if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
