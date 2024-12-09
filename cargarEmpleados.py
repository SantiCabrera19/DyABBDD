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

# Insertar datos en la tabla 'empleado'
def insertar_empleados(conexion, cursor, cantidad):
    empleados = []
    # Lista de titulaciones más realistas para el sector IT
    titulaciones = [
        "Ingeniero en Informática",
        "Ingeniero de Software",
        "Ingeniero en Sistemas",
        "Técnico en Programación",
        "Ingeniero en Computación"
    ]
    
    for _ in range(cantidad):
        dni = faker.unique.ssn()
        nombre = faker.name()
        direccion = faker.address()
        titulacion = random.choice(titulaciones)
        anos_exp = faker.random_int(min=1, max=20)
        
        empleados.append((dni, nombre, direccion, titulacion, anos_exp))

    query = """
    INSERT INTO empleado (DNI, Nombre, Direccion, Titulacion, AñosExp)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(query, empleados)
    conexion.commit()
    print(f"Se insertaron {cantidad} empleados.")

# Función principal
def main():
    insertar_empleados(conn, cursor, 100)  # 100 empleados

if __name__ == "__main__":
    main()

# Cerrar conexión
cursor.close()
conn.close()
