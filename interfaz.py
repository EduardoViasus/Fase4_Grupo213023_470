"""Interfaz de Software FJ con CustomTkinter."""

import os
import calendar
from datetime import date, datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox


class SelectorCalendario(ctk.CTkToplevel):
    """Ventana emergente de calendario mensual en español."""

    MESES = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]

    def __init__(self, master, al_seleccionar, fecha_actual=None):
        super().__init__(master)
        self.al_seleccionar = al_seleccionar
        hoy = fecha_actual or date.today()
        self.anio = hoy.year
        self.mes = hoy.month
        self.dia_sel = hoy.day

        self.title("Seleccionar fecha")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        self.transient(master)
        self.grab_set()

        x = master.winfo_pointerx() - 120
        y = master.winfo_pointery() + 14
        self.geometry(f"275x295+{max(20, x)}+{max(20, y)}")

        self._construir_ui()

    def _construir_ui(self):
        for w in self.winfo_children():
            w.destroy()

        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkButton(
            nav, text="<", width=30, height=28, fg_color="transparent",
            text_color="#202d40", hover_color="#e2e8f0", command=self._mes_anterior
        ).pack(side="left")

        titulo = f"{self.MESES[self.mes - 1]} de {self.anio}"
        ctk.CTkLabel(
            nav, text=titulo, text_color="#202d40", font=("Segoe UI", 13, "bold")
        ).pack(side="left", expand=True)

        ctk.CTkButton(
            nav, text=">", width=30, height=28, fg_color="transparent",
            text_color="#202d40", hover_color="#e2e8f0", command=self._mes_siguiente
        ).pack(side="right")

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(padx=12, pady=4)

        for col, nombre_dia in enumerate(self.DIAS):
            color = "#dc2626" if col >= 5 else "#64748b"
            ctk.CTkLabel(
                grid, text=nombre_dia, width=33, text_color=color, font=("Segoe UI", 11, "bold")
            ).grid(row=0, column=col, pady=(0, 4))

        semanas = calendar.monthcalendar(self.anio, self.mes)
        for fila_idx, semana in enumerate(semanas, start=1):
            for col_idx, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkLabel(grid, text="", width=33, height=28).grid(row=fila_idx, column=col_idx)
                else:
                    es_sel = (dia == self.dia_sel)
                    fg = "#cbd5e1" if es_sel else "transparent"
                    txt_col = "#dc2626" if col_idx >= 5 else "#202d40"
                    btn = ctk.CTkButton(
                        grid, text=str(dia), width=33, height=28, corner_radius=6,
                        fg_color=fg, hover_color="#e2e8f0", text_color=txt_col,
                        border_width=1 if es_sel else 0, border_color="#2364bb",
                        font=("Segoe UI", 12, "bold" if es_sel else "normal"),
                        command=lambda d=dia: self._elegir(d)
                    )
                    btn.grid(row=fila_idx, column=col_idx, padx=1, pady=1)

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=14, pady=(6, 10))
        ctk.CTkButton(
            pie, text="Hoy", width=70, height=26, fg_color="#f1f5f9",
            text_color="#202d40", hover_color="#e2e8f0", font=("Segoe UI", 11, "bold"),
            command=self._ir_hoy
        ).pack(side="left")
        ctk.CTkButton(
            pie, text="Limpiar", width=75, height=26, fg_color="#f1f5f9",
            text_color="#202d40", hover_color="#e2e8f0", font=("Segoe UI", 11),
            command=self._limpiar
        ).pack(side="right")

    def _mes_anterior(self):
        if self.mes == 1:
            self.mes = 12
            self.anio -= 1
        else:
            self.mes -= 1
        self._construir_ui()

    def _mes_siguiente(self):
        if self.mes == 12:
            self.mes = 1
            self.anio += 1
        else:
            self.mes += 1
        self._construir_ui()

    def _ir_hoy(self):
        hoy = date.today()
        self.anio, self.mes, self.dia_sel = hoy.year, hoy.month, hoy.day
        self._elegir(self.dia_sel)

    def _limpiar(self):
        self.al_seleccionar("")
        self.destroy()

    def _elegir(self, dia):
        fecha_txt = f"{dia:02d}/{self.mes:02d}/{self.anio}"
        self.al_seleccionar(fecha_txt)
        self.destroy()


