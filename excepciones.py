"""Errores propios del sistema. Todos heredan de una excepción común."""


class ErrorSistema(Exception):
    """Excepción base de Software FJ."""


class DatosInvalidosError(ErrorSistema):
    """Un dato está vacío o tiene un formato incorrecto"""


class DuplicadoError(ErrorSistema):
    """Ya existe una entidad con el mismo id."""


class NoEncontradoError(ErrorSistema):
    """No existe el cliente o servicio solicitado."""


class CalculoError(ErrorSistema):
    """El cálculo dio un valor inválido o inconsistente."""
    
class ReservaInvalidaError(ErrorSistema):
    """Error al procesar una reserva."""
    pass