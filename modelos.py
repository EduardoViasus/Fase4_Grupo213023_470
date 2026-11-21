from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from math import isfinite
import re

from excepciones import (
    CalculoError, DatosInvalidosError, ErrorSistema, OperacionNoPermitidaError,
    ReservaError,
)

# Funciones de validacion
def validar_texto(valor, campo, minimo=1, maximo=80):
    if not isinstance(valor, str):
        raise DatosInvalidosError(f"{campo}: debes escribir un texto.")
    valor = valor.strip()
    if not (minimo <= len(valor) <= maximo) or not valor.isprintable():
        raise DatosInvalidosError(f"{campo}: usa entre {minimo} y {maximo} caracteres.")
    return valor

def validar_identificador(valor):
    valor = validar_texto(valor, "Identificador", maximo=20).upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]*", valor):
        raise DatosInvalidosError("Identificador: usa letras, números o guiones.")
    return valor

def validar_numero(valor, campo, minimo=0, maximo=100000000):
    try:
        if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
            raise TypeError("Se esperaba un número.")
        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")
        numero = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise DatosInvalidosError(f"{campo}: escribe un número válido.") from error

    if not isfinite(numero) or not (minimo <= numero <= maximo):
        raise DatosInvalidosError(f"{campo}: debe estar entre {minimo} y {maximo}.")
    return numero

def validar_entero(valor, campo, minimo, maximo):
    numero = validar_numero(valor, campo, minimo, maximo)
    if not numero.is_integer():
        raise DatosInvalidosError(f"{campo}: debe ser un número entero.")
    return int(numero)


def validar_fecha_hora(fecha, hora):
    fecha = validar_texto(fecha, "Fecha", minimo=10, maximo=10)
    hora = validar_texto(hora, "Hora", minimo=5, maximo=5)
    if not re.fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", fecha):
        raise DatosInvalidosError("Fecha: usa el formato dd/mm/aaaa.")
    if not re.fullmatch(r"[0-9]{2}:[0-9]{2}", hora):
        raise DatosInvalidosError("Hora: usa el formato HH:MM de 24 horas.")
    try:
        return datetime.strptime(f"{fecha} {hora}", "%d/%m/%Y %H:%M")
    except ValueError as error:
        raise DatosInvalidosError("La fecha o la hora no son válidas.") from error


class Entidad(ABC):
    """Base común; el identificador no cambia después de crear la entidad."""

    def __init__(self, identificador):
        self.__identificador = validar_identificador(identificador)

    @property
    def identificador(self):
        return self.__identificador

    @abstractmethod
    def describir(self):
        pass

    def __str__(self):
        return self.describir()


# Clase Cliente: conserva las propiedades con setters del pull request.
class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        valor = validar_texto(valor, "Nombre completo", minimo=2, maximo=100)
        if (sum(letra.isalpha() for letra in valor) < 2
                or not all(letra.isalpha() or letra in " '-." for letra in valor)):
            raise DatosInvalidosError("Nombre: usa letras y separadores habituales.")
        self._nombre = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        valor = validar_texto(valor, "Correo electrónico", minimo=5, maximo=254).lower()
        if not re.fullmatch(r"[a-z0-9_%+.-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+", valor):
            raise DatosInvalidosError("Correo electrónico con formato incorrecto.")
        usuario, dominio = valor.split("@")
        if (len(usuario) > 64 or usuario.startswith(".") or usuario.endswith(".")
                or ".." in usuario or any(
                    parte.startswith("-") or parte.endswith("-") or len(parte) > 63
                    for parte in dominio.split(".")
                )):
            raise DatosInvalidosError("Correo electrónico con formato incorrecto.")
        self._correo = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = validar_texto(valor, "Teléfono", minimo=7, maximo=16)
        if not re.fullmatch(r"\+?[0-9]{7,15}", valor):
            raise DatosInvalidosError("Teléfono: usa de 7 a 15 dígitos y un + opcional al inicio.")
        self._telefono = valor

    def describir(self):
        return f"Cliente: {self.nombre} (ID: {self.identificador}) | Correo: {self.correo} | Tel: {self.telefono}"

