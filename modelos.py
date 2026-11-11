"""Entidades y reglas del negocio"""

from abc import ABC, abstractmethod
from math import isfinite
import re

from excepciones import CalculoError, DatosInvalidosError


def validar_texto(valor, campo, minimo=1, maximo=80):
    if not isinstance(valor, str):
        raise DatosInvalidosError(f"{campo}: debes escribir un texto.")
    valor = valor.strip()
    if not minimo <= len(valor) <= maximo or not valor.isprintable():
        raise DatosInvalidosError(
            f"{campo}: usa entre {minimo} y {maximo} caracteres, sin saltos de línea."
        )
    return valor


def validar_identificador(valor):
    valor = validar_texto(valor, "Identificador", maximo=20).upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]*", valor):
        raise DatosInvalidosError("Identificador: usa letras, números, guion o guion bajo.")
    return valor


def validar_numero(valor, campo, minimo, maximo):
    """aqui se convierte las entradas del formulario y conserva la causa de cada error"""
    try:
        if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
            raise TypeError("Se esperaba un número o un texto numérico.")
        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")
        numero = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise DatosInvalidosError(f"{campo}: escribe un número válido.") from error
    if not isfinite(numero) or not minimo <= numero <= maximo:
        raise DatosInvalidosError(f"{campo}: debe estar entre {minimo} y {maximo}.")
    return numero


def validar_entero(valor, campo, minimo, maximo):
    numero = validar_numero(valor, campo, minimo, maximo)
    if not numero.is_integer():
        raise DatosInvalidosError(f"{campo}: debe ser un número entero.")
    return int(numero)


class Entidad(ABC):

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


class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        nombre = validar_texto(nombre, "Nombre", minimo=3)
        if (sum(letra.isalpha() for letra in nombre) < 2
                or not all(letra.isalpha() or letra in " '-." for letra in nombre)):
            raise DatosInvalidosError("Nombre: usa letras y separadores habituales.")
        correo = validar_texto(correo, "Correo", maximo=254).lower()
        if not re.fullmatch(r"[a-z0-9_%+.-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+", correo):
            raise DatosInvalidosError("Correo: escribe una dirección como ana@ejemplo.com.")
        usuario, dominio = correo.split("@")
        if (len(usuario) > 64 or usuario.startswith(".") or usuario.endswith(".")
                or ".." in usuario or any(
                    parte.startswith("-") or parte.endswith("-") or len(parte) > 63
                    for parte in dominio.split(".")
                )):
            raise DatosInvalidosError("Correo: el formato de la dirección no es válido.")
        telefono = validar_texto(telefono, "Teléfono", maximo=16)
        if not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
            raise DatosInvalidosError("Teléfono: usa de 7 a 15 dígitos y un + opcional al inicio.")
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def describir(self):
        return f"{self.identificador} | {self.nombre} | {self.correo} | {self.telefono}"


class Servicio(Entidad):
    def __init__(self, identificador, nombre, tarifa):
        super().__init__(identificador)
        self.__nombre = validar_texto(nombre, "Nombre del servicio", minimo=3)
        self.__tarifa = round(validar_numero(tarifa, "Tarifa por hora", 0.01, 1000000000), 2)

    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa(self):
        return self.__tarifa

    def _aplicar_ajustes(self, subtotal, impuesto, descuento):
        impuesto = validar_numero(impuesto, "Impuesto (%)", 0, 100)
        descuento = validar_numero(descuento, "Descuento (%)", 0, 100)
        total = subtotal * (1 - descuento / 100) * (1 + impuesto / 100)
        if not isfinite(total) or total < 0:
            raise CalculoError("El costo calculado no es válido.")
        return round(total, 2)

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass


class ServicioSala(Servicio):
    def __init__(self, identificador, nombre, tarifa, capacidad):
        super().__init__(identificador, nombre, tarifa)
        self.__capacidad = validar_entero(capacidad, "Capacidad de la sala", 1, 100)

    def validar_parametros(self, duracion):
        return validar_numero(duracion, "Horas de sala", 1, 12)

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        horas = self.validar_parametros(duracion)
        return self._aplicar_ajustes(self.tarifa * horas, impuesto, descuento)

    def describir(self):
        return (f"{self.identificador} | Sala: {self.nombre} | "
                f"{self.__capacidad} personas | ${self.tarifa:,.2f}/hora")


