import customtkinter as ctk
from db import conectar
from dashboard import abrir_dashboard

# Función para verificar las credenciales del administrador
def verificar_admin(correo, contraseña):
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM administradores WHERE correo = %s", (correo,))
    admin = cursor.fetchone()
    db.close()

    # Comparar la contraseña directamente sin usar bcrypt
    if admin and admin['contrasena_hash'] == contraseña:
        return admin
    return None

# Función para el login
def login():
    app = ctk.CTk()
    app.title("Login Administrador")
    app.geometry("400x300")

    correo_var = ctk.StringVar()
    contra_var = ctk.StringVar()

    ctk.CTkLabel(app, text="Correo electrónico").pack(pady=10)
    correo_entry = ctk.CTkEntry(app, textvariable=correo_var)
    correo_entry.pack()

    ctk.CTkLabel(app, text="Contraseña").pack(pady=10)
    contra_entry = ctk.CTkEntry(app, textvariable=contra_var, show="*")
    contra_entry.pack()

    def on_login():
        correo = correo_var.get()
        contra = contra_var.get()
        admin = verificar_admin(correo, contra)
        if admin:
            app.destroy()
            abrir_dashboard(admin)
        else:
            ctk.CTkLabel(app, text="Credenciales incorrectas", text_color="red").pack()

    ctk.CTkButton(app, text="Iniciar sesión", command=on_login).pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    login()
