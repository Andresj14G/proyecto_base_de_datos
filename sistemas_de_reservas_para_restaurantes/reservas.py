import customtkinter as ctk
from tkinter import messagebox
from db import conectar
from datetime import datetime
from tkinter import ttk
from tkcalendar import Calendar
import smtplib
from email.mime.text import MIMEText

EMAIL_SENDER = 'sistemarestaurante7@gmail.com'
EMAIL_PASSWORD = 'bwcy obyx nnvs rnwa'  # pega aquí la contraseña de aplicación
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587


def enviar_correo_confirmacion(nombre, correo, fecha, hora, personas, mesa, correo_admin):
    asunto = "Confirmación de Reserva"
    cuerpo = f"""Estimado/a {nombre},

Su reserva ha sido confirmada con los siguientes detalles:

Fecha: {fecha}
Hora: {hora}
Número de personas: {personas}
Mesa asignada: {mesa}

Esta reserva fue realizada por el administrador: {correo_admin}

Gracias por su preferencia."""


    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = EMAIL_SENDER
    msg['To'] = correo

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        messagebox.showinfo("Correo enviado", "Correo de confirmación enviado al cliente.")
    except Exception as e:
        messagebox.showerror("Error de correo", f"No se pudo enviar el correo: {str(e)}")


id_reserva_editando = None
mesas_buscadas = False
app = None

