import pymysql
from faker import Faker
import random
from datetime import datetime, timedelta

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

def obtener_asignaciones():
    """Obtener las asignaciones existentes de empleados a proyectos"""
    cursor.execute("""
        SELECT DISTINCT DNIEmpleado, CodigoProyecto 
        FROM asignacionempleadoproyecto
    """)
    return cursor.fetchall()

def insertar_tipos_gasto():
    """Insertar tipos de gasto básicos"""
    tipos_gasto = [
        (1, 'Dietas'),
        (2, 'Viajes'),
        (3, 'Alojamiento'),
        (4, 'Transporte local'),
        (5, 'Material de oficina'),
        (6, 'Equipamiento'),
        (7, 'Formación'),
        (8, 'Otros gastos')
    ]
    
    query = """
    INSERT INTO tipo_gasto (cod_tipo_gasto, descripcion)
    VALUES (%s, %s)
    """
    
    try:
        cursor.executemany(query, tipos_gasto)
        conn.commit()
        print(f"Se han insertado {len(tipos_gasto)} tipos de gasto.")
    except pymysql.Error as e:
        if e.args[0] != 1062:  # Ignorar error de duplicado
            print(f"Error al insertar tipos de gasto: {e}")
        conn.rollback()

def generar_gastos():
    asignaciones = obtener_asignaciones()
    gastos = []
    
    for dni_empleado, codigo_proyecto in asignaciones:
        # Generar entre 0 y 5 gastos por asignación
        num_gastos = random.randint(0, 5)
        
        for _ in range(num_gastos):
            descripcion = faker.sentence()
            # Fecha dentro del último año
            fecha = faker.date_between(start_date='-1y', end_date='today')
            # Importe entre 50 y 1000 euros
            importe = round(random.uniform(50, 1000), 2)
            # Tipo de gasto aleatorio
            tipo_gasto = random.randint(1, 8)
            
            gastos.append((
                descripcion,
                fecha,
                importe,
                dni_empleado,
                tipo_gasto,
                codigo_proyecto
            ))
    
    query = """
    INSERT INTO gastos 
    (Descripcion, Fecha, Importe, DniEmpleado, cod_tipo_gasto, CodigoProyecto)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(query, gastos)
        conn.commit()
        print(f"Se han insertado {len(gastos)} gastos.")
    except pymysql.Error as e:
        print(f"Error al insertar gastos: {e}")
        conn.rollback()

def main():
    print("Iniciando carga de gastos...")
    insertar_tipos_gasto()
    generar_gastos()
    print("Proceso completado.")

if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
