"""Interfaz CustomTkinter"""

import customtkinter as ctk
from tkinter import messagebox


class Aplicacion(ctk.CTk):
    def __init__(self, sistema):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.sistema = sistema
        self.title("Software FJ | Clientes, servicios y reservas")
        self.geometry("1100x780")
        self.minsize(900, 680)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Software FJ", font=("Arial", 27, "bold")).grid(
            row=0, column=0, sticky="w", padx=24, pady=(18, 0)
        )
        ctk.CTkLabel(self, text="Gestión de clientes, servicios y reservas").grid(
            row=1, column=0, sticky="w", padx=24, pady=(0, 8)
        )
        self.pestanas = ctk.CTkTabview(self)
        self.pestanas.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        self._crear_clientes(self.pestanas.add("Clientes"))
        self._crear_servicios(self.pestanas.add("Servicios"))
        self._crear_reservas(self.pestanas.add("Reservas"))
        self.estado = ctk.CTkLabel(self, text="Listo para registrar la primera operación.", anchor="w")
        self.estado.grid(row=3, column=0, sticky="ew", padx=24, pady=(5, 0))
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
        self.tipo_servicio = self._selector(
            formulario, "Tipo de servicio", ["Sala", "Equipo", "Asesoría"], self._mostrar_tipo
        )
        self.campos_servicio = {
            "identificador": self._entrada(formulario, "Identificador", "S001"),
            "nombre": self._entrada(formulario, "Nombre del servicio", "Sala de reuniones"),
        }
        self.etiqueta_tarifa = ctk.CTkLabel(formulario, text="Tarifa por hora", anchor="w")
        self.etiqueta_tarifa.pack(fill="x", pady=(8, 0))
        tarifa = ctk.CTkEntry(formulario, placeholder_text="50000")
        tarifa.pack(fill="x", pady=(0, 4))
        self.campos_servicio["tarifa"] = tarifa

        contenedor = ctk.CTkFrame(formulario)
        contenedor.pack(fill="x", pady=8)
        self.parametros_tipo = {tipo: ctk.CTkFrame(contenedor) for tipo in ("Sala", "Equipo", "Asesoría")}
        sala = self.parametros_tipo["Sala"]
        self.capacidad_sala = self._entrada(sala, "Capacidad de personas (1 a 500)", "10")
        equipo = self.parametros_tipo["Equipo"]
        self.unidad_equipo = self._selector(
            equipo, "Unidad de cobro", ["días", "horas"], lambda _: self._actualizar_etiqueta_tarifa()
        )
        self.cantidad_equipo = self._entrada(equipo, "Cantidad de equipos (1 a 100)", "1", "1")
        self.deposito_equipo = self._entrada(equipo, "Depósito único (0 para omitir)", "50000", "50000")
        ctk.CTkLabel(
            equipo, text="El conjunto se alquila completo. El depósito se incluye en el subtotal; "
            "sobre ese valor se aplican descuento e impuesto.",
            wraplength=290, justify="left", text_color="gray40",
        ).pack(fill="x", pady=8)
        asesoria = self.parametros_tipo["Asesoría"]
        self.especialista_asesoria = self._entrada(asesoria, "Especialista", "Ing. Daniela")
        self.especialidad_asesoria = self._entrada(asesoria, "Especialidad", "Programación")
        self.preparacion_asesoria = self._selector(asesoria, "Horas extra de preparación", ["0", "0.5"])
        self._mostrar_tipo("Sala")
        self._boton(formulario, "Registrar servicio", self._registrar_servicio)

        self.servicio_cotizacion = self._selector(
            formulario, "Servicio para consultar", ["Sin registros"], lambda _: self._actualizar_unidades()
        )
        self.aviso_cotizacion = ctk.CTkLabel(formulario, text="Selecciona un servicio.", wraplength=290)
        self.aviso_cotizacion.pack(fill="x", pady=4)
        self.horas_cotizacion = self._entrada(formulario, "Duración (en la unidad indicada)", "2", "2")
        self.impuesto_cotizacion = self._entrada(formulario, "Impuesto (%)", "0 a 100", "0")
        self.descuento_cotizacion = self._entrada(formulario, "Descuento (%)", "0 a 100", "0")
        self._boton(formulario, "Consultar costo", self._cotizar)

    def _mostrar_tipo(self, tipo):
        for panel in self.parametros_tipo.values():
            panel.pack_forget()
        self.parametros_tipo[tipo].pack(fill="x", padx=6, pady=6)
        self._actualizar_etiqueta_tarifa()

    def _actualizar_etiqueta_tarifa(self):
        texto = "Tarifa por hora"
        if self.tipo_servicio.get() == "Equipo":
            unidad = "día" if self.unidad_equipo.get() == "días" else "hora"
            texto = f"Tarifa por unidad y {unidad}"
        self.etiqueta_tarifa.configure(text=texto)

    def _crear_reservas(self, pestana):
        formulario, self.lista_reservas = self._panel(pestana)
        self.cliente_reserva = self._selector(formulario, "Cliente", ["Sin registros"])
        self.servicio_reserva = self._selector(
            formulario, "Servicio", ["Sin registros"], lambda _: self._actualizar_unidades()
        )
        self.aviso_reserva = ctk.CTkLabel(formulario, text="Selecciona un servicio.", wraplength=290)
        self.aviso_reserva.pack(fill="x", pady=4)
        self.horas_reserva = self._entrada(formulario, "Duración (en la unidad indicada)", "2", "2")
        self.impuesto_reserva = self._entrada(formulario, "Impuesto (%)", "0 a 100", "0")
        self.descuento_reserva = self._entrada(formulario, "Descuento (%)", "0 a 100", "0")
        self._boton(formulario, "Crear reserva pendiente", self._crear_reserva)
        self.reserva_elegida = self._selector(formulario, "Reserva que deseas gestionar", ["Sin registros"])
        self._boton(formulario, "Confirmar", lambda: self._gestionar_reserva("Confirmar"))
        self._boton(formulario, "Cancelar", lambda: self._gestionar_reserva("Cancelar"))
        self._boton(formulario, "Procesar / completar", lambda: self._gestionar_reserva("Procesar"))
        ctk.CTkLabel(
            formulario, text="Solo una reserva confirmada ocupa un servicio. "
            "Debe cancelar o completar la reserva para libera el servicio.",
            wraplength=290, justify="left", text_color="gray40",
        ).pack(fill="x", pady=16)

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
        correcto, _ = self._realizar("Registrar servicio", self._guardar_servicio)
        if correcto:
            for campo in self.campos_servicio.values():
                campo.delete(0, "end")

    def _guardar_servicio(self):
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
        if selector.get() == "Sin registros":
            return ""
        return selector.get().split(" | ", 1)[0]

    def _cotizar(self):
        correcto, total = self._realizar("Consultar costo", lambda: self.sistema.cotizar(
            self._id_seleccionado(self.servicio_cotizacion), self.horas_cotizacion.get(),
            self.impuesto_cotizacion.get(), self.descuento_cotizacion.get(),
        ))
        if correcto:
            messagebox.showinfo("Costo del servicio", f"Total: ${total:,.2f}", parent=self)

    def _crear_reserva(self):
        correcto, reserva = self._realizar("Crear reserva", lambda: self.sistema.crear_reserva(
            self._id_seleccionado(self.cliente_reserva), self._id_seleccionado(self.servicio_reserva),
            self.horas_reserva.get(), self.impuesto_reserva.get(), self.descuento_reserva.get(),
        ))
        if correcto:
            self.reserva_elegida.set(f"{reserva.identificador} | {reserva.estado}")

    def _gestionar_reserva(self, accion):
        operaciones = {"Confirmar": self.sistema.confirmar_reserva,
                       "Cancelar": self.sistema.cancelar_reserva,
                       "Procesar": self.sistema.procesar_reserva}
        self._realizar(f"{accion} reserva", lambda: operaciones[accion](
            self._id_seleccionado(self.reserva_elegida)
        ))

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
        reservas = self.sistema.reservas
        self._escribir_listado(self.lista_clientes, f"CLIENTES ({len(clientes)})", [c.describir() for c in clientes])
        self._escribir_listado(self.lista_servicios, f"SERVICIOS ({len(servicios)})", [
            f"{s.describir()}\nEstado: {'Disponible' if s.disponible else 'Ocupado'}" for s in servicios
        ])
        self._escribir_listado(self.lista_reservas, f"RESERVAS ({len(reservas)})", [r.describir() for r in reservas])
        opciones = [f"{s.identificador} | {s.nombre} | {s.unidad_duracion}" for s in servicios]
        self._actualizar_selector(self.servicio_cotizacion, opciones)
        self._actualizar_selector(self.servicio_reserva, opciones)
        self._actualizar_selector(self.cliente_reserva, [f"{c.identificador} | {c.nombre}" for c in clientes])
        self._actualizar_selector(self.reserva_elegida, [f"{r.identificador} | {r.estado}" for r in reservas])
        self._actualizar_unidades()

    def _actualizar_unidades(self):
        for selector, aviso in ((self.servicio_cotizacion, self.aviso_cotizacion),
                                (self.servicio_reserva, self.aviso_reserva)):
            identificador = self._id_seleccionado(selector)
            servicio = next((s for s in self.sistema.servicios if s.identificador == identificador), None)
            if servicio is None:
                aviso.configure(text="Registra y selecciona un servicio.")
            else:
                minimo, maximo = servicio.rango_duracion
                aviso.configure(text=f"Unidad: {servicio.unidad_duracion}. Duración: de {minimo:g} a {maximo:g}.")

    def report_callback_exception(self, tipo, error, traza):
        self.sistema.logger.error("Error en un callback de la interfaz", exc_info=(tipo, error, traza))
        messagebox.showerror("Error de interfaz", "La operación falló. Consulta el log e inténtalo de nuevo.", parent=self)