# Clase abstracta Servicio
class Servicio(Entidad):
    def __init__(self, identificador, nombre, tarifa_base):
        super().__init__(identificador)
        self.nombre = nombre
        self.tarifa_base = tarifa_base

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "Nombre del servicio", minimo=3, maximo=80)

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        self._tarifa_base = round(validar_numero(valor, "Tarifa base", 0.01, 1000000000), 2)

    @property
    def tarifa(self):
        return self.tarifa_base

    @property
    def unidad_duracion(self):
        return "horas"

    def calcular_intervalo(self, fecha, hora, duracion):
        inicio = validar_fecha_hora(fecha, hora)
        tiempo = self.validar_parametros(duracion)
        try:
            periodo = timedelta(days=tiempo) if self.unidad_duracion == "días" else timedelta(hours=tiempo)
            fin = inicio + periodo
        except OverflowError as error:
            raise DatosInvalidosError("La duración excede las fechas admitidas.") from error
        return inicio, fin

    def _aplicar_ajustes(self, subtotal, impuesto, descuento):
        impuesto = validar_numero(impuesto, "Impuesto (%)", 0, 100)
        descuento = validar_numero(descuento, "Descuento (%)", 0, 100)
        total = subtotal * (1 - descuento / 100) * (1 + impuesto / 100)
        if not isfinite(total) or total < 0:
            raise CalculoError("El costo calculado no es válido.")
        return round(total, 2)

    @property
    @abstractmethod
    def rango_duracion(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def describir(self):
        pass

# Subclase 1: Reserva de salas
class ReservaSala(Servicio):
    def __init__(self, identificador, nombre, tarifa_base, capacidad):
        super().__init__(identificador, nombre, tarifa_base)
        self.capacidad = capacidad

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        self._capacidad = validar_entero(valor, "Capacidad", 1, 500)

    @property
    def rango_duracion(self):
        return 1, 720

    def validar_parametros(self, duracion):
        return validar_numero(duracion, "Horas de sala", *self.rango_duracion)

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        horas = self.validar_parametros(duracion)
        return self._aplicar_ajustes(self.tarifa_base * horas, impuesto, descuento)

    def describir(self):
        return f"SALA: {self.nombre} (ID: {self.identificador}) | Capacidad: {self.capacidad} p. | Tarifa/h: ${self.tarifa_base:,.0f}"

# Subclase 2: Alquiler de equipos
class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre, tarifa_base, deposito_garantia=50000,
                 cantidad=1, unidad="días"):
        super().__init__(identificador, nombre, tarifa_base)
        self.deposito_garantia = deposito_garantia
        self.cantidad = cantidad
        unidad = validar_texto(unidad, "Unidad de alquiler").lower()
        if unidad not in ("horas", "días"):
            raise DatosInvalidosError("Unidad de alquiler: elige horas o días.")
        self.__unidad = unidad

    @property
    def unidad_duracion(self):
        return self.__unidad

    @property
    def rango_duracion(self):
        return (0.5, 72) if self.unidad_duracion == "horas" else (1, 90)

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        self._cantidad = validar_entero(valor, "Cantidad de equipos", 1, 100)

    @property
    def deposito_garantia(self):
        return self._deposito_garantia

    @deposito_garantia.setter
    def deposito_garantia(self, valor):
        self._deposito_garantia = round(validar_numero(valor, "Depósito garantía", 0, 2000000), 2)

    def validar_parametros(self, duracion):
        return validar_numero(duracion, f"Alquiler en {self.unidad_duracion}", *self.rango_duracion)

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        tiempo = self.validar_parametros(duracion)
        subtotal = self.tarifa_base * tiempo * self.cantidad + self.deposito_garantia
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self):
        unidad = "hora" if self.unidad_duracion == "horas" else "día"
        return (f"EQUIPO: {self.nombre} (ID: {self.identificador}) | {self.cantidad} unidades | "
                f"Tarifa/unidad/{unidad}: ${self.tarifa_base:,.2f} | "
                f"Depósito único: ${self.deposito_garantia:,.2f}")

# Subclase 3: Asesoria especializada
class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, nombre, tarifa_base, especialista,
                 especialidad="General", horas_preparacion=0):
        super().__init__(identificador, nombre, tarifa_base)
        self.especialista = especialista
        self.especialidad = especialidad
        preparacion = validar_numero(horas_preparacion, "Horas de preparación", 0, 0.5)
        if preparacion not in (0, 0.5):
            raise DatosInvalidosError("Preparación: elige 0 o 0.5 horas.")
        self.__horas_preparacion = preparacion

    @property
    def horas_preparacion(self):
        return self.__horas_preparacion

    @property
    def especialidad(self):
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor):
        self._especialidad = validar_texto(valor, "Especialidad", minimo=3, maximo=60)

    @property
    def especialista(self):
        return self._especialista

    @especialista.setter
    def especialista(self, valor):
        self._especialista = validar_texto(valor, "Especialista", minimo=3, maximo=100)

    @property
    def rango_duracion(self):
        return 0.5, 100

    def validar_parametros(self, duracion):
        return validar_numero(duracion, "Horas de asesoría", *self.rango_duracion)

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        horas = self.validar_parametros(duracion)
        subtotal = self.tarifa_base * (horas + self.horas_preparacion)
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self):
        return (f"ASESORÍA: {self.nombre} (ID: {self.identificador}) | {self.especialidad} | "
                f"Asesor: {self.especialista} | Tarifa/h: ${self.tarifa_base:,.2f} | "
                f"Preparación adicional: {self.horas_preparacion:g} h")

