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

def obtener_analistas():
    cursor.execute("""
        SELECT DISTINCT e.DNI, e.Nombre 
        FROM empleado e 
        JOIN asignacionempleadoproyecto a ON e.DNI = a.DNIEmpleado 
        WHERE a.RolEmpleado = 'Analista'
    """)
    return cursor.fetchall()

def obtener_programadores():
    cursor.execute("""
        SELECT DISTINCT e.DNI, e.Nombre 
        FROM empleado e 
        JOIN asignacionempleadoproyecto a ON e.DNI = a.DNIEmpleado 
        WHERE a.RolEmpleado = 'Programador'
    """)
    return cursor.fetchall()

def asignar_jefes_proyecto():
    # Obtener analistas experimentados para ser jefes
    analistas = obtener_analistas()
    if not analistas:
        print("No hay analistas disponibles para asignar como jefes")
        return
    
    # Seleccionar 10% de analistas como jefes
    num_jefes = max(1, len(analistas) // 10)
    jefes_seleccionados = random.sample(analistas, num_jefes)
    
    # Obtener proyectos
    cursor.execute("SELECT Codigo FROM proyecto")
    proyectos = cursor.fetchall()
    
    # Asignar jefes a proyectos
    for jefe in jefes_seleccionados:
        try:
            cursor.execute("""
                INSERT INTO jefe_proyecto (cod_empleado) 
                VALUES (%s)
            """, (jefe[0],))
            conn.commit()
            print(f"Jefe de proyecto asignado: {jefe[1]}")
        except pymysql.Error as e:
            print(f"Error al asignar jefe {jefe[1]}: {e}")
            conn.rollback()

def agregar_lenguajes_programadores():
    programadores = obtener_programadores()
    lenguajes = ['Java', 'Python', 'C++', 'JavaScript', 'PHP', 'C#', 'Ruby', 'SQL', 'Go']
    
    for programador in programadores:
        # Asignar 2-4 lenguajes aleatorios a cada programador
        lenguajes_programador = random.sample(lenguajes, random.randint(2, 4))
        for lenguaje in lenguajes_programador:
            try:
                # Aquí deberías tener una tabla para almacenar los lenguajes de los programadores
                cursor.execute("""
                    INSERT INTO lenguajes_programador (DNIEmpleado, Lenguaje)
                    VALUES (%s, %s)
                """, (programador[0], lenguaje))
                conn.commit()
            except pymysql.Error as e:
                print(f"Error al asignar lenguaje {lenguaje} a {programador[1]}: {e}")
                conn.rollback()

def actualizar_costes_participacion():
    # Actualizar costes para todos los empleados en sus proyectos
    cursor.execute("""
        SELECT DNIEmpleado, CodigoProyecto, HorasDedicadas 
        FROM asignacionempleadoproyecto
    """)
    asignaciones = cursor.fetchall()
    
    for asignacion in asignaciones:
        # Calcular coste basado en horas y un coste por hora aleatorio
        coste_hora = random.uniform(30.0, 100.0)  # Entre 30 y 100 euros por hora
        coste_total = round(coste_hora * asignacion[2], 2)
        
        try:
            cursor.execute("""
                UPDATE asignacionempleadoproyecto 
                SET CosteParticipacion = %s 
                WHERE DNIEmpleado = %s AND CodigoProyecto = %s
            """, (coste_total, asignacion[0], asignacion[1]))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al actualizar coste para empleado {asignacion[0]}: {e}")
            conn.rollback()

def main():
    print("Iniciando actualización de jefes y lenguajes...")
    asignar_jefes_proyecto()
    agregar_lenguajes_programadores()
    actualizar_costes_participacion()
    print("Proceso completado.")

if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
