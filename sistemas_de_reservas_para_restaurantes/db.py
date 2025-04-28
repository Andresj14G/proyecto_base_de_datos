import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion = mysql.connector.connect(
            host='localhost',     # Cambia si tu base de datos no es local
            user='root',           # Tu usuario de MySQL
            password='',           # Tu contraseña de MySQL
            database='reservas_app',  # Reemplaza con el nombre real de tu base
            port=3307 
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return None