class SelectorHora(ctk.CTkToplevel):
    """Ventana emergente de selección de hora y minutos con actualización inmediata."""

    def __init__(self, master, al_seleccionar, hora_actual="08:00"):
        super().__init__(master)
        self.al_seleccionar = al_seleccionar
        partes = hora_actual.strip().split(":") if ":" in hora_actual else ["08", "00"]
        self.hora_sel = partes[0].zfill(2) if partes[0].isdigit() else "08"
        self.min_sel = partes[1].zfill(2) if len(partes) > 1 and partes[1].isdigit() else "00"

        self.title("Hora")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        self.transient(master)
        self.grab_set()

        x = master.winfo_pointerx() - 90
        y = master.winfo_pointery() + 14
        self.geometry(f"185x290+{max(20, x)}+{max(20, y)}")

        self.lbl_preview = ctk.CTkLabel(
            self, text=f"{self.hora_sel}:{self.min_sel}",
            text_color="#2364bb", font=("Segoe UI", 16, "bold")
        )
        self.lbl_preview.pack(pady=(8, 0))

        ctk.CTkLabel(
            self, text="Hora   :   Min", text_color="#586b80", font=("Segoe UI", 11, "bold")
        ).pack(pady=(0, 4))

        cols = ctk.CTkFrame(self, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=10)

        self.scroll_h = ctk.CTkScrollableFrame(cols, width=56, height=165, fg_color="#f8fafc")
        self.scroll_h.pack(side="left", fill="y", expand=True, padx=(0, 3))

        self.scroll_m = ctk.CTkScrollableFrame(cols, width=56, height=165, fg_color="#f8fafc")
        self.scroll_m.pack(side="right", fill="y", expand=True, padx=(3, 0))

        self.btns_h = {}
        for h in range(24):
            txt = f"{h:02d}"
            btn = ctk.CTkButton(
                self.scroll_h, text=txt, width=44, height=28, corner_radius=6,
                fg_color="#2364bb" if txt == self.hora_sel else "transparent",
                text_color="#ffffff" if txt == self.hora_sel else "#202d40",
                hover_color="#dbeafe", command=lambda v=txt: self._marcar_hora(v)
            )
            btn.pack(pady=1)
            self.btns_h[txt] = btn

        self.btns_m = {}
        for m in range(0, 60, 5):
            txt = f"{m:02d}"
            btn = ctk.CTkButton(
                self.scroll_m, text=txt, width=44, height=28, corner_radius=6,
                fg_color="#2364bb" if txt == self.min_sel else "transparent",
                text_color="#ffffff" if txt == self.min_sel else "#202d40",
                hover_color="#dbeafe", command=lambda v=txt: self._marcar_min(v)
            )
            btn.pack(pady=1)
            self.btns_m[txt] = btn

        ctk.CTkButton(
            self, text="Aplicar hora", height=32, corner_radius=8,
            fg_color="#2364bb", hover_color="#1c519a", text_color="#ffffff",
            font=("Segoe UI", 12, "bold"), command=self._confirmar
        ).pack(fill="x", padx=12, pady=8)

    def _sincronizar_valor(self):
        valor = f"{self.hora_sel}:{self.min_sel}"
        self.lbl_preview.configure(text=valor)
        self.al_seleccionar(valor)

    def _marcar_hora(self, val):
        self.hora_sel = val
        for k, b in self.btns_h.items():
            b.configure(
                fg_color="#2364bb" if k == val else "transparent",
                text_color="#ffffff" if k == val else "#202d40"
            )
        self._sincronizar_valor()

    def _marcar_min(self, val):
        self.min_sel = val
        for k, b in self.btns_m.items():
            b.configure(
                fg_color="#2364bb" if k == val else "transparent",
                text_color="#ffffff" if k == val else "#202d40"
            )
        self._sincronizar_valor()

    def _confirmar(self):
        self._sincronizar_valor()
        self.grab_release()
        self.destroy()