# Clase Reserva
class Reserva(Entidad):
    def __init__(self, id_reserva, cliente, servicio, duracion, fecha, hora,
                 impuesto=0, descuento=0):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("Reserva: Cliente no válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Reserva: Servicio no válido.")
            
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = servicio.validar_parametros(duracion)
        self.__inicio, self.__fin = servicio.calcular_intervalo(fecha, hora, self.duracion)
        if self.inicio < datetime.now():
            raise DatosInvalidosError("La reserva debe comenzar en una fecha y hora futuras.")
        self.__impuesto = validar_numero(impuesto, "Impuesto (%)", 0, 100)
        self.__descuento = validar_numero(descuento, "Descuento (%)", 0, 100)
        self.__total = self.calcular_costo_total()
        self.__estado = "ACTIVA"
        self.__fecha_finalizacion = None
        self.__observacion_finalizacion = ""

    @property
    def id_reserva(self):
        return self.identificador

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def inicio(self):
        return self.__inicio

    @property
    def fin(self):
        return self.__fin

    @property
    def total(self):
        return self.__total

    @property
    def estado(self):
        return self.__estado

    @property
    def fecha_finalizacion(self):
        return self.__fecha_finalizacion

    @property
    def observacion_finalizacion(self):
        return self.__observacion_finalizacion

    @property
    def finalizacion_anticipada(self):
        return self.fecha_finalizacion is not None and self.fecha_finalizacion < self.fin

    def se_cruza(self, inicio, fin):
        """Dos reservas consecutivas pueden compartir la hora de salida/entrada."""
        return self.estado == "ACTIVA" and self.inicio < fin and inicio < self.fin

    def cancelar(self):
        if self.estado != "ACTIVA":
            raise OperacionNoPermitidaError("La reserva ya terminó o ya fue cancelada.")
        self.__estado = "CANCELADA"

    def calcular_costo_total(self, impuesto=None, descuento=None):
        if impuesto is None:
            impuesto = self.__impuesto
        if descuento is None:
            descuento = self.__descuento
        return self.servicio.calcular_costo(self.duracion, impuesto, descuento)

    def finalizar(self, observacion=""):
        if self.estado != "ACTIVA":
            raise OperacionNoPermitidaError("Solo puedes finalizar una reserva activa.")
        momento = datetime.now()
        if not isinstance(observacion, str):
            raise DatosInvalidosError("La observación debe ser un texto.")
        observacion = " ".join(observacion.split())
        if momento < self.fin or observacion:
            observacion = validar_texto(observacion, "Observación de finalización", minimo=1, maximo=500)
        try:
            total = self.calcular_costo_total()
            if not isfinite(total) or total < 0 or round(total, 2) != self.total:
                raise CalculoError("El total no coincide con el valor original de la reserva.")
        except (ErrorSistema, ArithmeticError, TypeError, ValueError) as error:
            raise ReservaError("No se pudo finalizar la reserva; revisa la causa en el log.") from error
        else:
            self.__fecha_finalizacion = momento
            self.__observacion_finalizacion = observacion
            self.__estado = "FINALIZADA"
            return self.total

    def describir(self):
        descripcion = (f"RESERVA {self.id_reserva} [{self.estado}] | Cliente: {self.cliente.nombre} "
                f"({self.cliente.identificador}) | Servicio: {self.servicio.nombre} "
                f"({self.servicio.identificador}) | "
                f"Inicio: {self.inicio:%d/%m/%Y %H:%M} | Fin pactado: {self.fin:%d/%m/%Y %H:%M} | "
                f"{self.duracion:g} {self.servicio.unidad_duracion} | "
                f"Total: ${self.total:,.2f}")
        if self.fecha_finalizacion is not None:
            descripcion += f" | Fin real: {self.fecha_finalizacion:%d/%m/%Y %H:%M:%S}"
            if self.finalizacion_anticipada:
                descripcion += " | Finalización anticipada"
            if self.observacion_finalizacion:
                descripcion += f" | Observación: {self.observacion_finalizacion}"
        return descripcion
