import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, time
from db import conectar
from tkcalendar import Calendar

ESTADOS = {
    "disponible": {"color": "#4CAF50", "texto": "Disponible"},
    "ocupada": {"color": "#F44336", "texto": "Ocupada"},
    "reservada": {"color": "#FFA500", "texto": "Reserva"},
}

def abrir_disponibilidad():
    ventana = ctk.CTkToplevel()
    ventana.title("Disponibilidad de Mesas")
    ventana.geometry("1000x800")
    
    frame = DisponibilidadFrame(ventana)
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    return ventana

class DisponibilidadFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")

        self.fecha_seleccionada = ctk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.hora_seleccionada = ctk.StringVar(value="19:00:00")
        self.personas = ctk.IntVar(value=2)
        self.calendario_abierto = False

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.crear_widgets()
        self.actualizar_disponibilidad()

    def crear_widgets(self):
        ctk.CTkLabel(self.main_frame, text="Disponibilidad de Mesas", font=("Arial", 20, "bold")).pack(pady=10)

        # Frame de controles
        control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        control_frame.pack(pady=10, fill="x")

        # Selector de fecha
        ctk.CTkLabel(control_frame, text="Fecha:").grid(row=0, column=0, padx=5)
        self.fecha_entry = ctk.CTkEntry(control_frame, textvariable=self.fecha_seleccionada, width=100)
        self.fecha_entry.grid(row=0, column=1, padx=5)
        ctk.CTkButton(control_frame, text="📅", width=30, command=self.abrir_calendario).grid(row=0, column=2, padx=5)

        # Selector de hora
        ctk.CTkLabel(control_frame, text="Hora:").grid(row=0, column=3, padx=5)
        horas = [f"{h:02d}:00:00" for h in range(12, 23)]
        ctk.CTkComboBox(control_frame, variable=self.hora_seleccionada, values=horas, width=100).grid(row=0, column=4, padx=5)

        # Selector de personas
        ctk.CTkLabel(control_frame, text="Personas:").grid(row=0, column=5, padx=5)
        ctk.CTkEntry(control_frame, textvariable=self.personas, width=60).grid(row=0, column=6, padx=5)

        # Botón de consulta (reemplazando el botón circular)
        ctk.CTkButton(control_frame, text="Consultar Disponibilidad", 
                     command=self.actualizar_disponibilidad, width=180).grid(row=0, column=7, padx=5)

        # Leyenda de estados
        estado_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        estado_frame.pack(pady=10)
        
        for estado, config in ESTADOS.items():
            ctk.CTkLabel(
                estado_frame,
                text=config["texto"],
                fg_color=config["color"],
                corner_radius=10,
                text_color="white",
                width=150,
                height=25,
                font=("Arial", 12)
            ).pack(side="left", padx=10)

        # Frame para resultados
        self.resultados_frame = ctk.CTkFrame(self.main_frame)
        self.resultados_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def abrir_calendario(self):
        if self.calendario_abierto:
            return
            
        self.calendario_abierto = True
        top = ctk.CTkToplevel(self)
        top.title("Seleccionar Fecha")
        top.geometry("300x300")
        top.transient(self)
        top.grab_set()
        
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20, padx=20, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Seleccionar", command=lambda: self.seleccionar_fecha(cal, top)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", command=top.destroy).pack(side="left", padx=10)
        
        top.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_calendario(top))

    def seleccionar_fecha(self, calendario, ventana):
        self.fecha_seleccionada.set(calendario.get_date())
        self.cerrar_calendario(ventana)
        self.actualizar_disponibilidad()

    def cerrar_calendario(self, ventana):
        self.calendario_abierto = False
        ventana.destroy()

    def actualizar_disponibilidad(self):
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()

        fecha = self.fecha_seleccionada.get()
        hora = self.hora_seleccionada.get()
        personas = self.personas.get()

        mesas = self.consultar_mesas(fecha, hora, personas)

        if not mesas:
            ctk.CTkLabel(self.resultados_frame, 
                        text="No se encontraron mesas",
                        text_color="red").pack(pady=20)
            return

        grid = ctk.CTkFrame(self.resultados_frame, fg_color="transparent")
        grid.pack(pady=10, padx=10, fill="both", expand=True)

        columnas = 4
        for i in range(columnas):
            grid.grid_columnconfigure(i, weight=1)

        for idx, mesa in enumerate(mesas):
            # Determinar el estado de la mesa
            if mesa['reservada_exacta']:
                estado = "reservada"
            elif mesa['estado'] == 'ocupada':
                estado = "ocupada"
            else:
                estado = "disponible"
            
            color = ESTADOS[estado]["color"]
            texto = ESTADOS[estado]["texto"]

            card = ctk.CTkFrame(grid, fg_color=color, corner_radius=10)
            card.grid(row=idx//columnas, column=idx%columnas, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(card, text=f"Mesa {mesa['numero_mesa']}", 
                         font=("Arial", 14, "bold"), 
                         text_color="white").pack(pady=5)
            
            ctk.CTkLabel(card, text=f"Capacidad: {mesa['capacidad']}", 
                        font=("Arial", 12), 
                        text_color="white").pack()
            
            ctk.CTkLabel(card, text=texto, 
                         font=("Arial", 12, "bold"), 
                         text_color="white").pack(pady=5)
            
            # Mostrar info adicional para mesas reservadas
            if mesa['reservada_exacta']:
                hora_reserva = mesa['hora_reserva'].strftime('%H:%M') if isinstance(mesa['hora_reserva'], time) else mesa['hora_reserva']
                ctk.CTkLabel(card, text=f"Reserva: {hora_reserva}",
                            font=("Arial", 11),
                            text_color="white").pack()

    def consultar_mesas(self, fecha, hora, personas):
        try:
            db = conectar()
            cursor = db.cursor(dictionary=True)

            query = """
                SELECT 
                    m.id_mesa,
                    m.numero_mesa,
                    m.capacidad,
                    m.estado,
                    CASE WHEN EXISTS (
                        SELECT 1 FROM reservas r 
                        WHERE r.id_mesa = m.id_mesa 
                        AND r.fecha_reserva = %s
                        AND r.hora_reserva = %s
                        AND r.estado = 'confirmada'
                    ) THEN 1 ELSE 0 END AS reservada_exacta,
                    (
                        SELECT r.hora_reserva 
                        FROM reservas r 
                        WHERE r.id_mesa = m.id_mesa 
                        AND r.fecha_reserva = %s
                        AND r.hora_reserva = %s
                        AND r.estado = 'confirmada'
                        LIMIT 1
                    ) AS hora_reserva
                FROM mesas m
                WHERE m.capacidad >= %s
                ORDER BY m.numero_mesa
            """

            cursor.execute(query, (fecha, hora, fecha, hora, personas))
            mesas = cursor.fetchall()
            db.close()
            return mesas

        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar mesas:\n{str(e)}")
            return []