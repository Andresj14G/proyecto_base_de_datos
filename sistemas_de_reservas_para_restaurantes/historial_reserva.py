import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, time
from db import conectar
import io

# Configuración de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Variable global para controlar la instancia
ventana_historial_abierta = None

def abrir_historial(parent=None):
    """Función principal para abrir el historial"""
    global ventana_historial_abierta
    
    # Si la ventana ya existe, la traemos al frente
    if ventana_historial_abierta is not None and ventana_historial_abierta.winfo_exists():
        ventana_historial_abierta.lift()
        ventana_historial_abierta.focus_force()
        return
    
    # Si se llama desde el dashboard
    if parent:
        ventana_historial_abierta = HistorialReservas(parent)
    else:
        # Si se ejecuta directamente
        app = ctk.CTk()
        ventana_historial_abierta = HistorialReservas(app)
        app.mainloop()

class HistorialReservas:
    def __init__(self, parent):
        self.parent = parent
        
        # Configurar ventana principal
        if isinstance(parent, ctk.CTk):
            self.ventana = parent
        else:
            self.ventana = ctk.CTkToplevel(parent)
            self.ventana.transient(parent)
        
        self.ventana.title(" Historial de Reservas")
        self.ventana.geometry("1200x800")
        self.ventana.minsize(950, 700)
        
        # Manejar cierre de ventana
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        # Configurar grid principal
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)
        

        
        # Frame superior para filtros
        self.filtros_frame = ctk.CTkFrame(self.ventana, height=80)
        self.filtros_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        self.filtros_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        # Título con icono
        ctk.CTkLabel(self.filtros_frame, 
                    text="  Historial de Reservas", 
                    font=("Arial", 18, "bold"),
                    ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Filtro por cliente
        ctk.CTkLabel(self.filtros_frame, text="Cliente:").grid(row=0, column=1, padx=(20,5), sticky="e")
        self.cliente_entry = ctk.CTkEntry(self.filtros_frame, 
                                        width=200,
                                        placeholder_text="Nombre del cliente...")
        self.cliente_entry.grid(row=0, column=2, padx=5, sticky="w")
        
        # Filtro por fecha
        ctk.CTkLabel(self.filtros_frame, text="Fecha desde:").grid(row=0, column=3, padx=(20,5), sticky="e")
        self.fecha_desde_entry = ctk.CTkEntry(self.filtros_frame, 
                                            width=120,
                                            placeholder_text="AAAA-MM-DD")
        self.fecha_desde_entry.grid(row=0, column=4, padx=5, sticky="w")
        
        ctk.CTkLabel(self.filtros_frame, text="hasta:").grid(row=0, column=5, padx=(0,5), sticky="e")
        self.fecha_hasta_entry = ctk.CTkEntry(self.filtros_frame, 
                                            width=120,
                                            placeholder_text="AAAA-MM-DD")
        self.fecha_hasta_entry.grid(row=0, column=6, padx=5, sticky="w")
        
        # Botones de acción
        self.btn_buscar = ctk.CTkButton(self.filtros_frame, 
                                      text="Buscar", 
                                      command=self.cargar_reservas,
                                      width=100,
                                      fg_color="#4CAF50",
                                      hover_color="#45a049")
        self.btn_buscar.grid(row=0, column=7, padx=(20,10))
        
        self.btn_limpiar = ctk.CTkButton(self.filtros_frame, 
                                       text="Limpiar", 
                                       command=self.limpiar_filtros,
                                       width=100,
                                       fg_color="#f44336",
                                       hover_color="#d32f2f")
        self.btn_limpiar.grid(row=0, column=8, padx=(0,20))
        
        # Frame principal para la tabla
        self.tabla_frame = ctk.CTkFrame(self.ventana)
        self.tabla_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,20))
        self.tabla_frame.grid_columnconfigure(0, weight=1)
        self.tabla_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar estilo de la tabla
        self.configurar_estilo_tabla()
        
        # Definir columnas
        self.columns = {
            'id': {'text': 'ID', 'width': 70, 'anchor': 'center'},
            'cliente': {'text': 'Cliente', 'width': 180, 'anchor': 'w'},
            'fecha': {'text': 'Fecha', 'width': 100, 'anchor': 'center'},
            'hora': {'text': 'Hora', 'width': 80, 'anchor': 'center'},
            'mesa': {'text': 'Mesa', 'width': 70, 'anchor': 'center'},
            'personas': {'text': 'Personas', 'width': 80, 'anchor': 'center'},
            'estado': {'text': 'Estado', 'width': 120, 'anchor': 'center'},
            'telefono': {'text': 'Teléfono', 'width': 120, 'anchor': 'center'},
            'email': {'text': 'Email', 'width': 200, 'anchor': 'w'}
        }
        
        # Crear tabla
        self.crear_tabla()
        
        # Frame inferior para estadísticas
        self.stats_frame = ctk.CTkFrame(self.ventana, height=50)
        self.stats_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,20))
        
        self.total_label = ctk.CTkLabel(self.stats_frame, 
                                      text="Total reservas: 0",
                                      font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=20)
        
        self.filtro_label = ctk.CTkLabel(self.stats_frame, 
                                       text="Filtros aplicados: Ninguno",
                                       font=("Arial", 12))
        self.filtro_label.pack(side="left", padx=20)
        
        # Cargar datos iniciales
        self.cargar_reservas()
        
        # Centrar ventana si es secundaria
        if isinstance(self.ventana, ctk.CTkToplevel):
            self.centrar_ventana()

    def configurar_estilo_tabla(self):
        """Configura el estilo visual de la tabla"""
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview",
                      background="#f8f9fa",
                      foreground="black",
                      rowheight=30,
                      fieldbackground="#f8f9fa",
                      font=('Arial', 11),
                      borderwidth=0)
        
        style.map('Treeview', 
                 background=[('selected', '#0078d7')],
                 foreground=[('selected', 'white')])
        
        style.configure("Treeview.Heading",
                       font=('Arial', 12, 'bold'),
                       background="#e9ecef",
                       foreground="#495057",
                       relief="flat")
        
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def crear_tabla(self):
        """Crea y configura el widget Treeview"""
        self.tabla = ttk.Treeview(self.tabla_frame, 
                                 columns=list(self.columns.keys()), 
                                 show='headings',
                                 selectmode='extended')
        
        # Configurar columnas
        for col, config in self.columns.items():
            self.tabla.heading(col, text=config['text'])
            self.tabla.column(col, width=config['width'], anchor=config['anchor'])
        
        # Scrollbars
        scroll_y = ctk.CTkScrollbar(self.tabla_frame, 
                                   orientation="vertical", 
                                   command=self.tabla.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        
        scroll_x = ctk.CTkScrollbar(self.tabla_frame, 
                                   orientation="horizontal", 
                                   command=self.tabla.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.tabla.configure(yscrollcommand=scroll_y.set,
                           xscrollcommand=scroll_x.set)
        
        self.tabla.grid(row=0, column=0, sticky="nsew")

    def cargar_reservas(self):
        """Carga las reservas desde la base de datos"""
        try:
            filtro_cliente = self.cliente_entry.get().strip()
            fecha_desde = self.fecha_desde_entry.get().strip()
            fecha_hasta = self.fecha_hasta_entry.get().strip()

            query = """
                SELECT 
                    r.id_reserva,
                    c.nombre_completo AS cliente,
                    r.fecha_reserva,
                    r.hora_reserva,
                    r.id_mesa,
                    r.num_personas,
                    r.estado,
                    c.telefono,
                    c.correo_electronico AS email
                FROM reservas r
                JOIN clientes c ON r.id_cliente = c.id_cliente
                WHERE 1=1
            """
            params = []
            filtros = []

            if filtro_cliente:
                query += " AND c.nombre_completo LIKE %s"
                params.append(f"%{filtro_cliente}%")
                filtros.append(f"Cliente: {filtro_cliente}")
            
            if fecha_desde:
                query += " AND r.fecha_reserva >= %s"
                params.append(fecha_desde)
                filtros.append(f"Desde: {fecha_desde}")
            
            if fecha_hasta:
                query += " AND r.fecha_reserva <= %s"
                params.append(fecha_hasta)
                filtros.append(f"Hasta: {fecha_hasta}")

            query += " ORDER BY r.fecha_reserva DESC, r.hora_reserva DESC"

            db = conectar()
            cursor = db.cursor(dictionary=True)
            cursor.execute(query, params)
            reservas = cursor.fetchall()
            db.close()

            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            # Llenar tabla con resultados
            for reserva in reservas:
                hora = reserva['hora_reserva']
                if isinstance(hora, time):
                    hora_formateada = hora.strftime('%H:%M')
                else:
                    hora_formateada = str(hora)[:5]  # Tomar solo HH:MM si es string
                
                self.tabla.insert('', 'end', values=(
                    reserva['id_reserva'],
                    reserva['cliente'],
                    reserva['fecha_reserva'],
                    hora_formateada,
                    reserva['id_mesa'],
                    reserva['num_personas'],
                    reserva['estado'].capitalize(),
                    reserva['telefono'],
                    reserva['email']
                ))

            # Actualizar estadísticas
            self.actualizar_estadisticas(len(reservas), filtros)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{str(e)}")

    def actualizar_estadisticas(self, total, filtros):
        """Actualiza las etiquetas de estadísticas"""
        self.total_label.configure(text=f"Total reservas: {total}")
        
        texto_filtros = "Filtros: " + (', '.join(filtros) if filtros else "Ninguno")
        if len(texto_filtros) > 50:  # Limitar longitud para evitar desbordamiento
            texto_filtros = texto_filtros[:47] + "..."
        self.filtro_label.configure(text=texto_filtros)

    def limpiar_filtros(self):
        """Limpia todos los filtros de búsqueda"""
        self.cliente_entry.delete(0, 'end')
        self.fecha_desde_entry.delete(0, 'end')
        self.fecha_hasta_entry.delete(0, 'end')
        self.cargar_reservas()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f'+{x}+{y}')

    def cerrar_ventana(self):
        """Maneja el cierre correcto de la ventana"""
        global ventana_historial_abierta
        ventana_historial_abierta = None
        self.ventana.destroy()

if __name__ == "__main__":
    abrir_historial()