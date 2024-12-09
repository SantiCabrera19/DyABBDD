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

# Insertar datos en la tabla 'fase'
def insertar_fases(conexion, cursor, cantidad_por_proyecto):
    fases = []
    cursor.execute("SELECT Codigo FROM proyecto;")
    codigos_proyecto = [row[0] for row in cursor.fetchall()]
    
    nombres_fases = ["Análisis", "Diseño", "Desarrollo", "Pruebas", "Implementación"]
    secuencia_global = 1  # Contador global para NroSecuencia

    for codigo_proyecto in codigos_proyecto:
        for nro_secuencia in range(1, cantidad_por_proyecto + 1):
            nombre = nombres_fases[nro_secuencia - 1] if nro_secuencia <= len(nombres_fases) else faker.word()
            fecha_comienzo = faker.date_this_year()
            fecha_finalizacion = faker.date_between(start_date=fecha_comienzo, end_date='+6m')
            estado = random.choice(['En curso', 'Finalizada'])
            fases.append((secuencia_global, codigo_proyecto, nombre, fecha_comienzo, fecha_finalizacion, estado))
            secuencia_global += 1

    query = """
    INSERT INTO fase (NroSecuencia, CodigoProyecto, Nombre, FechaComienzo, FechaFinalizacion, Estado)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(query, fases)
    conexion.commit()
    print(f"Se han insertado {len(fases)} fases.")

# Función principal
def main():
    insertar_fases(conn, cursor, 4)  # 4 fases por proyecto

if __name__ == "__main__":
    main()

# Cerrar conexión
cursor.close()
conn.close()
