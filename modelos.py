from abc import ABC, abstractmethod
from math import isfinite
import re

from excepciones import CalculoError, DatosInvalidosError, ReservaInvalidaError

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

# Clase Cliente
class Cliente:
    def __init__(self, identificador, nombre, correo, telefono):
        self.identificador = identificador
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def identificador(self):
        return self._identificador

    @identificador.setter
    def identificador(self, valor):
        self._identificador = validar_identificador(valor)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "Nombre completo", minimo=2, maximo=100)

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        valor = validar_texto(valor, "Correo electrónico", minimo=5, maximo=100)
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", valor):
            raise DatosInvalidosError("Correo electrónico con formato incorrecto.")
        self._correo = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = validar_texto(valor, "Teléfono", minimo=7, maximo=15)
        if not valor.isdigit():
            raise DatosInvalidosError("Teléfono: ingrese solo números.")
        self._telefono = valor

    def describir(self):
        return f"Cliente: {self.nombre} (ID: {self.identificador}) | Correo: {self.correo} | Tel: {self.telefono}"

# Clase abstracta Servicio
class Servicio(ABC):
    def __init__(self, identificador, nombre, tarifa_base):
        self.identificador = identificador
        self.nombre = nombre
        self.tarifa_base = tarifa_base

    @property
    def identificador(self):
        return self._identificador

    @identificador.setter
    def identificador(self, valor):
        self._identificador = validar_identificador(valor)

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
        self._tarifa_base = validar_numero(valor, "Tarifa base", minimo=0, maximo=5000000)

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0, *args, **kwargs):
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
        self._capacidad = int(validar_numero(valor, "Capacidad", minimo=1, maximo=500))

    def calcular_costo(self, duracion, impuesto=0, descuento=0, *args, **kwargs):
        duracion_val = validar_numero(duracion, "Horas de sala", minimo=1, maximo=720)
        imp = validar_numero(impuesto, "Impuesto (%)", minimo=0, maximo=100)
        desc = validar_numero(descuento, "Descuento (%)", minimo=0, maximo=100)
        
        subtotal = self.tarifa_base * duracion_val
        subtotal_desc = subtotal * (1 - desc / 100)
        total = subtotal_desc * (1 + imp / 100)
        return round(total, 2)

    def describir(self):
        return f"SALA: {self.nombre} (ID: {self.identificador}) | Capacidad: {self.capacidad} p. | Tarifa/h: ${self.tarifa_base:,.0f}"

# Subclase 2: Alquiler de equipos
class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre, tarifa_base, deposito_garantia=50000):
        super().__init__(identificador, nombre, tarifa_base)
        self.deposito_garantia = deposito_garantia

    @property
    def deposito_garantia(self):
        return self._deposito_garantia

    @deposito_garantia.setter
    def deposito_garantia(self, valor):
        self._deposito_garantia = validar_numero(valor, "Depósito garantía", minimo=0, maximo=2000000)

    def calcular_costo(self, duracion, impuesto=0, descuento=0, *args, **kwargs):
        duracion_val = validar_numero(duracion, "Días de alquiler", minimo=1, maximo=90)
        subtotal = (self.tarifa_base * duracion_val) + self.deposito_garantia
        desc = validar_numero(descuento, "Descuento (%)", minimo=0, maximo=100)
        imp = validar_numero(impuesto, "Impuesto (%)", minimo=0, maximo=100)
        
        total = (subtotal * (1 - desc / 100)) * (1 + imp / 100)
        return round(total, 2)

    def describir(self):
        return f"EQUIPO: {self.nombre} (ID: {self.identificador}) | Tarifa/día: ${self.tarifa_base:,.0f} | Depósito: ${self.deposito_garantia:,.0f}"

# Subclase 3: Asesoria especializada
class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, nombre, tarifa_base, especialista):
        super().__init__(identificador, nombre, tarifa_base)
        self.especialista = especialista

    @property
    def especialista(self):
        return self._especialista

    @especialista.setter
    def especialista(self, valor):
        self._especialista = validar_texto(valor, "Especialista", minimo=3, maximo=100)

    def calcular_costo(self, duracion, impuesto=0, descuento=0, *args, **kwargs):
        duracion_val = validar_numero(duracion, "Horas asesoría", minimo=1, maximo=100)
        imp = validar_numero(impuesto, "Impuesto (%)", minimo=0, maximo=100)
        desc = validar_numero(descuento, "Descuento (%)", minimo=0, maximo=100)
        
        subtotal = self.tarifa_base * duracion_val
        total = (subtotal * (1 - desc / 100)) * (1 + imp / 100)
        return round(total, 2)

    def describir(self):
        return f"ASESORIA: {self.nombre} (ID: {self.identificador}) | Asesor: {self.especialista} | Tarifa/h: ${self.tarifa_base:,.0f}"

# Clase Reserva
class Reserva:
    def __init__(self, id_reserva, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("Reserva: Cliente no válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Reserva: Servicio no válido.")
            
        self.id_reserva = validar_identificador(id_reserva)
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = validar_numero(duracion, "Duración", minimo=1, maximo=720)
        self._estado = "PENDIENTE"

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError("No se puede confirmar una reserva cancelada.")
        self._estado = "CONFIRMADA"

    def cancelar(self):
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError("La reserva ya está cancelada.")
        self._estado = "CANCELADA"

    def calcular_costo_total(self, impuesto=0, descuento=0):
        return self.servicio.calcular_costo(self.duracion, impuesto, descuento)

    def describir(self):
        costo = self.calcular_costo_total()
        return f"RESERVA {self.id_reserva} [{self._estado}] - Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre} | Total: ${costo:,.2f}"