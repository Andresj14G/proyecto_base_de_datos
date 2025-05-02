import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion = mysql.connector.connect(
            host='bi9apiftweniqomxwrnk-mysql.services.clever-cloud.com',     # Cambia si tu base de datos no es local
            user='udulqfxzco36vg1c',           # Tu usuario de MySQL
            password='eCSHruiHD8WkcvTTkmJi',           # Tu contraseña de MySQL
            database='bi9apiftweniqomxwrnk',  # Reemplaza con el nombre real de tu base
            port=3306
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return None