class Aplicacion(ctk.CTk):
    """Ventana principal para clientes, servicios y reservas."""

    COLOR_SIDEBAR = "#182c46"
    COLOR_SIDEBAR_ACT = "#244a6b"
    COLOR_SIDEBAR_HOV = "#233f5f"
    COLOR_BG = "#f5f8fb"
    COLOR_CARD = "#ffffff"
    COLOR_BORDER = "#dde6ee"
    COLOR_PRIMARY = "#2364bb"
    COLOR_PRIMARY_HOV = "#1c519a"
    COLOR_GREEN = "#19775f"
    COLOR_GREEN_HOV = "#14614d"
    COLOR_DANGER = "#b91c1c"
    COLOR_DANGER_HOV = "#991b1b"
    COLOR_TEXT = "#202d40"
    COLOR_MUTED = "#586b80"

    SUGERENCIAS_SERVICIO = {
        "Sala": ["Sala de reuniones", "Sala de juntas", "Auditorio principal", "Sala de capacitación"],
        "Equipo": ["Kit audiovisual", "Proyector HD + pantalla", "Portátil corporativo", "Sistema de sonido"],
        "Asesoría": ["Asesoría en programación", "Consultoría UX/UI", "Soporte técnico", "Mentoría de proyectos"],
    }

    CAPACIDADES_SALA = ["4", "8", "10", "15", "20", "30", "50", "100", "200", "500"]

    def __init__(self, sistema):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        super().__init__()

        self.sistema = sistema
        self.vista_actual = "Clientes"

        self.title("Software FJ | Gestión de clientes, servicios y reservas")
        self.geometry("1240x820")
        self.minsize(1040, 720)
        self.configure(fg_color=self.COLOR_BG)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_sidebar()
        self._construir_area_principal()
        self._actualizar_vistas()
        
    def _construir_sidebar(self):
        """Crea el menú lateral fijo con la marca y los botones de navegación."""
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(26, 24))
        brand_text = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text.pack(side="left")
        ctk.CTkLabel(
            brand_text, text="Software FJ", text_color="#ffffff",
            font=("Segoe UI", 17, "bold"), anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            sidebar, text="Menú", text_color="#aebfd5",
            font=("Segoe UI", 10, "bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(4, 8))

        self.botones_nav = {}
        opciones = [
            ("Clientes", "Clientes"),
            ("Servicios", "Servicios"),
            ("Reservas", "Reservas"),
            ("Logs", "Registro de actividad"),
        ]
        for clave, etiqueta in opciones:
            btn = ctk.CTkButton(
                sidebar, text=f"  {etiqueta}", anchor="w", height=42, corner_radius=8,
                fg_color="transparent", hover_color=self.COLOR_SIDEBAR_HOV,
                text_color="#c4d2e3", font=("Segoe UI", 13, "bold"),
                command=lambda c=clave: self._cambiar_vista(c)
            )
            btn.pack(fill="x", padx=14, pady=3)
            self.botones_nav[clave] = btn

    def _construir_area_principal(self):
        """Crea el contenedor de las pantallas."""
        contenedor = ctk.CTkFrame(self, fg_color=self.COLOR_BG, corner_radius=0)
        contenedor.grid(row=0, column=1, sticky="nsew")
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_rowconfigure(0, weight=1)

        self.cuerpo = ctk.CTkFrame(contenedor, fg_color="transparent")
        self.cuerpo.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.cuerpo.grid_rowconfigure(0, weight=1)

        self.vistas = {}
        self._crear_vista_clientes()
        self._crear_vista_servicios()
        self._crear_vista_reservas()
        self._crear_vista_logs()
        self._cambiar_vista("Clientes")

    def _cambiar_vista(self, nombre):
        """Muestra la vista seleccionada y resalta su botón en el menú lateral."""
        self.vista_actual = nombre

        for clave, frame in self.vistas.items():
            if clave == nombre:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

        for clave, btn in self.botones_nav.items():
            if clave == nombre:
                btn.configure(fg_color=self.COLOR_SIDEBAR_ACT, text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#c4d2e3")

        if nombre == "Logs":
            self._refrescar_logs()

    def _crear_tarjeta(self, padre, titulo):
        """Crea una tarjeta blanca con encabezado y borde sutil."""
        card = ctk.CTkFrame(
            padre, fg_color=self.COLOR_CARD, corner_radius=8,
            border_width=1, border_color=self.COLOR_BORDER
        )
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 10))

        ctk.CTkLabel(
            header, text=titulo, text_color=self.COLOR_TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=self.COLOR_BORDER).pack(fill="x")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)
        return card, body

    def _entrada(self, contenedor, etiqueta, ejemplo="", inicial=None):
        """Crea una etiqueta y un campo de entrada."""
        ctk.CTkLabel(
            contenedor, text=etiqueta, text_color=self.COLOR_TEXT,
            font=("Segoe UI", 12, "bold"), anchor="w"
        ).pack(fill="x", pady=(8, 3))
        entrada = ctk.CTkEntry(
            contenedor, placeholder_text=ejemplo, height=38, corner_radius=8,
            border_color="#b8c7d6", fg_color="#ffffff", text_color=self.COLOR_TEXT
        )
        entrada.pack(fill="x", pady=(0, 4))
        if inicial is not None:
            entrada.insert(0, inicial)
        return entrada

    def _selector(self, contenedor, etiqueta, valores, comando=None, editable=False):
        """Crea una etiqueta y un desplegable de solo lectura o editable."""
        ctk.CTkLabel(
            contenedor, text=etiqueta, text_color=self.COLOR_TEXT,
            font=("Segoe UI", 12, "bold"), anchor="w"
        ).pack(fill="x", pady=(8, 3))
        selector = ctk.CTkComboBox(
            contenedor, values=valores, state="normal" if editable else "readonly",
            height=38, corner_radius=8, border_color="#b8c7d6",
            button_color="#e2e8f0", button_hover_color="#cbd5e1",
            fg_color="#ffffff", text_color=self.COLOR_TEXT, command=comando
        )
        selector.pack(fill="x", pady=(0, 4))
        selector.set(valores[0])
        return selector

    def _fila_fecha_hora(self, contenedor, al_cambiar=None):
        """Crea una fila de 2 columnas con selector de fecha (calendario) y hora de inicio."""
        ahora = datetime.now()
        siguiente = ahora.replace(second=0, microsecond=0) + timedelta(minutes=5 - ahora.minute % 5)
        fila = ctk.CTkFrame(contenedor, fg_color="transparent")
        fila.pack(fill="x", pady=(8, 4))
        fila.grid_columnconfigure(0, weight=1)
        fila.grid_columnconfigure(1, weight=1)

        col_f = ctk.CTkFrame(fila, fg_color="transparent")
        col_f.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(
            col_f, text="Fecha de reserva", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 12, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 3))

        box_f = ctk.CTkFrame(col_f, fg_color="transparent")
        box_f.pack(fill="x")
        ent_fecha = ctk.CTkEntry(
            box_f, placeholder_text="dd/mm/aaaa", height=38, corner_radius=8,
            border_color="#b8c7d6", fg_color="#ffffff", text_color=self.COLOR_TEXT
        )
        ent_fecha.insert(0, siguiente.strftime("%d/%m/%Y"))
        ent_fecha.pack(side="left", fill="x", expand=True, padx=(0, 4))

        def notificar_cambio(evento=None):
            if al_cambiar is not None:
                al_cambiar()

        def poner_fecha(valor):
            ent_fecha.delete(0, "end")
            ent_fecha.insert(0, valor)
            notificar_cambio()

        def abrir_cal():
            try:
                seleccionada = datetime.strptime(ent_fecha.get(), "%d/%m/%Y").date()
            except ValueError:
                seleccionada = None
            SelectorCalendario(self, poner_fecha, seleccionada)

        ctk.CTkButton(
            box_f, text="...", width=32, height=38, corner_radius=8,
            fg_color="#e2e8f0", hover_color="#cbd5e1", text_color=self.COLOR_TEXT,
            command=abrir_cal
        ).pack(side="right")

        col_h = ctk.CTkFrame(fila, fg_color="transparent")
        col_h.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            col_h, text="Hora de inicio", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 12, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, 3))

        box_h = ctk.CTkFrame(col_h, fg_color="transparent")
        box_h.pack(fill="x")
        ent_hora = ctk.CTkEntry(
            box_h, placeholder_text="HH:MM", height=38, corner_radius=8,
            border_color="#b8c7d6", fg_color="#ffffff", text_color=self.COLOR_TEXT
        )
        ent_hora.insert(0, siguiente.strftime("%H:%M"))
        ent_hora.pack(side="left", fill="x", expand=True, padx=(0, 4))

        def poner_hora(val):
            ent_hora.delete(0, "end")
            ent_hora.insert(0, val)
            notificar_cambio()

        def abrir_reloj():
            SelectorHora(self, poner_hora, ent_hora.get())

        ctk.CTkButton(
            box_h, text="...", width=32, height=38, corner_radius=8,
            fg_color="#e2e8f0", hover_color="#cbd5e1", text_color=self.COLOR_TEXT,
            command=abrir_reloj
        ).pack(side="right")

        for campo in (ent_fecha, ent_hora):
            campo.bind("<KeyRelease>", notificar_cambio)
            campo.bind("<FocusOut>", notificar_cambio)
        return ent_fecha, ent_hora

    def _boton(self, contenedor, texto, comando, variante="primary"):
        """Crea un botón según la variante de color indicada."""
        estilos = {
            "primary": (self.COLOR_PRIMARY, self.COLOR_PRIMARY_HOV, "#ffffff"),
            "success": (self.COLOR_GREEN, self.COLOR_GREEN_HOV, "#ffffff"),
            "danger": (self.COLOR_DANGER, self.COLOR_DANGER_HOV, "#ffffff"),
            "neutral": ("#e2e8f0", "#cbd5e1", self.COLOR_TEXT),
        }
        fg, hov, txt = estilos.get(variante, estilos["primary"])
        btn = ctk.CTkButton(
            contenedor, text=texto, command=comando, height=40, corner_radius=8,
            fg_color=fg, hover_color=hov, text_color=txt, font=("Segoe UI", 13, "bold")
        )
        btn.pack(fill="x", pady=(12, 0))
        return btn

    def _crear_vista_clientes(self):
        """Construye la pantalla de registro y listado de clientes."""
        vista = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=0)
        vista.grid_columnconfigure(1, weight=1)
        vista.grid_rowconfigure(1, weight=1)
        self.vistas["Clientes"] = vista

        head = ctk.CTkFrame(vista, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        ctk.CTkLabel(head, text="Clientes", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_TEXT).pack(anchor="w")

        card_form, body_form = self._crear_tarjeta(vista, "Nuevo cliente")
        card_form.configure(width=360)
        card_form.grid(row=1, column=0, sticky="nsew", padx=(0, 18))
        card_form.grid_propagate(False)

        self.campos_cliente = {
            "identificador": self._entrada(body_form, "Identificador", "C001"),
            "nombre": self._entrada(body_form, "Nombre completo", "Ana Pérez"),
            "correo": self._entrada(body_form, "Correo electrónico", "ana@ejemplo.com"),
            "telefono": self._entrada(body_form, "Teléfono (sin espacios)", "3001234567"),
        }
        self._boton(body_form, "Registrar cliente", self._registrar_cliente, "primary")

        card_list, body_list = self._crear_tarjeta(vista, "Clientes registrados")
        card_list.grid(row=1, column=1, sticky="nsew")
        self.lista_clientes = ctk.CTkScrollableFrame(body_list, fg_color="transparent")
        self.lista_clientes.pack(fill="both", expand=True)

    def _crear_vista_servicios(self):
        """Construye los formularios de servicios y cotización."""
        vista = ctk.CTkScrollableFrame(self.cuerpo, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_columnconfigure(1, weight=1)
        self.vistas["Servicios"] = vista

        head = ctk.CTkFrame(vista, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        ctk.CTkLabel(head, text="Servicios", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_TEXT).pack(anchor="w")

        card_srv, body_srv = self._crear_tarjeta(vista, "Nuevo servicio")
        card_srv.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.tipo_servicio = self._selector(
            body_srv, "Tipo de servicio", ["Sala", "Equipo", "Asesoría"], self._mostrar_tipo
        )
        self.campos_servicio = {
            "identificador": self._entrada(body_srv, "Identificador", "S001"),
            "nombre": self._selector(
                body_srv, "Nombre del servicio",
                self.SUGERENCIAS_SERVICIO["Sala"], editable=True
            ),
        }

        self.etiqueta_tarifa = ctk.CTkLabel(
            body_srv, text="Tarifa por hora (COP)", text_color=self.COLOR_TEXT,
            font=("Segoe UI", 12, "bold"), anchor="w"
        )
        self.etiqueta_tarifa.pack(fill="x", pady=(8, 3))
        tarifa = ctk.CTkEntry(
            body_srv, placeholder_text="50000", height=38, corner_radius=8,
            border_color="#b8c7d6", fg_color="#ffffff", text_color=self.COLOR_TEXT
        )
        tarifa.pack(fill="x", pady=(0, 4))
        self.campos_servicio["tarifa"] = tarifa

        contenedor = ctk.CTkFrame(
            body_srv, fg_color="#f8fafc", corner_radius=10,
            border_width=1, border_color="#cbd5e1"
        )
        contenedor.pack(fill="x", pady=10)

        self.parametros_tipo = {tipo: ctk.CTkFrame(contenedor, fg_color="transparent") for tipo in ("Sala", "Equipo", "Asesoría")}

        sala = self.parametros_tipo["Sala"]
        self.capacidad_sala = self._selector(
            sala, "Capacidad de personas (1 a 500)", self.CAPACIDADES_SALA, editable=True
        )
        self.capacidad_sala.set("10")

        equipo = self.parametros_tipo["Equipo"]
        self.unidad_equipo = self._selector(
            equipo, "Unidad de cobro", ["días", "horas"], lambda _: self._actualizar_etiqueta_tarifa()
        )
        self.cantidad_equipo = self._entrada(equipo, "Cantidad de equipos (1 a 100)", "1", "1")
        self.deposito_equipo = self._entrada(equipo, "Depósito único (0 para omitir)", "50000", "50000")
        ctk.CTkLabel(
            equipo, text="El depósito se cobra una vez por el conjunto, antes de aplicar descuento e impuesto.",
            wraplength=360, justify="left", text_color=self.COLOR_MUTED, font=("Segoe UI", 11)
        ).pack(fill="x", pady=6)

        asesoria = self.parametros_tipo["Asesoría"]
        self.especialista_asesoria = self._entrada(asesoria, "Especialista", "Ing. Daniela")
        self.especialidad_asesoria = self._entrada(asesoria, "Especialidad", "Programación")
        self.preparacion_asesoria = self._selector(asesoria, "Horas extra de preparación", ["0", "0.5"])

        self._mostrar_tipo("Sala")
        self._boton(body_srv, "Registrar servicio", self._registrar_servicio, "primary")

        card_cot, body_cot = self._crear_tarjeta(vista, "Cotización")
        card_cot.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

        self.servicio_cotizacion = self._selector(
            body_cot, "Servicio para consultar", ["Sin registros"], lambda _: self._actualizar_unidades()
        )
        self.aviso_cotizacion = ctk.CTkLabel(
            body_cot, text="Selecciona un servicio.", text_color=self.COLOR_PRIMARY,
            font=("Segoe UI", 12, "bold"), anchor="w"
        )
        self.aviso_cotizacion.pack(fill="x", pady=(4, 4))

        self.horas_cotizacion = self._entrada(body_cot, "Duración (en la unidad indicada)", "2", "2")
        self.impuesto_cotizacion = self._entrada(body_cot, "Impuesto (%)", "0 a 100", "0")
        self.descuento_cotizacion = self._entrada(body_cot, "Descuento (%)", "0 a 100", "0")

        resumen_cot = ctk.CTkFrame(body_cot, fg_color="transparent")
        resumen_cot.pack(fill="x", pady=(14, 4))
        ctk.CTkLabel(resumen_cot, text="Total:", text_color=self.COLOR_MUTED, font=("Segoe UI", 12)).pack(side="left", pady=12)
        self.lbl_resultado_cot = ctk.CTkLabel(resumen_cot, text="$0.00", text_color=self.COLOR_PRIMARY, font=("Segoe UI", 16, "bold"))
        self.lbl_resultado_cot.pack(side="right", padx=14, pady=12)

        self._boton(body_cot, "Cotizar y preparar reserva", self._cotizar_y_pasar, "primary")

        card_list, body_list = self._crear_tarjeta(vista, "Servicios registrados")
        card_list.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        self.lista_servicios = ctk.CTkFrame(body_list, fg_color="transparent")
        self.lista_servicios.pack(fill="both", expand=True)

    def _mostrar_tipo(self, tipo):
        """Muestra únicamente los campos de la subclase de servicio elegida y actualiza opciones."""
        for panel in self.parametros_tipo.values():
            panel.pack_forget()
        self.parametros_tipo[tipo].pack(fill="x", padx=12, pady=10)

        if hasattr(self, "campos_servicio") and "nombre" in self.campos_servicio:
            sugerencias = self.SUGERENCIAS_SERVICIO.get(tipo, ["Servicio general"])
            self.campos_servicio["nombre"].configure(values=sugerencias)
            self.campos_servicio["nombre"].set(sugerencias[0])

        self._actualizar_etiqueta_tarifa()

    def _actualizar_etiqueta_tarifa(self):
        """Actualiza la etiqueta de tarifa según la unidad de cobro del servicio."""
        texto = "Tarifa por hora (COP)"
        if self.tipo_servicio.get() == "Equipo":
            unidad = "día" if self.unidad_equipo.get() == "días" else "hora"
            texto = f"Tarifa por unidad y {unidad} (COP)"
        self.etiqueta_tarifa.configure(text=texto)

    def _crear_vista_reservas(self):
        """Construye los formularios y el listado de reservas."""
        vista = ctk.CTkScrollableFrame(self.cuerpo, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_columnconfigure(1, weight=1)
        self.vistas["Reservas"] = vista

        head = ctk.CTkFrame(vista, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        ctk.CTkLabel(head, text="Reservas", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_TEXT).pack(anchor="w")

        card_new, body_new = self._crear_tarjeta(vista, "Nueva reserva")
        card_new.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.cliente_reserva = self._selector(body_new, "Cliente", ["Sin registros"])
        self.servicio_reserva = self._selector(
            body_new, "Servicio", ["Sin registros"], lambda _: self._actualizar_unidades()
        )
        self.aviso_reserva = ctk.CTkLabel(
            body_new, text="Selecciona un servicio.", text_color=self.COLOR_PRIMARY,
            font=("Segoe UI", 12, "bold"), anchor="w"
        )
        self.aviso_reserva.pack(fill="x", pady=(4, 4))

        self.fecha_reserva, self.hora_reserva = self._fila_fecha_hora(body_new, self._invalidar_disponibilidad)

        self.horas_reserva = self._entrada(body_new, "Duración", "2", "2")
        self.horas_reserva.bind("<KeyRelease>", self._invalidar_disponibilidad)
        self.horas_reserva.bind("<FocusOut>", self._invalidar_disponibilidad)
        self.impuesto_reserva = self._entrada(body_new, "Impuesto (%)", "0 a 100", "0")
        self.descuento_reserva = self._entrada(body_new, "Descuento (%)", "0 a 100", "0")
        self.aviso_disponibilidad = ctk.CTkLabel(
            body_new, text="Consulta la disponibilidad para este horario.",
            text_color=self.COLOR_MUTED, wraplength=340, justify="left", anchor="w",
        )
        self.aviso_disponibilidad.pack(fill="x", pady=(10, 0))
        self._boton(body_new, "Consultar disponibilidad", self._consultar_disponibilidad, "neutral")
        self.btn_crear_reserva = self._boton(body_new, "Crear reserva", self._crear_reserva, "primary")

        card_ges, body_ges = self._crear_tarjeta(vista, "Gestionar reserva")
        card_ges.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

        self.reserva_elegida = self._selector(
            body_ges, "Reserva", ["Sin registros"],
            lambda _: self._actualizar_botones_reserva()
        )

        self.lbl_estado_actual = ctk.CTkLabel(
            body_ges, text="Estado actual: Sin registros",
            text_color=self.COLOR_TEXT, font=("Segoe UI", 13, "bold"), anchor="w"
        )
        self.lbl_estado_actual.pack(fill="x", pady=(10, 4))

        self.lbl_horario_reserva = ctk.CTkLabel(
            body_ges, text="", text_color=self.COLOR_MUTED,
            wraplength=340, justify="left", anchor="w",
        )
        self.lbl_horario_reserva.pack(fill="x", pady=8)
        self.btn_finalizar_reserva = self._boton(
            body_ges, "Finalizar reserva", lambda: self._gestionar_reserva("Finalizar"), "success"
        )
        self.btn_cancelar_reserva = self._boton(
            body_ges, "Cancelar reserva", lambda: self._gestionar_reserva("Cancelar"), "danger"
        )

        card_list, body_list = self._crear_tarjeta(vista, "Historial de reservas")
        card_list.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        self.lista_reservas = ctk.CTkFrame(body_list, fg_color="transparent")
        self.lista_reservas.pack(fill="both", expand=True)

    def _crear_vista_logs(self):
        """Construye un visor en vivo para el archivo de logs del sistema."""
        vista = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(1, weight=1)
        self.vistas["Logs"] = vista

        head = ctk.CTkFrame(vista, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ctk.CTkLabel(head, text="Registro de actividad", font=("Segoe UI", 22, "bold"), text_color=self.COLOR_TEXT).pack(side="left")
        ctk.CTkButton(
            head, text="Actualizar", command=self._refrescar_logs,
            fg_color=self.COLOR_PRIMARY, hover_color=self.COLOR_PRIMARY_HOV, height=36, corner_radius=8
        ).pack(side="right")

        card_log, body_log = self._crear_tarjeta(vista, f"Archivo activo: {os.path.basename(str(self.sistema.ruta_log))}")
        card_log.grid(row=1, column=0, sticky="nsew")

        self.caja_logs = ctk.CTkTextbox(
            body_log, fg_color="#0f172a", text_color="#e2e8f0",
            font=("Consolas", 12), corner_radius=10, wrap="word"
        )
        self.caja_logs.pack(fill="both", expand=True)
        self.caja_logs.configure(state="disabled")

    def _refrescar_logs(self):
        """Lee el archivo de logs y muestra su contenido en el visor."""
        self.caja_logs.configure(state="normal")
        self.caja_logs.delete("1.0", "end")
        ruta = str(self.sistema.ruta_log)
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8", errors="replace") as archivo:
                contenido = archivo.read().strip()
            self.caja_logs.insert("1.0", contenido or "El archivo de logs aún no tiene eventos registrados.")
        else:
            self.caja_logs.insert("1.0", "No se encontró el archivo de logs en la ruta configurada.")
        self.caja_logs.see("end")
        self.caja_logs.configure(state="disabled")

    def _realizar(self, descripcion, accion):
        """Ejecuta una operación controlada por sistema.ejecutar y actualiza la vista."""
        correcto, resultado = self.sistema.ejecutar(descripcion, accion)
        self._actualizar_vistas()
        if not correcto:
            messagebox.showerror(descripcion, str(resultado), parent=self)
        return correcto, resultado

    def _registrar_cliente(self):
        """Captura los datos del formulario y registra un nuevo cliente."""
        correcto, _ = self._realizar("Registrar cliente", lambda: self.sistema.registrar_cliente(
            **{nombre: campo.get() for nombre, campo in self.campos_cliente.items()}
        ))
        if correcto:
            for campo in self.campos_cliente.values():
                campo.delete(0, "end")

    def _registrar_servicio(self):
        """Valida y registra el servicio según la subclase elegida."""
        correcto, _ = self._realizar("Registrar servicio", self._guardar_servicio)
        if correcto:
            self.campos_servicio["identificador"].delete(0, "end")
            self.campos_servicio["tarifa"].delete(0, "end")

    def _guardar_servicio(self):
        """Invoca el método de registro correspondiente al tipo de servicio."""
        datos = {nombre: campo.get() for nombre, campo in self.campos_servicio.items()}
        tipo = self.tipo_servicio.get()
        if tipo == "Sala":
            return self.sistema.registrar_servicio(**datos, capacidad=self.capacidad_sala.get())
        if tipo == "Equipo":
            return self.sistema.registrar_equipo(
                **datos, deposito_garantia=self.deposito_equipo.get(),
                cantidad=self.cantidad_equipo.get(), unidad=self.unidad_equipo.get(),
            )
        return self.sistema.registrar_asesoria(
            **datos, especialista=self.especialista_asesoria.get(),
            especialidad=self.especialidad_asesoria.get(), horas_preparacion=self.preparacion_asesoria.get(),
        )

    def _id_seleccionado(self, selector):
        """Extrae el identificador del elemento seleccionado en un ComboBox."""
        if selector.get() == "Sin registros":
            return ""
        return selector.get().split(" | ", 1)[0]

    def _cotizar_y_pasar(self):
        """Calcula el costo y precarga servicio, duración, impuesto y descuento en Reservas."""
        duracion = self.horas_cotizacion.get()
        impuesto = self.impuesto_cotizacion.get()
        descuento = self.descuento_cotizacion.get()
        srv_texto = self.servicio_cotizacion.get()

        correcto, total = self._realizar("Consultar costo", lambda: self.sistema.cotizar(
            self._id_seleccionado(self.servicio_cotizacion), duracion, impuesto, descuento,
        ))
        if correcto:
            self.lbl_resultado_cot.configure(text=f"${total:,.2f} COP")

            if srv_texto != "Sin registros":
                self.servicio_reserva.set(srv_texto)
            self.horas_reserva.delete(0, "end")
            self.horas_reserva.insert(0, duracion)
            self.impuesto_reserva.delete(0, "end")
            self.impuesto_reserva.insert(0, impuesto)
            self.descuento_reserva.delete(0, "end")
            self.descuento_reserva.insert(0, descuento)
            self._actualizar_unidades()

            messagebox.showinfo(
                "Cotización",
                f"Total: ${total:,.2f} COP\n\nLos datos se copiaron al formulario de reservas.",
                parent=self
            )

    def _crear_reserva(self):
        """Registra el horario, comprueba cruces y crea una reserva activa."""
        fecha = self.fecha_reserva.get().strip()
        hora = self.hora_reserva.get().strip()
        correcto, reserva = self._realizar("Crear reserva", lambda: self.sistema.crear_reserva(
            self._id_seleccionado(self.cliente_reserva), self._id_seleccionado(self.servicio_reserva),
            self.horas_reserva.get(), fecha=fecha, hora=hora,
            impuesto=self.impuesto_reserva.get(), descuento=self.descuento_reserva.get(),
        ))
        if correcto:
            self.reserva_elegida.set(f"{reserva.identificador} | {reserva.estado}")
            self._actualizar_botones_reserva()
            self.aviso_disponibilidad.configure(
                text=f"Horario reservado: {reserva.inicio:%d/%m/%Y %H:%M} a {reserva.fin:%d/%m/%Y %H:%M}.",
                text_color=self.COLOR_DANGER,
            )
            self.btn_crear_reserva.configure(state="disabled")

    def _invalidar_disponibilidad(self, evento=None):
        """Una consulta anterior deja de ser válida al cambiar el horario."""
        self.aviso_disponibilidad.configure(
            text="Consulta la disponibilidad para este horario.", text_color=self.COLOR_MUTED
        )
        self.btn_crear_reserva.configure(state="normal")

    def _consultar_disponibilidad(self):
        correcto, disponible = self._realizar(
            "Consultar disponibilidad", lambda: self.sistema.consultar_disponibilidad(
                self._id_seleccionado(self.servicio_reserva), self.fecha_reserva.get(),
                self.hora_reserva.get(), self.horas_reserva.get(),
            )
        )
        if correcto:
            self.aviso_disponibilidad.configure(
                text="Disponible para el horario indicado." if disponible else "Ocupado durante el horario indicado.",
                text_color=self.COLOR_GREEN if disponible else self.COLOR_DANGER,
            )
            self.btn_crear_reserva.configure(state="normal" if disponible else "disabled")

    def _gestionar_reserva(self, accion):
        """Finaliza o cancela la reserva seleccionada."""
        if accion == "Finalizar":
            identificador = self._id_seleccionado(self.reserva_elegida)
            reserva = next((r for r in self.sistema.reservas if r.identificador == identificador), None)
            if reserva is not None and reserva.estado == "ACTIVA" and datetime.now() < reserva.fin:
                self._solicitar_finalizacion_anticipada(reserva)
                return
        self._realizar(f"{accion} reserva", lambda: {
            "Finalizar": self.sistema.finalizar_reserva,
            "Cancelar": self.sistema.cancelar_reserva,
        }[accion](self._id_seleccionado(self.reserva_elegida)))

    def _solicitar_finalizacion_anticipada(self, reserva):
        ventana = ctk.CTkToplevel(self)
        ventana.title(f"Finalizar reserva {reserva.identificador}")
        ventana.geometry("460x330")
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text=f"Fin pactado: {reserva.fin:%d/%m/%Y %H:%M}\n"
            "Indica por qué finaliza antes de la hora acordada.",
            wraplength=410, justify="left", anchor="w",
        ).pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(
            ventana, text="Observación obligatoria (máximo 500 caracteres)", anchor="w"
        ).pack(fill="x", padx=20, pady=(4, 6))
        observacion = ctk.CTkTextbox(ventana, height=110, wrap="word")
        observacion.pack(fill="x", padx=20)
        aviso = ctk.CTkLabel(ventana, text="", text_color=self.COLOR_DANGER, anchor="w")
        aviso.pack(fill="x", padx=20, pady=(4, 0))

        def guardar():
            texto = observacion.get("1.0", "end").strip()
            if not texto:
                aviso.configure(text="Escribe la razón de la finalización anticipada.")
                self.sistema.logger.error(
                    "Intento de finalizar anticipadamente la reserva %s sin observación.",
                    reserva.identificador,
                )
                observacion.focus_set()
                return
            correcto, _ = self._realizar(
                "Finalizar reserva", lambda: self.sistema.finalizar_reserva(
                    reserva.identificador, observacion=texto,
                )
            )
            if correcto:
                ventana.destroy()

        botones = ctk.CTkFrame(ventana, fg_color="transparent")
        botones.pack(fill="x", padx=20, pady=(12, 18))
        ctk.CTkButton(
            botones, text="Cancelar", width=130, command=ventana.destroy,
            fg_color="#e2e8f0", hover_color="#cbd5e1", text_color=self.COLOR_TEXT,
        ).pack(side="left")
        ctk.CTkButton(
            botones, text="Finalizar", width=130, command=guardar,
            fg_color=self.COLOR_GREEN, hover_color=self.COLOR_GREEN_HOV,
        ).pack(side="right")
        observacion.focus_set()

    def _actualizar_botones_reserva(self):
        """Las reservas activas se pueden finalizar o cancelar."""
        identificador = self._id_seleccionado(self.reserva_elegida)
        reserva = next((r for r in self.sistema.reservas if r.identificador == identificador), None)
        if reserva is None:
            self.lbl_estado_actual.configure(text="Estado actual: Sin registros")
            self.lbl_horario_reserva.configure(text="")
            self.btn_finalizar_reserva.configure(state="disabled")
            self.btn_cancelar_reserva.configure(state="disabled")
            return
        activa = reserva.estado == "ACTIVA"
        self.lbl_estado_actual.configure(text=f"Estado actual: {reserva.estado}")
        horario = f"Inicio: {reserva.inicio:%d/%m/%Y %H:%M}\nFin pactado: {reserva.fin:%d/%m/%Y %H:%M}"
        if reserva.fecha_finalizacion is not None:
            horario += f"\nFin real: {reserva.fecha_finalizacion:%d/%m/%Y %H:%M:%S}"
            if reserva.observacion_finalizacion:
                horario += f"\nObservación: {reserva.observacion_finalizacion}"
        self.lbl_horario_reserva.configure(text=horario)
        self.btn_finalizar_reserva.configure(state="normal" if activa else "disabled")
        self.btn_cancelar_reserva.configure(state="normal" if activa else "disabled")

    def _renderizar_tarjetas_lista(self, contenedor, items, construir_fila):
        """Pinta una tarjeta por cada registro o un mensaje vacío si no hay datos."""
        for widget in contenedor.winfo_children():
            widget.destroy()

        if not items:
            ctk.CTkLabel(
                contenedor, text="Sin registros.",
                text_color=self.COLOR_MUTED, font=("Segoe UI", 13)
            ).pack(pady=28)
            return

        for item in items:
            fila = ctk.CTkFrame(
                contenedor, fg_color="#f8fafc", corner_radius=10,
                border_width=1, border_color=self.COLOR_BORDER
            )
            fila.pack(fill="x", pady=5)
            construir_fila(fila, item)

    def _actualizar_selector(self, selector, valores):
        """Actualiza los valores de un desplegable conservando la selección previa."""
        anterior = selector.get().split(" | ", 1)[0]
        valores = valores or ["Sin registros"]
        selector.configure(values=valores)
        elegido = next((valor for valor in valores if valor.split(" | ", 1)[0] == anterior), valores[0])
        selector.set(elegido)

    def _actualizar_vistas(self):
        """Sincroniza todas las listas y selectores con el estado actual del sistema."""
        clientes = self.sistema.clientes
        servicios = self.sistema.servicios
        reservas = self.sistema.reservas

        self._renderizar_tarjetas_lista(self.lista_clientes, clientes, lambda fila, c: (
            ctk.CTkLabel(fila, text=c.describir(), text_color=self.COLOR_TEXT, font=("Segoe UI", 13), justify="left", anchor="w").pack(fill="x", padx=16, pady=12)
        ))

        def pintar_servicio(fila, s):
            etiqueta = ctk.CTkLabel(fila, text=s.describir(), text_color=self.COLOR_TEXT, font=("Segoe UI", 13), justify="left", anchor="w")
            etiqueta.pack(fill="x", padx=16, pady=(12, 4))
            fila.bind("<Configure>", lambda evento: etiqueta.configure(wraplength=max(160, evento.width - 32)))
            activas = sum(r.estado == "ACTIVA" and r.servicio.identificador == s.identificador for r in reservas)
            ctk.CTkLabel(fila, text=f"Reservas activas: {activas}", text_color=self.COLOR_MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=16, pady=(0, 12))

        self._renderizar_tarjetas_lista(self.lista_servicios, servicios, pintar_servicio)

        def pintar_reserva(fila, r):
            etiqueta = ctk.CTkLabel(fila, text=r.describir(), text_color=self.COLOR_TEXT, font=("Segoe UI", 13), justify="left", anchor="w")
            etiqueta.pack(fill="x", padx=16, pady=12)
            fila.bind("<Configure>", lambda evento: etiqueta.configure(wraplength=max(160, evento.width - 32)))

        self._renderizar_tarjetas_lista(self.lista_reservas, reservas, pintar_reserva)

        opciones_srv = [f"{s.identificador} | {s.nombre} | {s.unidad_duracion}" for s in servicios]
        self._actualizar_selector(self.servicio_cotizacion, opciones_srv)
        self._actualizar_selector(self.servicio_reserva, opciones_srv)
        self._actualizar_selector(self.cliente_reserva, [f"{c.identificador} | {c.nombre}" for c in clientes])
        self._actualizar_selector(self.reserva_elegida, [f"{r.identificador} | {r.estado}" for r in reservas])
        self._actualizar_unidades()
        self._actualizar_botones_reserva()

        if self.vista_actual == "Logs":
            self._refrescar_logs()

    def _actualizar_unidades(self):
        """Muestra la unidad de cobro y el rango permitido del servicio seleccionado."""
        for selector, aviso in ((self.servicio_cotizacion, self.aviso_cotizacion),
                                (self.servicio_reserva, self.aviso_reserva)):
            identificador = self._id_seleccionado(selector)
            servicio = next((s for s in self.sistema.servicios if s.identificador == identificador), None)
            if servicio is None:
                aviso.configure(text="Registra y selecciona un servicio.")
            else:
                minimo, maximo = servicio.rango_duracion
                aviso.configure(text=f"Duración en {servicio.unidad_duracion}: de {minimo:g} a {maximo:g}.")
        self._invalidar_disponibilidad()

    def report_callback_exception(self, tipo, error, traza):
        """Captura errores inesperados de Tkinter sin cerrar la ventana."""
        self.sistema.logger.error("Error en un callback de la interfaz", exc_info=(tipo, error, traza))
        messagebox.showerror("Error de interfaz", "La operación falló. Consulta el log e inténtalo de nuevo.", parent=self)
