import customtkinter as ctk
from clientes import abrir_clientes

def abrir_dashboard(admin):
    app = ctk.CTk()
    app.title("Panel de Administración - Restaurante")
    app.geometry("500x400")
    app.resizable(False, False)

    ctk.CTkLabel(app, text="Sistema de Reservas", font=("Arial", 24, "bold")).pack(pady=20)

    # Mostrar el nombre del administrador en la parte superior
    ctk.CTkLabel(app, text=f"Bienvenido, {admin['nombre']}", font=("Arial", 14)).pack(pady=10)

    # Botón para gestionar clientes
    btn_clientes = ctk.CTkButton(
        app, text="Gestionar Clientes", width=300, height=50,
        command=abrir_clientes
    )
    btn_clientes.pack(pady=10)

    # Botón para gestionar reservas (luego lo creamos)
    btn_reservas = ctk.CTkButton(
        app, text="Gestionar Reservas", width=300, height=50,
        command=lambda: print("Abrir módulo de reservas")  # temporal
    )
    btn_reservas.pack(pady=10)

    # Botón para salir
    btn_salir = ctk.CTkButton(
        app, text="Cerrar Sesión", width=300, height=50,
        fg_color="red", hover_color="#cc0000",
        command=app.destroy
    )
    btn_salir.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    # Este método ahora recibirá un admin como argumento
    pass
