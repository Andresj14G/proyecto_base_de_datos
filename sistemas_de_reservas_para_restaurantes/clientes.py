import customtkinter as ctk
from db import conectar
from tkinter import messagebox

def abrir_clientes():
    clientes = ctk.CTk()
    clientes.title("Gestión de Clientes")
    clientes.geometry("500x400")
    clientes.resizable(False, False)

    def registrar_cliente():
        nombre = entry_nombre.get()
        correo = entry_correo.get()
        telefono = entry_telefono.get()

        if not nombre or not correo:
            messagebox.showerror("Error", "El nombre y correo son obligatorios")
            return

        db = conectar()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO clientes (nombre_completo, correo_electronico, telefono) VALUES (%s, %s, %s)", (nombre, correo, telefono))
            db.commit()
            messagebox.showinfo("Éxito", "Cliente registrado correctamente")
            entry_nombre.delete(0, ctk.END)
            entry_correo.delete(0, ctk.END)
            entry_telefono.delete(0, ctk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente: {e}")
        finally:
            db.close()

    # Título
    ctk.CTkLabel(clientes, text="Registro de Clientes", font=("Arial", 16, "bold")).pack(pady=20)

    # Campos
    ctk.CTkLabel(clientes, text="Nombre completo:").pack(pady=5)
    entry_nombre = ctk.CTkEntry(clientes)
    entry_nombre.pack(pady=5)

    ctk.CTkLabel(clientes, text="Correo electrónico:").pack(pady=5)
    entry_correo = ctk.CTkEntry(clientes)
    entry_correo.pack(pady=5)

    ctk.CTkLabel(clientes, text="Teléfono (opcional):").pack(pady=5)
    entry_telefono = ctk.CTkEntry(clientes)
    entry_telefono.pack(pady=5)

    # Botón de Registro
    ctk.CTkButton(clientes, text="Registrar Cliente", command=registrar_cliente).pack(pady=20)

    clientes.mainloop()
