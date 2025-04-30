import customtkinter as ctk
from tkinter import messagebox
from db import conectar
from datetime import datetime
from tkinter import ttk

id_reserva_editando = None

def abrir_reservas():
    global id_reserva_editando
    app = ctk.CTk()
    app.title("Gestión de Reservas")
    app.geometry("600x750")

    ctk.CTkLabel(app, text="Registrar Nueva Reserva", font=("Arial", 18, "bold")).pack(pady=20)

    ctk.CTkLabel(app, text="Seleccionar Cliente:").pack(pady=5)
    cliente_combo = ctk.CTkComboBox(app, width=300)
    cliente_combo.pack()

    def cargar_clientes():
        db = conectar()
        cursor = db.cursor()
        cursor.execute("SELECT id_cliente, nombre_completo FROM clientes")
        clientes = cursor.fetchall()
        db.close()
        opciones = [f"{id} - {nombre}" for (id, nombre) in clientes]
        cliente_combo.configure(values=opciones)

    cargar_clientes()

    ctk.CTkLabel(app, text="Fecha de Reserva (YYYY-MM-DD):").pack(pady=5)
    entry_fecha_reserva = ctk.CTkEntry(app)
    entry_fecha_reserva.pack()

    ctk.CTkLabel(app, text="Hora de Reserva (HH:MM AM/PM):").pack(pady=5)
    entry_hora_reserva = ctk.CTkEntry(app)
    entry_hora_reserva.pack()

    ctk.CTkLabel(app, text="Número de Personas:").pack(pady=5)
    entry_personas = ctk.CTkEntry(app)
    entry_personas.pack()

    def buscar_mesas():
        fecha_reserva = entry_fecha_reserva.get()
        hora_reserva_raw = entry_hora_reserva.get()
        personas = entry_personas.get()

        try:
            hora_obj = datetime.strptime(hora_reserva_raw.strip(), '%I:%M %p')
            hora_reserva_24 = hora_obj.strftime('%H:%M:%S')
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM AM/PM")
            return

        if not fecha_reserva or not hora_reserva_24 or not personas:
            messagebox.showerror("Error", "Todos los campos deben estar completos")
            return

        try:
            personas = int(personas)
        except:
            messagebox.showerror("Error", "Número de personas inválido")
            return

        db = conectar()
        cursor = db.cursor()
        cursor.execute(""" 
            SELECT id_mesa FROM mesas 
            WHERE estado = 'activa' AND capacidad >= %s AND id_mesa NOT IN (
                SELECT id_mesa FROM reservas
                WHERE fecha_reserva = %s AND hora_reserva = %s AND estado = 'confirmada')
        """, (personas, fecha_reserva, hora_reserva_24))
        disponibles = cursor.fetchall()
        db.close()

        if disponibles:
            mesa_combo.configure(values=[str(m[0]) for m in disponibles])
            mesa_combo.set(str(disponibles[0][0]))
        else:
            messagebox.showinfo("Sin disponibilidad", "No hay mesas disponibles para ese horario")
            mesa_combo.configure(values=[])

    ctk.CTkButton(app, text="Buscar Mesas Disponibles", command=buscar_mesas).pack(pady=10)

    ctk.CTkLabel(app, text="Mesa disponible:").pack(pady=5)
    mesa_combo = ctk.CTkComboBox(app, width=300)
    mesa_combo.pack()

    def confirmar():
        global id_reserva_editando

        cliente = cliente_combo.get()
        if not cliente or '-' not in cliente:
            messagebox.showerror("Error", "Selecciona un cliente válido")
            return

        id_cliente = cliente.split(" - ")[0]
        id_mesa = mesa_combo.get()
        fecha_reserva = entry_fecha_reserva.get()
        hora_reserva_raw = entry_hora_reserva.get()
        personas = entry_personas.get()
        fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            hora_reserva_24 = datetime.strptime(hora_reserva_raw.strip(), '%I:%M %p').strftime('%H:%M:%S')
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM AM/PM")
            return

        if not id_mesa:
            messagebox.showerror("Error", "No se ha seleccionado ninguna mesa")
            return

        db = conectar()
        cursor = db.cursor()

        if id_reserva_editando:
            cursor.execute("""
                UPDATE reservas SET id_cliente = %s, id_mesa = %s, fecha_reserva = %s,
                hora_reserva = %s, num_personas = %s WHERE id_reserva = %s
            """, (id_cliente, id_mesa, fecha_reserva, hora_reserva_24, personas, id_reserva_editando))
            messagebox.showinfo("Reserva Actualizada", "La reserva fue actualizada exitosamente")
            id_reserva_editando = None
        else:
            cursor.execute("""
                INSERT INTO reservas (id_cliente, id_mesa, fecha_reserva, hora_reserva, num_personas, estado, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, 'confirmada', %s)
            """, (id_cliente, id_mesa, fecha_reserva, hora_reserva_24, personas, fecha_creacion))
            messagebox.showinfo("Reserva Confirmada", "La reserva ha sido registrada exitosamente")

        db.commit()
        db.close()

        cargar_tabla_reservas()

    ctk.CTkButton(app, text="Confirmar Reserva", command=confirmar).pack(pady=10)

    def toggle_tabla():
        if tabla_frame.winfo_ismapped():
            tabla_frame.pack_forget()
        else:
            tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkButton(app, text="Reservas Activas", command=toggle_tabla).pack(pady=5)

    tabla_frame = ctk.CTkFrame(app)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0", foreground="black")

    tabla = ttk.Treeview(tabla_frame, columns=("ID", "Cliente", "Mesa", "Fecha", "Hora", "Personas"), show="headings")
    for col in tabla["columns"]:
        tabla.heading(col, text=col)
        tabla.column(col, width=80)
    tabla.pack(fill="both", expand=True)

    def cargar_tabla_reservas():
        for row in tabla.get_children():
            tabla.delete(row)

        db = conectar()
        cursor = db.cursor()
        cursor.execute("""
            SELECT r.id_reserva, c.nombre_completo, r.id_mesa, r.fecha_reserva, r.hora_reserva, r.num_personas
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            WHERE r.estado = 'confirmada'
            ORDER BY r.fecha_reserva, r.hora_reserva
        """)
        for row in cursor.fetchall():
            tabla.insert("", "end", values=row)
        db.close()

    cargar_tabla_reservas()

    def cancelar_reserva():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona una reserva", "Debes seleccionar una reserva para cancelar")
            return

        id_reserva = tabla.item(seleccion[0])["values"][0]

        db = conectar()
        cursor = db.cursor()
        cursor.execute("UPDATE reservas SET estado = 'cancelada' WHERE id_reserva = %s", (id_reserva,))
        db.commit()
        db.close()
        messagebox.showinfo("Cancelado", "La reserva fue cancelada correctamente")
        cargar_tabla_reservas()

    def modificar_reserva():
        global id_reserva_editando
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona una reserva", "Debes seleccionar una reserva para modificar")
            return

        datos = tabla.item(seleccion[0])["values"]
        id_reserva_editando = datos[0]

        nombre_cliente = datos[1]
        db = conectar()
        cursor = db.cursor()
        cursor.execute("SELECT id_cliente FROM clientes WHERE nombre_completo = %s", (nombre_cliente,))
        resultado = cursor.fetchone()
        db.close()

        if resultado:
            id_cliente = resultado[0]
            cliente_combo.set(f"{id_cliente} - {nombre_cliente}")
        else:
            messagebox.showerror("Error", "Cliente no encontrado en la base de datos")
            return

        mesa_combo.set(str(datos[2]))
        entry_fecha_reserva.delete(0, ctk.END)
        entry_fecha_reserva.insert(0, datos[3])
        entry_hora_reserva.delete(0, ctk.END)
        entry_hora_reserva.insert(0, datetime.strptime(datos[4], '%H:%M:%S').strftime('%I:%M %p'))
        entry_personas.delete(0, ctk.END)
        entry_personas.insert(0, datos[5])

    ctk.CTkButton(app, text="Modificar Reserva", width=300, height=40, command=modificar_reserva).pack(pady=5)
    ctk.CTkButton(app, text="Guardar Cambios", width=300, height=40, fg_color="green", command=confirmar).pack(pady=5)
    ctk.CTkButton(app, text="Cancelar Reserva", width=300, height=40, fg_color="red", command=cancelar_reserva).pack(pady=5)

    app.mainloop()
