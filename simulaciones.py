from sistema import SistemaGestion
from modelos import AlquilerEquipo, AsesoriaEspecializada


def ejecutar_simulaciones():
    print("=== OPERACIONES OPCIONALES FASE 4 ===")
    try:
        sistema = SistemaGestion()
    except OSError as error:
        print(f"No se pudo abrir el archivo de logs: {error}")
        return 1

    # Se conservan los ejemplos del pull request; el alta pasa por un método público.
    def crear_equipo():
        equipo = AlquilerEquipo("E001", "Laptop Gamer", 25000, 100000)
        return sistema.agregar_servicio(equipo)

    def crear_asesoria():
        asesoria = AsesoriaEspecializada("A001", "Consultoría Software", 80000, "Ing. Daniela")
        return sistema.agregar_servicio(asesoria)

    def cambiar_tarifa_asesoria():
        servicio = sistema.buscar_servicio("A002")
        servicio.tarifa_base = 90000
        return servicio

    # Descripción, acción y resultado de éxito/error esperado.
    # Las primeras diez operaciones corresponden a los casos del pull request.
    operaciones = [
        ("Registrar cliente válido", lambda: sistema.registrar_cliente(
            "C101", "Ana Pérez", "ana@correo.com", "3001234567"), True),
        ("Registrar cliente con correo inválido", lambda: sistema.registrar_cliente(
            "C102", "Carlos Ruiz", "carlos-correo-mal", "3119876543"), False),
        ("Registrar cliente con teléfono inválido", lambda: sistema.registrar_cliente(
            "C103", "Beatriz Gómez", "beatriz@correo.com", "ABC3000000"), False),
        ("Registrar servicio de sala", lambda: sistema.registrar_servicio(
            "S001", "Sala Ejecutiva", 45000, 15), True),
        ("Intentar duplicar servicio S001", lambda: sistema.registrar_servicio(
            "S001", "Sala Confe", 30000, 10), False),
        ("Registrar alquiler por día y con depósito", crear_equipo, True),
        ("Registrar asesoría sin preparación extra", crear_asesoria, True),
        ("Cotizar sala S001 por 5 horas", lambda: sistema.cotizar(
            "S001", 5, impuesto=19, descuento=10), True),
        ("Cotizar servicio inexistente", lambda: sistema.cotizar("S999", 3), False),
        ("Cotizar duración negativa", lambda: sistema.cotizar("S001", -4), False),
        ("Registrar tres equipos por hora y sin depósito", lambda: sistema.registrar_equipo(
            "E002", "Portátiles", 10000, deposito_garantia=0, cantidad=3, unidad="horas"), True),
        ("Registrar asesoría con media hora de preparación", lambda: sistema.registrar_asesoria(
            "A002", "Asesoría Python", 80000, "Ing. Sara", especialidad="Programación",
            horas_preparacion=0.5), True),
        ("Cotizar equipo por día con depósito", lambda: sistema.cotizar("E001", 2), True),
        ("Cotizar tres equipos por hora", lambda: sistema.cotizar("E002", 2), True),
        ("Cotizar asesoría sin preparación extra", lambda: sistema.cotizar("A001", 1), True),
        ("Cotizar asesoría con preparación extra", lambda: sistema.cotizar("A002", 1), True),
        ("Rechazar capacidad fraccionaria", lambda: sistema.registrar_servicio(
            "S002", "Sala secundaria", 30000, 2.5), False),
        ("Controlar parámetros faltantes", lambda: sistema.registrar_cliente("C104"), False),
        ("Crear reserva R001 de equipo por día", lambda: sistema.crear_reserva(
            "C101", "E001", 2, impuesto=19, descuento=10), True),
        ("Confirmar R001", lambda: sistema.confirmar_reserva("R001"), True),
        ("Rechazar servicio ocupado", lambda: sistema.crear_reserva("C101", "E001", 1), False),
        ("Completar R001 y liberar el equipo", lambda: sistema.procesar_reserva("R001"), True),
        ("Rechazar cancelación de reserva completada", lambda: sistema.cancelar_reserva("R001"), False),
        ("Crear reserva R002 de sala", lambda: sistema.crear_reserva("C101", "S001", 2), True),
        ("Rechazar procesamiento sin confirmar", lambda: sistema.procesar_reserva("R002"), False),
        ("Confirmar R002", lambda: sistema.confirmar_reserva("R002"), True),
        ("Cancelar R002 y liberar la sala", lambda: sistema.cancelar_reserva("R002"), True),
        ("Crear reserva R003 de asesoría", lambda: sistema.crear_reserva("C101", "A002", 1), True),
        ("Confirmar R003", lambda: sistema.confirmar_reserva("R003"), True),
        ("Cambiar tarifa mediante una propiedad validada", cambiar_tarifa_asesoria, True),
        ("Detectar costo inconsistente sin completar R003", lambda: sistema.procesar_reserva("R003"), False),
        ("Cancelar R003 después del error de costo", lambda: sistema.cancelar_reserva("R003"), True),
        ("Rechazar duración no finita", lambda: sistema.cotizar("S001", "nan"), False),
        ("Controlar un error aritmético inesperado", lambda: 10 / 0, False),
        ("Continuar con un cliente válido después del error", lambda: sistema.registrar_cliente(
            "C104", "Luis Gómez", "luis@correo.com", "3007654321"), True),
    ]

    coincidencias = 0
    try:
        for numero, (descripcion, accion, esperado) in enumerate(operaciones, start=1):
            correcto, resultado = sistema.ejecutar(f"Op {numero}: {descripcion}", accion)
            coincidencias += int(correcto == esperado)
            estado = "CORRECTO" if correcto else "ERROR CONTROLADO"
            revision = "ESPERADO" if correcto == esperado else "REVISAR"
            print(f"{numero:02d}. [{estado} / {revision}] {descripcion}\n    {resultado}")
        print(f"\nResultados de éxito/error esperados: {coincidencias}/{len(operaciones)}")
        print(f"Archivo de logs: {sistema.ruta_log}")
        return 0 if coincidencias == len(operaciones) else 1
    finally:
        sistema.cerrar()
        
if __name__ == "__main__":
    raise SystemExit(ejecutar_simulaciones())
