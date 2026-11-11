"""Interfaz CustomTkinter"""

import customtkinter as ctk
from tkinter import messagebox


class Aplicacion(ctk.CTk):
    def __init__(self, sistema):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.sistema = sistema
        self.title("Software FJ | Clientes y salas")
        self.geometry("1100x780")
        self.minsize(900, 680)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Software FJ", font=("Arial", 27, "bold")).grid(
            row=0, column=0, sticky="w", padx=24, pady=(18, 0)
        )
        ctk.CTkLabel(self, text="Gestión de clientes y servicios de salas").grid(
            row=1, column=0, sticky="w", padx=24, pady=(0, 8)
        )
        self.pestanas = ctk.CTkTabview(self)
        self.pestanas.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        self._crear_clientes(self.pestanas.add("Clientes"))
        self._crear_servicios(self.pestanas.add("Servicios"))
        self.estado = ctk.CTkLabel(self, text="Listo para registrar la primera operación.", anchor="w")
        self.estado.grid(row=3, column=0, sticky="ew", padx=24, pady=(5, 0))
        ctk.CTkLabel(
            self, text="Los registros se conservan solo mientras esta ventana esté abierta.",
            text_color="gray40",
        ).grid(row=4, column=0, sticky="w", padx=24, pady=(0, 12))
        self._actualizar_vistas()
        if sistema.aviso_log:
            self.estado.configure(text="El archivo de logs se guardará en la carpeta temporal.")

    def _panel(self, pestana):
        pestana.grid_columnconfigure(1, weight=1)
        pestana.grid_rowconfigure(0, weight=1)
        formulario = ctk.CTkScrollableFrame(pestana, width=320)
        formulario.grid(row=0, column=0, sticky="ns", padx=(4, 10), pady=8)
        listado = ctk.CTkTextbox(pestana, wrap="word", font=("Arial", 14))
        listado.grid(row=0, column=1, sticky="nsew", padx=(0, 4), pady=8)
        listado.configure(state="disabled")
        return formulario, listado

    def _entrada(self, formulario, etiqueta, ejemplo="", inicial=None):
        ctk.CTkLabel(formulario, text=etiqueta, anchor="w").pack(fill="x", pady=(8, 0))
        entrada = ctk.CTkEntry(formulario, placeholder_text=ejemplo)
        entrada.pack(fill="x", pady=(0, 4))
        if inicial is not None:
            entrada.insert(0, inicial)
        return entrada

    def _selector(self, formulario, etiqueta, valores, comando=None):
        ctk.CTkLabel(formulario, text=etiqueta, anchor="w").pack(fill="x", pady=(8, 0))
        selector = ctk.CTkComboBox(formulario, values=valores, state="readonly", command=comando)
        selector.pack(fill="x", pady=(0, 4))
        selector.set(valores[0])
        return selector

    def _boton(self, formulario, texto, comando):
        ctk.CTkButton(formulario, text=texto, command=comando).pack(fill="x", pady=(12, 0))

    def _crear_clientes(self, pestana):
        formulario, self.lista_clientes = self._panel(pestana)
        self.campos_cliente = {
            "identificador": self._entrada(formulario, "Identificador", "C001"),
            "nombre": self._entrada(formulario, "Nombre completo", "Ana Pérez"),
            "correo": self._entrada(formulario, "Correo electrónico", "ana@ejemplo.com"),
            "telefono": self._entrada(formulario, "Teléfono (sin espacios)", "3001234567"),
        }
        self._boton(formulario, "Registrar cliente", self._registrar_cliente)

    def _crear_servicios(self, pestana):
        formulario, self.lista_servicios = self._panel(pestana)
        self.campos_servicio = {
            "identificador": self._entrada(formulario, "Identificador", "S001"),
            "nombre": self._entrada(formulario, "Nombre de la sala", "Sala de reuniones"),
            "tarifa": self._entrada(formulario, "Tarifa por hora", "50000"),
            "capacidad": self._entrada(formulario, "Capacidad de personas (1 a 100)", "10"),
        }
        self._boton(formulario, "Registrar sala", self._registrar_servicio)
        ctk.CTkLabel(
            formulario, text="Consulta el costo de una sala por un periodo de 1 a 12 horas.",
            wraplength=290, justify="left", text_color="gray40",
        ).pack(fill="x", pady=16)
        self.servicio_cotizacion = self._selector(formulario, "Sala para consultar", ["Sin registros"])
        self.horas_cotizacion = self._entrada(formulario, "Duración en horas", "2", "2")
        self.impuesto_cotizacion = self._entrada(formulario, "Impuesto (%)", "0 a 100", "0")
        self.descuento_cotizacion = self._entrada(formulario, "Descuento (%)", "0 a 100", "0")
        self._boton(formulario, "Consultar costo", self._cotizar)

    def _realizar(self, descripcion, accion):
        correcto, resultado = self.sistema.ejecutar(descripcion, accion)
        self._actualizar_vistas()
        self.estado.configure(
            text=f"{descripcion}: {'completado' if correcto else 'revisa los datos'}. "
                 f"Operaciones atendidas: {self.sistema.operaciones}.",
            text_color="gray25" if correcto else "#AC2525",
        )
        if not correcto:
            messagebox.showerror(descripcion, str(resultado), parent=self)
        return correcto, resultado

    def _registrar_cliente(self):
        correcto, _ = self._realizar("Registrar cliente", lambda: self.sistema.registrar_cliente(
            **{nombre: campo.get() for nombre, campo in self.campos_cliente.items()}
        ))
        if correcto:
            for campo in self.campos_cliente.values():
                campo.delete(0, "end")

    def _registrar_servicio(self):
        correcto, _ = self._realizar("Registrar sala", lambda: self.sistema.registrar_servicio(
            **{nombre: campo.get() for nombre, campo in self.campos_servicio.items()},
        ))
        if correcto:
            for campo in self.campos_servicio.values():
                campo.delete(0, "end")

    def _id_seleccionado(self, selector):
        if selector.get() == "Sin registros":
            return ""
        return selector.get().split(" | ", 1)[0]

    def _cotizar(self):
        correcto, total = self._realizar("Consultar costo", lambda: self.sistema.cotizar(
            self._id_seleccionado(self.servicio_cotizacion), self.horas_cotizacion.get(),
            self.impuesto_cotizacion.get(), self.descuento_cotizacion.get(),
        ))
        if correcto:
            messagebox.showinfo("Costo de la sala", f"Total: ${total:,.2f}", parent=self)

    def _escribir_listado(self, listado, titulo, lineas):
        listado.configure(state="normal")
        listado.delete("1.0", "end")
        contenido = "\n\n".join(lineas) if lineas else "Todavía no hay registros."
        listado.insert("1.0", f"{titulo}\n\n{contenido}")
        listado.configure(state="disabled")

    def _actualizar_selector(self, selector, valores):
        anterior = selector.get().split(" | ", 1)[0]
        valores = valores or ["Sin registros"]
        selector.configure(values=valores)
        elegido = next((valor for valor in valores if valor.split(" | ", 1)[0] == anterior), valores[0])
        selector.set(elegido)

    def _actualizar_vistas(self):
        clientes = self.sistema.clientes
        servicios = self.sistema.servicios
        self._escribir_listado(self.lista_clientes, f"CLIENTES ({len(clientes)})", [c.describir() for c in clientes])
        self._escribir_listado(self.lista_servicios, f"SALAS ({len(servicios)})", [s.describir() for s in servicios])
        self._actualizar_selector(self.servicio_cotizacion, [f"{s.identificador} | {s.nombre}" for s in servicios])

    def report_callback_exception(self, tipo, error, traza):
        self.sistema.logger.error("Error en un callback de la interfaz", exc_info=(tipo, error, traza))
        messagebox.showerror("Error de interfaz", "La operación falló. Consulta el log e inténtalo de nuevo.", parent=self)
