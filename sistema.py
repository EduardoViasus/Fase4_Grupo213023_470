"""Gestión de listas y punto común para controlar errores y registrar los eventos."""

import logging
from pathlib import Path
from tempfile import gettempdir

from excepciones import DatosInvalidosError, DuplicadoError, ErrorSistema, NoEncontradoError
from modelos import (
    Cliente, Servicio, Reserva, ReservaSala, AlquilerEquipo,
    AsesoriaEspecializada, validar_identificador,
)


def configurar_logs():
    logger = logging.getLogger("software_fj")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        return logger, Path(logger.handlers[0].baseFilename), ""

    ruta = Path(__file__).resolve().parent / "logs" / "software_fj.log"
    aviso = ""
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        archivo = logging.FileHandler(ruta, encoding="utf-8")
    except OSError as error:
        ruta = Path(gettempdir()) / "software_fj" / "software_fj.log"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        archivo = logging.FileHandler(ruta, encoding="utf-8")
        aviso = f"No se pudo abrir el log del proyecto ({error}). Se usará: {ruta}"
    archivo.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(archivo)
    if aviso:
        logger.warning(aviso)
    return logger, ruta, aviso


class SistemaGestion:
    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        self.__operaciones = 0
        self.logger, self.ruta_log, self.aviso_log = configurar_logs()
        self.logger.info("Inicio de Software FJ; listas vacías en memoria.")

    @property
    def clientes(self):
        return self.__clientes.copy()

    @property
    def servicios(self):
        return self.__servicios.copy()

    @property
    def reservas(self):
        return self.__reservas.copy()

    @property
    def operaciones(self):
        return self.__operaciones

    def ejecutar(self, descripcion, accion):
        try:
            resultado = accion()
        except ErrorSistema as error:
            self.logger.exception("%s: %s", descripcion, error)
            return False, str(error)
        except (TypeError, ValueError) as error:
            self.logger.exception("%s: parámetros incorrectos o faltantes", descripcion)
            return False, f"Revisa los datos y parámetros de la operación: {error}"
        except Exception as error:
            self.logger.exception("%s: error inesperado", descripcion)
            return False, f"Error inesperado ({type(error).__name__}). Consulta el archivo de logs."
        else:
            self.logger.info("%s: operación exitosa. %s", descripcion, resultado)
            return True, resultado
        finally:
            self.__operaciones += 1
            self.logger.info("Fin de la operación %s: %s", self.operaciones, descripcion)

    def registrar_cliente(self, identificador, nombre, correo, telefono):
        cliente = Cliente(identificador, nombre, correo, telefono)
        if any(actual.identificador == cliente.identificador for actual in self.__clientes):
            raise DuplicadoError("Ya existe un cliente con ese identificador.")
        self.__clientes.append(cliente)
        return cliente

    def registrar_servicio(self, identificador, nombre, tarifa, capacidad):
        servicio = ReservaSala(identificador, nombre, tarifa, capacidad)
        return self.agregar_servicio(servicio)

    def registrar_equipo(self, identificador, nombre, tarifa, deposito_garantia=50000,
                         cantidad=1, unidad="días"):
        servicio = AlquilerEquipo(identificador, nombre, tarifa, deposito_garantia,
                                  cantidad=cantidad, unidad=unidad)
        return self.agregar_servicio(servicio)

    def registrar_asesoria(self, identificador, nombre, tarifa, especialista,
                           especialidad="General", horas_preparacion=0):
        servicio = AsesoriaEspecializada(identificador, nombre, tarifa, especialista,
                                         especialidad=especialidad,
                                         horas_preparacion=horas_preparacion)
        return self.agregar_servicio(servicio)

    def agregar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Debes proporcionar un servicio válido.")
        if any(actual.identificador == servicio.identificador for actual in self.__servicios):
            raise DuplicadoError("Ya existe un servicio con ese identificador.")
        self.__servicios.append(servicio)
        return servicio

    def _buscar(self, lista, identificador, entidad):
        identificador = validar_identificador(identificador)
        for elemento in lista:
            if elemento.identificador == identificador:
                return elemento
        raise NoEncontradoError(f"No existe {entidad} con el identificador {identificador}.")

    def buscar_cliente(self, identificador):
        return self._buscar(self.__clientes, identificador, "un cliente")

    def buscar_servicio(self, identificador):
        return self._buscar(self.__servicios, identificador, "un servicio")

    def buscar_reserva(self, identificador):
        return self._buscar(self.__reservas, identificador, "una reserva")

    def cotizar(self, servicio_id, duracion, impuesto=0, descuento=0):
        servicio = self.buscar_servicio(servicio_id)
        return servicio.calcular_costo(duracion, impuesto, descuento)

    def crear_reserva(self, cliente_id, servicio_id, duracion, impuesto=0, descuento=0):
        cliente = self.buscar_cliente(cliente_id)
        servicio = self.buscar_servicio(servicio_id)
        identificador = f"R{len(self.__reservas) + 1:03d}"
        reserva = Reserva(identificador, cliente, servicio, duracion, impuesto, descuento)
        self.__reservas.append(reserva)
        return reserva

    def confirmar_reserva(self, identificador):
        reserva = self.buscar_reserva(identificador)
        reserva.confirmar()
        return reserva

    def cancelar_reserva(self, identificador):
        reserva = self.buscar_reserva(identificador)
        reserva.cancelar()
        return reserva

    def procesar_reserva(self, identificador):
        reserva = self.buscar_reserva(identificador)
        reserva.procesar()
        return reserva

    def cerrar(self):
        self.logger.info("Cierre de Software FJ. Operaciones realizadas: %s", self.operaciones)
        for archivo in self.logger.handlers[:]:
            archivo.close()
            self.logger.removeHandler(archivo)
