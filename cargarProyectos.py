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

# Insertar datos en la tabla 'proyecto'
def insertar_proyectos(conexion, cursor, cantidad):
    proyectos = []
    for _ in range(cantidad):
        nombre = f"Proyecto {faker.word().capitalize()}"
        cliente = faker.company()
        descripcion = faker.text(max_nb_chars=200)
        presupuesto = round(faker.pydecimal(left_digits=6, right_digits=2, positive=True), 2)
        nro_horas = faker.random_int(min=500, max=5000)
        fecha_inicio = faker.date_this_year()
        fecha_fin = faker.date_between(start_date=fecha_inicio, end_date='+2y')
        
        proyectos.append((nombre, cliente, descripcion, presupuesto, nro_horas, fecha_inicio, fecha_fin))

    query = """
    INSERT INTO proyecto (Nombre, Cliente, Descripcion, Presupuesto, NroHorasEstimadas, FechaInicio, FechaFin)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(query, proyectos)
    conexion.commit()
    print(f"Se insertaron {cantidad} proyectos.")

# Insertar datos en la tabla 'fase'
def insertar_fases(conexion, cursor, cantidad):
    fases = []
    cursor.execute("SELECT Codigo FROM proyecto;")
    codigos_proyecto = [row[0] for row in cursor.fetchall()]

    # Usar un conjunto para asegurar que los números de secuencia sean únicos
    secuencias_usadas = set()

    for _ in range(cantidad):
        # Generar un número de secuencia único
        nro_secuencia = random.randint(1, 50)
        while nro_secuencia in secuencias_usadas:
            nro_secuencia = random.randint(1, 50)
        secuencias_usadas.add(nro_secuencia)

        codigo_proyecto = random.choice(codigos_proyecto)
        nombre = faker.word()
        fecha_comienzo = faker.date_this_year()
        fecha_finalizacion = faker.date_between(start_date=fecha_comienzo, end_date='+3m')
        estado = random.choice(['En curso', 'Finalizada'])
        fases.append((nro_secuencia, codigo_proyecto, nombre, fecha_comienzo, fecha_finalizacion, estado))

    query = """
    INSERT INTO fase (NroSecuencia, CodigoProyecto, Nombre, FechaComienzo, FechaFinalizacion, Estado)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(query, fases)
    conexion.commit()
    print(f"Se han insertado {cantidad} fases.")

# Insertar datos en la tabla 'empleado'
def insertar_empleados(conexion, cursor, cantidad):
    empleados = []
    for _ in range(cantidad):
        dni = faker.unique.ssn()
        nombre = faker.name()
        direccion = faker.address()
        titulacion = faker.job()
        anos_exp = faker.random_int(min=1, max=30)
        
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
    insertar_proyectos(conn, cursor, 50)  # Insertar 50 proyectos
    insertar_fases(conn, cursor, 300)      # Insertar 300 fases
    insertar_empleados(conn, cursor, 100)   # Insertar 100 empleados

if __name__ == "__main__":
    main()

# Cerrar conexión
cursor.close()
conn.close()
