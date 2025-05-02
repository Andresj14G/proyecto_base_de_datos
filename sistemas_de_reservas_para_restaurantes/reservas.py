import customtkinter as ctk
from tkinter import messagebox
from db import conectar
from datetime import datetime
from tkinter import ttk
from tkcalendar import Calendar
import tkinter as tk

id_reserva_editando = None


def abrir_reservas():
    global id_reserva_editando

    def cancelar_reserva():
        global id_reserva_editando
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona una reserva", "Debes seleccionar una reserva para cancelar")
            return
        id_reserva_a_cancelar = tabla.item(seleccion[0])["values"][0] # Obtener el ID de la reserva a cancelar

        confirmacion = messagebox.askyesno("Confirmar Cancelación", "¿Estás seguro de que deseas cancelar esta reserva?")
        if confirmacion:
            db = conectar()
            cursor = db.cursor()
            try:
                cursor.execute("DELETE FROM reservas WHERE id_reserva = %s", (id_reserva_a_cancelar,))
                db.commit()
                messagebox.showinfo("Reserva Cancelada", "La reserva ha sido cancelada exitosamente")
                cargar_tabla_reservas() # Recargar la tabla para reflejar la eliminación
                limpiar_campos()
                btn_guardar_cambios.pack_forget() # Ocultar el botón "Guardar Cambios" si estaba visible
                id_reserva_editando = None
                if tabla_frame.winfo_ismapped():
                    toggle_tabla() # Ocultar la tabla después de cancelar
            except Exception as e:
                messagebox.showerror("Error al Cancelar", f"Ocurrió un error al cancelar la reserva: {e}")
                db.rollback()
            finally:
                db.close()
        else:
            messagebox.showinfo("Cancelación Abortada", "La cancelación de la reserva ha sido abortada")

    def modificar_reserva():
        global id_reserva_editando
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona una reserva", "Debes seleccionar una reserva para modificar")
            return
        id_reserva_editando = tabla.item(seleccion[0])["values"][0]
        db = conectar()
        cursor = db.cursor()
        cursor.execute("""
            SELECT r.id_reserva, c.id_cliente, r.id_mesa, r.fecha_reserva, r.hora_reserva, r.num_personas
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            WHERE r.id_reserva = %s
        """, (id_reserva_editando,))
        reserva = cursor.fetchone()
        db.close()
        cliente_combo.set(f"{reserva[1]} -")
        entry_fecha_reserva.delete(0, ctk.END)
        entry_fecha_reserva.insert(0, reserva[3])
        entry_hora_reserva.delete(0, ctk.END)
        hora_obj = datetime.strptime(str(reserva[4]), '%H:%M:%S')
        horas_combo.set(hora_obj.strftime('%I'))
        minutos_combo.set(hora_obj.strftime('%M'))
        ampm_combo.set(hora_obj.strftime('%p'))
        entry_hora_reserva.insert(0, hora_obj.strftime('%I:%M %p'))
        entry_personas.delete(0, ctk.END)
        entry_personas.insert(0, reserva[5])
        mesa_combo.set(reserva[2])
        btn_guardar_cambios.pack(pady=5)

    app = ctk.CTk()
    app.title("Gestión de Reservas")
    app.geometry("600x750")

    ctk.CTkLabel(app, text="Registrar Nueva Reserva", font=("Arial", 18, "bold")).pack(pady=20)
    ctk.CTkLabel(app, text="Seleccionar Cliente:").pack(pady=5)
    cliente_combo = ctk.CTkComboBox(app, width=300)
    cliente_combo.pack(pady=5)
    cliente_combo.set("Seleccione un cliente") # Establecer texto inicial

    def cargar_clientes():
        db = conectar()
        cursor = db.cursor()
        cursor.execute("SELECT id_cliente, nombre_completo FROM clientes")
        clientes = cursor.fetchall()
        db.close()
        opciones = [f"{id} - {nombre}" for (id, nombre) in clientes]
        cliente_combo.configure(values=opciones)

    cargar_clientes()

    ctk.CTkLabel(app, text="Fecha de Reserva:").pack(pady=5)
    entry_fecha_reserva = ctk.CTkEntry(app, width=200)
    entry_fecha_reserva.pack(pady=5)

    def abrir_calendario():
        top = ctk.CTkToplevel(app)
        top.title("Seleccionar fecha")
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10)

        def seleccionar_fecha():
            fecha = cal.get_date()
            entry_fecha_reserva.delete(0, ctk.END)
            entry_fecha_reserva.insert(0, fecha)
            top.destroy()

        ctk.CTkButton(top, text="Seleccionar", command=seleccionar_fecha).pack(pady=5)

    ctk.CTkButton(app, text="📅 Elegir Fecha", command=abrir_calendario).pack()
    ctk.CTkLabel(app, text="Hora de Reserva:").pack(pady=5)
    hora_frame = ctk.CTkFrame(app)
    hora_frame.pack(pady=5)
    horas_combo = ctk.CTkComboBox(hora_frame, width=80, values=[f"{i:02d}" for i in range(1, 13)])
    horas_combo.set("12")
    horas_combo.grid(row=0, column=0, padx=5)
    minutos_combo = ctk.CTkComboBox(hora_frame, width=80, values=[f"{i:02d}" for i in range(0, 60)])
    minutos_combo.set("00")
    minutos_combo.grid(row=0, column=1, padx=5)
    ampm_combo = ctk.CTkComboBox(hora_frame, width=60, values=["AM", "PM"])
    ampm_combo.set("AM")
    ampm_combo.grid(row=0, column=2, padx=5)

    def actualizar_hora():
        hora = horas_combo.get()
        minutos = minutos_combo.get()
        ampm = ampm_combo.get()
        try:
            hora_obj = datetime.strptime(f"{hora}:{minutos} {ampm}", '%I:%M %p')
            entry_hora_reserva.delete(0, ctk.END)
            entry_hora_reserva.insert(0, hora_obj.strftime('%I:%M %p'))
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM AM/PM")

    ctk.CTkButton(hora_frame, text="Seleccionar Hora", command=actualizar_hora).grid(row=1, columnspan=3, pady=10)
    entry_hora_reserva = ctk.CTkEntry(app)
    entry_hora_reserva.pack(pady=10)
    ctk.CTkLabel(app, text="Número de Personas:").pack(pady=5)
    entry_personas = ctk.CTkEntry(app)
    entry_personas.pack()

    def limpiar_campos():
        cliente_combo.set("")
        entry_fecha_reserva.delete(0, ctk.END)
        entry_hora_reserva.delete(0, ctk.END)
        entry_personas.delete(0, ctk.END)
        mesa_combo.set("")
        horas_combo.set("12")
        minutos_combo.set("00")
        ampm_combo.set("AM")
        btn_guardar_cambios.pack_forget()

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
    mesa_combo.set("Seleccione una mesa") # Establecer texto inicial

    def confirmar():
        global id_reserva_editando
        cliente_seleccionado = cliente_combo.get()
        if not cliente_seleccionado or cliente_seleccionado == "Seleccione un cliente" or '-' not in cliente_seleccionado:
            messagebox.showerror("Error", "Selecciona un cliente válido de la lista.")
            return
        try:
            id_cliente = int(cliente_seleccionado.split(" - ")[0])
        except ValueError:
            messagebox.showerror("Error", "El ID del cliente no es un número válido.")
            return

        mesa_seleccionada = mesa_combo.get()
        if not mesa_seleccionada or mesa_seleccionada == "Seleccione una mesa":
            messagebox.showerror("Error", "Selecciona una mesa disponible.")
            return
        id_mesa = mesa_seleccionada

        fecha_reserva = entry_fecha_reserva.get()
        hora_reserva_raw = entry_hora_reserva.get()
        personas = entry_personas.get()
        fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            hora_reserva_24 = datetime.strptime(hora_reserva_raw.strip(), '%I:%M %p').strftime('%H:%M:%S')
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM AM/PM")
            return
        db = conectar()
        cursor = db.cursor()
        try:
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
            cargar_tabla_reservas()
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar la reserva: {e}")
            db.rollback() # Importante para deshacer cualquier cambio en caso de error
        finally:
            db.close()

    ctk.CTkButton(app, text="Confirmar Reserva", command=confirmar).pack(pady=10)

    # Sección de Reservas Activas
    reservas_activas_button = ctk.CTkButton(app, text="Reservas Activas")
    reservas_activas_button.pack(pady=5)

    # Frame para los botones Modificar y Cancelar
    botones_opciones_frame = ctk.CTkFrame(app)
    botones_opciones_frame.pack(pady=5)

    modificar_button = ctk.CTkButton(botones_opciones_frame, text="Modificar Reserva", command=modificar_reserva)
    modificar_button.pack(side="left", padx=5)
    cancelar_button = ctk.CTkButton(botones_opciones_frame, text="Cancelar Reserva", command=cancelar_reserva)
    cancelar_button.pack(side="left", padx=5)
    btn_guardar_cambios = ctk.CTkButton(botones_opciones_frame, text="Guardar Cambios", command=confirmar)
    btn_guardar_cambios.pack_forget() # Ocultar inicialmente

    tabla_frame = ctk.CTkFrame(app)
    # No empaquetamos tabla_frame aquí inicialmente

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

    def toggle_tabla():
        if tabla_frame.winfo_ismapped():
            tabla_frame.pack_forget()
        else:
            tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

    reservas_activas_button.configure(command=toggle_tabla)

    app.mainloop()