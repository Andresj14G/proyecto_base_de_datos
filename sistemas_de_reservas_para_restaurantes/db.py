import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion = mysql.connector.connect(
            host='bkm7vcjidmn7qfn6ftdp-mysql.services.clever-cloud.com',     # Cambia si tu base de datos no es local
            user='upxkzqnv6msyanp2',           # Tu usuario de MySQL
            password='gMrGGEvah2CkmlJx1csu',           # Tu contraseña de MySQL
            database='bkm7vcjidmn7qfn6ftdp',  # Reemplaza con el nombre real de tu base
            port=3306
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return None
