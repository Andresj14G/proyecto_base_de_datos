import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from tkinter import messagebox
import calendar
from db import conectar

# Configuración de customtkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class DisponibilidadScreen(ctk.CTkFrame):
    def __init__(self, parent, cambiar_pantalla):
        super().__init__(parent)
        self.cambiar_pantalla = cambiar_pantalla
        self.configure(fg_color="transparent")
        
        # Configuración de grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Variables
        self.fecha_seleccionada = ctk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.hora_seleccionada = ctk.StringVar(value="19:00")
        self.personas = ctk.IntVar(value=2)
        
        # Widgets
        self.crear_widgets()
        
        # Cargar datos iniciales
        self.actualizar_disponibilidad()
    
    def crear_widgets(self):
        # Título
        ctk.CTkLabel(
            self.main_frame, 
            text="Consulta de Disponibilidad", 
            font=("Arial", 20, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Selector de fecha
        ctk.CTkLabel(self.main_frame, text="Fecha:").grid(row=1, column=0, sticky="w")
        self.calendario = ctk.CTkEntry(self.main_frame, textvariable=self.fecha_seleccionada)
        self.calendario.grid(row=1, column=1, sticky="ew", padx=5)
        ctk.CTkButton(
            self.main_frame, 
            text="📅", 
            width=30,
            command=self.mostrar_calendario
        ).grid(row=1, column=2, padx=(5, 0))
        
        # Selector de hora
        ctk.CTkLabel(self.main_frame, text="Hora:").grid(row=2, column=0, sticky="w")
        horas = [f"{h:02d}:00" for h in range(12, 23)]
        self.combo_hora = ctk.CTkComboBox(
            self.main_frame, 
            variable=self.hora_seleccionada,
            values=horas
        )
        self.combo_hora.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Número de personas
        ctk.CTkLabel(self.main_frame, text="Personas:").grid(row=3, column=0, sticky="w")

        # Frame para el control de entrada
        entry_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        entry_frame.grid(row=3, column=1, sticky="ew", pady=5)

        # Entrada de texto para número de personas
        self.entry_personas = ctk.CTkEntry(
            entry_frame,
            width=60,
            justify="center",
            textvariable=self.personas
        )
        self.entry_personas.pack(side="left", padx=5)

        # eventos
        self.entry_personas.bind("<Return>", lambda e: self.validar_personas())
        self.entry_personas.bind("<FocusOut>", lambda e: self.validar_personas())

        # Botón de consulta
        ctk.CTkButton(
            self.main_frame,
            text="Consultar Disponibilidad",
            command=self.actualizar_disponibilidad
        ).grid(row=4, column=0, columnspan=3, pady=10)
        
        # Frame para resultados
        self.resultados_frame = ctk.CTkFrame(self.main_frame)
        self.resultados_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        
        # Configurar grid para expansión
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)
    
    def validar_personas(self, event=None):
        """Valida el valor ingresado en el entry de personas"""
        try:
            valor = int(self.entry_personas.get())
            if valor < 1:
                self.personas.set(1)
                messagebox.showwarning("Advertencia", "El número mínimo de personas es 1")
            elif valor > 10:
                self.personas.set(10)
                messagebox.showwarning("Advertencia", "El número máximo de personas es 10")
            else:
                self.personas.set(valor)
            
            # Actualizar el entry con el valor validado
            self.entry_personas.delete(0, "end")
            self.entry_personas.insert(0, str(self.personas.get()))
            
            # Actualizar disponibilidad
            self.actualizar_disponibilidad()
            
        except ValueError:
            self.personas.set(2)  # Valor por defecto si no es número
            messagebox.showerror("Error", "Por favor ingrese un número válido")
            self.entry_personas.delete(0, "end")
            self.entry_personas.insert(0, "2")
    
    def mostrar_calendario(self):
        
        popup = ctk.CTkToplevel(self)
        popup.title("Seleccionar fecha")
        popup.transient(self)
        popup.grab_set()
        
        # fecha actual
        try:
            fecha_actual = datetime.strptime(self.fecha_seleccionada.get(), '%Y-%m-%d')
        except:
            fecha_actual = datetime.now()
        
        # calendario
        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(fecha_actual.year, fecha_actual.month)
        
        # Encabezados de días
        for i, day in enumerate(["L", "M", "X", "J", "V", "S", "D"]):
            ctk.CTkLabel(popup, text=day).grid(row=0, column=i)
        
        #Días del mes
        for week_num, week in enumerate(month_days, start=1):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = ctk.CTkButton(
                        popup, 
                        text=str(day),
                        width=30,
                        height=30,
                        command=lambda d=day: self.seleccionar_fecha(popup, fecha_actual.year, fecha_actual.month, d)
                    )
                    btn.grid(row=week_num, column=day_num, padx=2, pady=2)
        
        # Botones de navegación
        ctk.CTkButton(
            popup,
            text="< Mes anterior",
            command=lambda: self.cambiar_mes_calendario(popup, fecha_actual.year, fecha_actual.month - 1)
        ).grid(row=8, column=0, columnspan=3, pady=5)
        
        ctk.CTkButton(
            popup,
            text="Mes siguiente >",
            command=lambda: self.cambiar_mes_calendario(popup, fecha_actual.year, fecha_actual.month + 1)
        ).grid(row=8, column=4, columnspan=3, pady=5)
    
    def seleccionar_fecha(self, popup, year, month, day):
        fecha = f"{year}-{month:02d}-{day:02d}"
        self.fecha_seleccionada.set(fecha)
        popup.destroy()
        self.actualizar_disponibilidad()
    
    def cambiar_mes_calendario(self, popup, year, month):
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        
        popup.destroy()
        self.mostrar_calendario()
    
    def actualizar_disponibilidad(self):
        
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        
        fecha = self.fecha_seleccionada.get()
        hora = self.hora_seleccionada.get()
        personas = self.personas.get()
        
        
        mesas_disponibles = self.consultar_mesas_disponibles(fecha, hora, personas)
        
        
        if not mesas_disponibles:
            ctk.CTkLabel(
                self.resultados_frame,
                text=f"No hay mesas disponibles para {personas} personas el {fecha} a las {hora}",
                text_color="red",
                font=("Arial", 14)
            ).pack(pady=20)
            return
        
        
        ctk.CTkLabel(
            self.resultados_frame,
            text=f"Mesas disponibles para {personas} personas el {fecha} a las {hora}:",
            font=("Arial", 14)
        ).pack(pady=(0, 10))
        
        
        table_frame = ctk.CTkFrame(self.resultados_frame)
        table_frame.pack(fill="x", padx=10, pady=5)
        
        
        headers = ["Mesa", "Capacidad", "Ubicación", "Estado"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Arial", 12, "bold")
            ).grid(row=0, column=col, padx=5, pady=2, sticky="w")
        
       
        for row, mesa in enumerate(mesas_disponibles, start=1):
            estado = "Disponible" if mesa["disponible"] else "Reservada"
            color_estado = "green" if mesa["disponible"] else "red"
            
            ctk.CTkLabel(
                table_frame,
                text=mesa["numero_mesa"]
            ).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            ctk.CTkLabel(
                table_frame,
                text=mesa["capacidad"]
            ).grid(row=row, column=1, padx=5, pady=2, sticky="w")
            
            ctk.CTkLabel(
                table_frame,
                text=mesa["ubicacion"]
            ).grid(row=row, column=2, padx=5, pady=2, sticky="w")
            
            ctk.CTkLabel(
                table_frame,
                text=estado,
                text_color=color_estado
            ).grid(row=row, column=3, padx=5, pady=2, sticky="w")
        
        # Estadísticas
        total_mesas = len(mesas_disponibles)
        mesas_disp = sum(1 for m in mesas_disponibles if m["disponible"])
        
        ctk.CTkLabel(
            self.resultados_frame,
            text=f"Total mesas: {total_mesas} | Disponibles: {mesas_disp} | Ocupadas: {total_mesas - mesas_disp}",
            font=("Arial", 12)
        ).pack(pady=(10, 0))
    
    def consultar_mesas_disponibles(self, fecha, hora, personas):
        try:
            db = conectar()
            cursor = db.cursor(dictionary=True)
            
            # Consulta
            query = """
            SELECT 
                m.id_mesa, 
                m.numero_mesa, 
                m.capacidad, 
                m.ubicacion,
                CASE WHEN r.id_reserva IS NULL THEN 1 ELSE 0 END AS disponible
            FROM 
                mesas m
            LEFT JOIN 
                reservas r ON m.id_mesa = r.id_mesa 
                AND r.fecha_reserva = %s 
                AND r.hora_reserva = %s 
                AND r.estado = 'confirmada'
            WHERE 
                m.estado = 'activa'
                AND m.capacidad >= %s
            ORDER BY 
                m.ubicacion, m.capacidad
            """
            
            cursor.execute(query, (fecha, hora, personas))
            mesas = cursor.fetchall()
            
            db.close()
            return mesas
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo consultar la disponibilidad: {str(e)}")
            return []

# Prueba
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Reservas")
        self.geometry("800x600")
        
        def cambiar_pantalla(pantalla):
            print(f"Cambiando a pantalla: {pantalla}")
        
        self.disponibilidad_screen = DisponibilidadScreen(self, cambiar_pantalla)
        self.disponibilidad_screen.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()