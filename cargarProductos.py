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
        SELECT DISTINCT e.DNI 
        FROM empleado e 
        JOIN asignacionempleadoproyecto a ON e.DNI = a.DNIEmpleado 
        WHERE a.RolEmpleado = 'Analista'
    """)
    return [row[0] for row in cursor.fetchall()]

def obtener_fases():
    cursor.execute("SELECT NroSecuencia, CodigoProyecto FROM fase")
    return [(row[0], row[1]) for row in cursor.fetchall()]

def insertar_productos(conexion, cursor):
    analistas = obtener_analistas()
    fases = obtener_fases()
    
    tipos_software = ['Diagrama UML', 'Programa Java', 'Script Python', 'API REST', 'Base de datos']
    productos = []
    
    for fase_id, proyecto_id in fases:
        # Generar 1-3 productos por fase
        for _ in range(random.randint(1, 3)):
            tipo_producto = random.choice(['Software', 'Informe', 'Prototipo'])
            nombre = f"{tipo_producto} - {faker.word().capitalize()}"
            descripcion = faker.sentence()
            estado = random.choice(['Finalizado', 'No finalizado'])
            responsable = random.choice(analistas)
            
            if tipo_producto == 'Software':
                version_ubicacion = random.choice(tipos_software)
                productos.append((
                    nombre, descripcion, estado, responsable,
                    'Software', version_ubicacion
                ))
            elif tipo_producto == 'Prototipo':
                version_ubicacion = f"v{random.randint(1,5)}.{random.randint(0,9)} - /prototipos/proyecto_{proyecto_id}"
                productos.append((
                    nombre, descripcion, estado, responsable,
                    'Prototipo', version_ubicacion
                ))
            else:
                productos.append((
                    nombre, descripcion, estado, responsable,
                    'Informe', None
                ))

    # Insertar productos
    query = """
    INSERT INTO productos 
    (Nombre, Descripcion, Estado, ResponsableDNI, Tipo, VersionUbicacion)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(query, productos)
        conexion.commit()
        print(f"Se han insertado {len(productos)} productos.")
        
        # Asociar productos con fases
        asociar_productos_fases(conexion, cursor, productos, fases)
    except pymysql.Error as e:
        print(f"Error al insertar productos: {e}")
        conexion.rollback()

def asociar_productos_fases(conexion, cursor, productos, fases):
    asociaciones = []
    
    # Obtener los códigos de los productos insertados
    cursor.execute("SELECT Codigo, Nombre FROM productos")
    productos_dict = {row[1]: row[0] for row in cursor.fetchall()}
    
    for producto in productos:
        nombre_producto = producto[0]
        codigo_producto = productos_dict.get(nombre_producto)
        if codigo_producto:
            # Asociar cada producto a 1-3 fases aleatorias
            fases_producto = random.sample(fases, random.randint(1, min(3, len(fases))))
            for fase_id, proyecto_id in fases_producto:
                asociaciones.append((codigo_producto, fase_id))

    query = """
    INSERT INTO productos_fases 
    (cod_producto, cod_fase)
    VALUES (%s, %s)
    """
    
    try:
        cursor.executemany(query, asociaciones)
        conexion.commit()
        print(f"Se han creado {len(asociaciones)} asociaciones entre productos y fases.")
    except pymysql.Error as e:
        print(f"Error al crear asociaciones: {e}")
        conexion.rollback()

def main():
    insertar_productos(conn, cursor)

if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()