def abrir_reservas():
    global id_reserva_editando, mesas_buscadas
    mesas_buscadas = False

    app = ctk.CTk()
    app.title("Registrar Nueva Reserva")
    app.geometry("600x600")

    # ---------------- Cliente ----------------
    ctk.CTkLabel(app, text="Seleccionar Cliente:").pack(pady=(20, 5))
    cliente_combo = ctk.CTkComboBox(app, width=300)
    cliente_combo.pack()
    cliente_combo.set("Seleccione un cliente")

    def cargar_clientes():
        db = conectar()
        cur = db.cursor()
        cur.execute("SELECT id_cliente, nombre_completo FROM clientes")
        opciones = [f"{i} - {n}" for i, n in cur.fetchall()]
        db.close()
        print(f"Opciones del combo box: {opciones}") # Para depuración
        cliente_combo.configure(values=opciones)
    cargar_clientes()

    # ---------------- Fecha ----------------
    ctk.CTkLabel(app, text="Fecha de Reserva:").pack(pady=(15, 5))
    entry_fecha = ctk.CTkEntry(app, width=200)
    entry_fecha.pack()

    def abrir_calendario():
        top = ctk.CTkToplevel(app)
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10)
        def sel_fecha():
            entry_fecha.delete(0, ctk.END)
            entry_fecha.insert(0, cal.get_date())
            top.destroy()
        ctk.CTkButton(top, text="Seleccionar", command=sel_fecha).pack(pady=5)
    ctk.CTkButton(app, text="📅 Elegir Fecha", command=abrir_calendario).pack()

    # ---------------- Hora ----------------
    ctk.CTkLabel(app, text="Hora de Reserva:").pack(pady=(15, 5))
    frame_hora = ctk.CTkFrame(app)
    frame_hora.pack()
    horas = [f"{i:02d}" for i in range(1, 13)]
    minutos = [f"{i:02d}" for i in range(60)]
    combo_h = ctk.CTkComboBox(frame_hora, values=horas, width=60)
    combo_m = ctk.CTkComboBox(frame_hora, values=minutos, width=60)
    combo_ap = ctk.CTkComboBox(frame_hora, values=["AM", "PM"], width=60)
    combo_h.set("12"); combo_m.set("00"); combo_ap.set("AM")
    combo_h.grid(row=0, column=0, padx=5)
    combo_m.grid(row=0, column=1, padx=5)
    combo_ap.grid(row=0, column=2, padx=5)
    entry_hora = ctk.CTkEntry(app, width=200)
    entry_hora.pack(pady=5)

    def seleccionar_hora():
        try:
            dt = datetime.strptime(f"{combo_h.get()}:{combo_m.get()} {combo_ap.get()}", '%I:%M %p')
            entry_hora.delete(0, ctk.END)
            entry_hora.insert(0, dt.strftime('%I:%M %p'))
        except:
            messagebox.showerror("Error", "Formato de hora inválido")
    ctk.CTkButton(app, text="⏰ Seleccionar Hora", command=seleccionar_hora).pack()

    # ---------------- Personas ----------------
    ctk.CTkLabel(app, text="Número de Personas:").pack(pady=(15, 5))
    entry_personas = ctk.CTkEntry(app, width=200)
    entry_personas.pack()

    # ---------------- Mesas disponibles ----------------
    ctk.CTkLabel(app, text="Mesas disponibles:").pack(pady=(15, 5))
    combo_mesa = ctk.CTkComboBox(app, values=[], width=200, state="disabled")
    combo_mesa.pack()

    def buscar_mesas():
        global mesas_buscadas
        fecha = entry_fecha.get()
        hora = entry_hora.get()
        pers = entry_personas.get()
        sel = cliente_combo.get()
        

        campos_vacios = []
        if sel == "Seleccione un cliente":
            campos_vacios.append("Cliente")
        if not fecha:
            campos_vacios.append("Fecha")
        if not hora:
            campos_vacios.append("Hora")
        if not pers:
            campos_vacios.append("Número de Personas")
        

        if campos_vacios:
            mensaje = "Rellene el resto de campos: " + ", ".join(campos_vacios)
            messagebox.showerror("Error", mensaje)
            return

        if not fecha or not pers:
            messagebox.showerror("Error", "Complete fecha y personas")
            return
        try:
            pers_i = int(pers)
            assert pers_i > 0
        except:
            messagebox.showerror("Error", "Número de personas inválido")
            return
        db = conectar()
        cur = db.cursor()
        cur.execute(
            "SELECT id_mesa FROM mesas WHERE estado='disponible' AND capacidad>= %s "
            "AND id_mesa NOT IN (SELECT id_mesa FROM reservas WHERE fecha_reserva=%s AND hora_reserva=%s AND estado='confirmada')",
            (pers_i, fecha, hora)
        )
        disponibles = [str(r[0]) for r in cur.fetchall()]
        db.close()
        if disponibles:
            combo_mesa.configure(values=disponibles, state="normal")
            combo_mesa.set(disponibles[0])
            mesas_buscadas = True
        else:
            messagebox.showinfo("Sin mesas", "No hay mesas disponibles")
            combo_mesa.configure(values=[], state="disabled")
            mesas_buscadas = False
    ctk.CTkButton(app, text="Buscar Mesas", command=buscar_mesas).pack(pady=10)

    # ---------------- Limpiar campos ----------------
    def limpiar_campos():
        global id_reserva_editando, mesas_buscadas
        id_reserva_editando = None
        mesas_buscadas = False
        cliente_combo.set("Seleccione un cliente")
        entry_fecha.delete(0, ctk.END)
        entry_hora.delete(0, ctk.END)
        entry_personas.delete(0, ctk.END)
        combo_mesa.configure(values=[], state="disabled")
        combo_mesa.set("")
        btn_guardar.pack_forget()
        btn_confirmar.pack(pady=10)

    # ---------------- Insertar nueva reserva ----------------
    def confirmar():
        sel = cliente_combo.get()
        fecha = entry_fecha.get()
        hora = entry_hora.get()
        pers = entry_personas.get()
        mid = combo_mesa.get()


        campos_vacios = []
        if sel == "Seleccione un cliente":
            campos_vacios.append("Cliente")
        if not fecha:
            campos_vacios.append("Fecha")
        if not hora:
            campos_vacios.append("Hora")
        if not pers:
            campos_vacios.append("Número de Personas")
        if not mesas_buscadas or not mid:
            campos_vacios.append("Mesa")

        if campos_vacios:
            mensaje = "Rellene el resto de campos: " + ", ".join(campos_vacios)
            messagebox.showerror("Error", mensaje)
            return

        if '-' not in sel:
            messagebox.showerror("Error", "Error al obtener ID del cliente")
            return
        try:
            cid = int(sel.split(' - ')[0])
        except ValueError:
            messagebox.showerror("Error", "Error al obtener ID del cliente")
            return
        if not mesas_buscadas:
            messagebox.showerror("Error", "Busque mesas primero")
            return
        try:
            hora_24 = datetime.strptime(hora, '%I:%M %p').strftime('%H:%M:%S')
            pers_i = int(pers)
            assert pers_i > 0
        except ValueError:
            messagebox.showerror("Error", "Formato de hora o número de personas inválido")
            return
        except AssertionError:
            messagebox.showerror("Error", "Número de personas debe ser mayor que cero")
            return

        ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db = conectar()
        cur = db.cursor()
        try:
            # Validar que la mesa no esté ocupada en esa fecha y hora
            cur.execute(
                "SELECT COUNT(*) FROM reservas WHERE id_mesa=%s AND fecha_reserva=%s AND hora_reserva=%s AND estado='confirmada'",
                (mid, fecha, hora_24)
            )
            ya_reservada = cur.fetchone()[0]

            if ya_reservada > 0:
                messagebox.showerror("Error", "Esa mesa ya está reservada para esa fecha y hora.")
                db.close()
                return

            # Insertar la nueva reserva
            cur.execute(
                "INSERT INTO reservas (id_cliente, id_mesa, fecha_reserva, hora_reserva, num_personas, estado, fecha_creacion)"
                " VALUES (%s, %s, %s, %s, %s, 'confirmada', %s)",
                (cid, mid, fecha, hora_24, pers_i, ahora)
            )
            db.commit()
            messagebox.showinfo("OK", "Reserva registrada")

            # Obtener datos del cliente y enviar correo
            cur.execute("SELECT nombre_completo, correo_electronico FROM clientes WHERE id_cliente=%s", (cid,))
            cliente = cur.fetchone()
            if cliente:
                enviar_correo_confirmacion(
                    nombre=cliente[0],
                    correo=cliente[1],
                    fecha=fecha,
                    hora=hora_24,
                    personas=pers_i,
                    mesa=mid,
                    correo_admin='admin@correo.com'
            )
        except Exception as e:
                db.rollback()
                messagebox.showerror("Error", str(e))
        finally:
            db.close()

    # ---------------- Actualizar reserva existente ----------------
    # ---------------- Actualizar reserva existente ----------------
    def guardar_cambios():
        global id_reserva_editando, app
        if not id_reserva_editando:
            messagebox.showerror("Error", "Nada que guardar")
            return
        sel = cliente_combo.get()
        if '-' not in sel:
            messagebox.showerror("Error", "Cliente inválido")
            return
        try:
            cid = int(sel.split(' - ')[0])
        except ValueError:
            messagebox.showerror("Error", "Error al obtener ID del cliente")
            return
        mid = combo_mesa.get()
        fecha = entry_fecha.get()
        hora_24 = datetime.strptime(entry_hora.get(), '%I:%M %p').strftime('%H:%M:%S')
        pers = int(entry_personas.get())
        db = conectar()
        cur = db.cursor()
        try:
            # Validar que la mesa no esté ocupada por otra reserva (excluyendo la actual)
            cur.execute(
                "SELECT COUNT(*) FROM reservas WHERE id_mesa=%s AND fecha_reserva=%s AND hora_reserva=%s AND estado='confirmada' AND id_reserva != %s",
                (mid, fecha, hora_24, id_reserva_editando)
            )
            ya_reservada = cur.fetchone()[0]
            if ya_reservada > 0:
                messagebox.showerror("Error", "Esa mesa ya está reservada para esa fecha y hora.")
                db.close()
                return

            cur.execute(
                "UPDATE reservas SET id_cliente=%s, id_mesa=%s, fecha_reserva=%s, hora_reserva=%s, num_personas=%s"
                " WHERE id_reserva=%s",
                (cid, mid, fecha, hora_24, pers, id_reserva_editando)
            )
            db.commit()
            messagebox.showinfo("OK", "Reserva actualizada")
            # Obtener datos del cliente y enviar correo con nuevos detalles
            cur.execute("SELECT nombre_completo, correo_electronico FROM clientes WHERE id_cliente=%s", (cid,))
            cliente = cur.fetchone()
            if cliente:
                enviar_correo_confirmacion(
                nombre=cliente[0],
                correo=cliente[1],
                fecha=fecha,
                hora=hora_24,
                personas=pers,
                mesa=mid,
                correo_admin='admin@correo.com'  # o usa admin['correo'] si está en sesión
    )

            limpiar_campos()
            if app is not None:
                app.destroy() # Cierra solo la ventana de edición
            # Si la ventana de gestión ('win') ya está abierta, no necesitas volver a crearla aquí.
            # La actualización se verá la próxima vez que la consultes.
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error BD", str(e))
        finally:
            db.close()

    # ---------------- Botones principales ----------------
    btn_confirmar = ctk.CTkButton(app, text="Confirmar Reserva", command=confirmar)
    btn_confirmar.pack(pady=10)
    btn_guardar = ctk.CTkButton(app, text="Guardar Cambios", command=guardar_cambios, fg_color="green")

    # ---------------- Gestión de reservas ----------------
    def gestionar_reservas():
        global id_reserva_editando, mesas_buscadas
        win = ctk.CTkToplevel(app)
        win.title("Gestión de Reservas")
        win.geometry("700x400")

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        style = ttk.Style(win)
        style.theme_use("default")
        style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0", foreground="black")

        tv = ttk.Treeview(frame, columns=("ID","Cliente","Mesa","Fecha","Hora","Personas"), show="headings")
        for col in tv["columns"]:
            tv.heading(col, text=col)
            tv.column(col, width=100)
        tv.pack(fill="both", expand=True)

        def cargar():
            for row in tv.get_children():
                tv.delete(row)
            db = conectar()
            cur = db.cursor()
            cur.execute(
                "SELECT r.id_reserva, c.nombre_completo, r.id_mesa, r.fecha_reserva, r.hora_reserva, r.num_personas"
                " FROM reservas r JOIN clientes c ON r.id_cliente=c.id_cliente"
                " WHERE r.estado='confirmada' ORDER BY r.fecha_reserva, r.hora_reserva"
            )
            for r in cur.fetchall():
                tv.insert("", "end", values=r)
            db.close()
        cargar()

        def cancelar_res():
            sel = tv.selection()
            if not sel:
                messagebox.showwarning("Error", "Seleccione una reserva")
                return
            rid = tv.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Cancelar reserva?"):
                db = conectar()
                cur = db.cursor()
                try:
                    cur.execute("DELETE FROM reservas WHERE id_reserva=%s", (rid,))
                    db.commit()
                    cargar()
                except:
                    db.rollback()
                finally:
                    db.close()

        def modificar_res():
            global id_reserva_editando, mesas_buscadas
            sel = tv.selection()
            if not sel:
                messagebox.showwarning("Error", "Seleccione una reserva")
                return
            rid, nombre_cliente, mid, f, h, p = tv.item(sel[0])["values"] # Ahora obtenemos el nombre
            print(f"ID de reserva a editar: {rid}, Nombre del cliente: {nombre_cliente}") # Para depuración
            id_reserva_editando = rid
            # Necesitamos buscar el ID del cliente correspondiente al nombre para setear el combo box correctamente
            db = conectar()
            cur = db.cursor()
            cur.execute("SELECT id_cliente FROM clientes WHERE nombre_completo=%s", (nombre_cliente,))
            cliente_id = cur.fetchone()
            db.close()
            if cliente_id:
                cliente_combo.set(f"{cliente_id[0]} - {nombre_cliente}")
            else:
                cliente_combo.set("") # O maneja el caso si no se encuentra el ID
                messagebox.showerror("Error", "No se encontró el ID del cliente para la reserva.")
                return

            entry_fecha.delete(0, ctk.END)
            entry_fecha.insert(0, f)
            dt = datetime.strptime(h, '%H:%M:%S')
            combo_h.set(dt.strftime('%I'))
            combo_m.set(dt.strftime('%M'))
            combo_ap.set(dt.strftime('%p'))
            entry_hora.delete(0, ctk.END)
            entry_hora.insert(0, dt.strftime('%I:%M %p'))
            entry_personas.delete(0, ctk.END)
            entry_personas.insert(0, p)
            combo_mesa.configure(values=[str(mid)], state="normal")
            combo_mesa.set(str(mid))
            mesas_buscadas = True
            win.destroy()
            btn_confirmar.pack_forget()
            btn_guardar.pack(pady=10)

        ctk.CTkButton(win, text="Modificar Reserva", command=modificar_res).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(win, text="Cancelar Reserva", command=cancelar_res, fg_color="red").pack(side="left", padx=10, pady=10)

    ctk.CTkButton(app, text="Gestionar Reservas", command=gestionar_reservas).pack(pady=10)
    app.mainloop()

if __name__ == "__main__":
    abrir_reservas()