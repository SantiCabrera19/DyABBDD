import pymysql
from faker import Faker
import random
from datetime import timedelta

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

def insertar_recursos():
    recursos_hw = [
        'Servidor Dell PowerEdge',
        'Laptop HP ProBook',
        'Impresora Láser',
        'Scanner Industrial',
        'Router Cisco',
        'Workstation HP',
        'NAS Storage',
        'UPS System'
    ]
    
    recursos_sw = [
        'Visual Studio',
        'IntelliJ IDEA',
        'Oracle Database',
        'Windows Server',
        'Adobe Creative Suite',
        'AutoCAD',
        'VMware',
        'Microsoft Office'
    ]
    
    recursos = []
    
    # Generar recursos HW
    for recurso in recursos_hw:
        nombre = f"{recurso} {faker.random_int(1000, 9999)}"
        descripcion = faker.text(max_nb_chars=200)
        tipo = 'HW'
        recursos.append((nombre, descripcion, tipo))
    
    # Generar recursos SW
    for recurso in recursos_sw:
        nombre = f"{recurso} v{faker.random_int(2020, 2024)}"
        descripcion = faker.text(max_nb_chars=200)
        tipo = 'SW'
        recursos.append((nombre, descripcion, tipo))
    
    query = """
    INSERT INTO recursos (Nombre, Descripcion, Tipo)
    VALUES (%s, %s, %s)
    """
    
    try:
        cursor.executemany(query, recursos)
        conn.commit()
        print(f"Se han insertado {len(recursos)} recursos.")
    except pymysql.Error as e:
        print(f"Error al insertar recursos: {e}")
        conn.rollback()

def asignar_recursos_fases():
    # Obtener todos los recursos y fases
    cursor.execute("SELECT Codigo FROM recursos")
    recursos = cursor.fetchall()
    
    cursor.execute("SELECT NroSecuencia, CodigoProyecto FROM fase")
    fases = cursor.fetchall()
    
    asignaciones = []
    for fase in fases:
        # Asignar 2-4 recursos aleatorios a cada fase
        recursos_fase = random.sample(recursos, random.randint(2, 4))
        for recurso in recursos_fase:
            # Generar periodo de uso (ej: "2 meses", "3 semanas")
            duracion = random.randint(1, 6)
            unidad = random.choice(['días', 'semanas', 'meses'])
            periodo_uso = f"{duracion} {unidad}"
            
            asignaciones.append((
                recurso[0],     # cod_recurso
                fase[0],        # cod_fase
                fase[1],        # CodigoProyecto
                periodo_uso
            ))
    
    query = """
    INSERT INTO usorecursos (cod_recurso, cod_fase, CodigoProyecto, PeriodoUso)
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(query, asignaciones)
        conn.commit()
        print(f"Se han creado {len(asignaciones)} asignaciones de recursos a fases.")
    except pymysql.Error as e:
        print(f"Error al asignar recursos a fases: {e}")
        conn.rollback()

def main():
    print("Iniciando carga de recursos...")
    insertar_recursos()
    asignar_recursos_fases()
    print("Proceso completado.")

if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
