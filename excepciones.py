"""Errores propios del sistema. Todos heredan de una excepción común."""


class ErrorSistema(Exception):
    """Excepción base de Software FJ."""


class DatosInvalidosError(ErrorSistema):
    """Un dato está vacío o tiene un formato incorrecto"""


class DuplicadoError(ErrorSistema):
    """Ya existe una entidad con el mismo id."""


class NoEncontradoError(ErrorSistema):
    """No existe el cliente, servicio o reserva solicitado."""


class CalculoError(ErrorSistema):
    """El cálculo dio un valor inválido o inconsistente."""
    
class ReservaError(ErrorSistema):
    """No fue posible procesar una reserva."""


class ReservaInvalidaError(ReservaError):
    """Error al procesar una reserva."""


class OperacionNoPermitidaError(ReservaInvalidaError):
    """El estado actual no permite realizar la operación solicitada."""


class ServicioNoDisponibleError(ReservaInvalidaError):
    """El servicio ya está ocupado por otra reserva."""
