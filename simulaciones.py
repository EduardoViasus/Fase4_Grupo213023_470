from datetime import datetime, timedelta
from sistema import SistemaGestion
from modelos import AlquilerEquipo, AsesoriaEspecializada


def ejecutar_simulaciones():
    print("=== OPERACIONES OPCIONALES FASE 4 ===")
    try:
        sistema = SistemaGestion()
    except OSError as error:
        print(f"No se pudo abrir el archivo de logs: {error}")
        return 1

    def crear_equipo():
        equipo = AlquilerEquipo("E001", "Laptop Gamer", 25000, 100000)
        return sistema.agregar_servicio(equipo)

    def crear_asesoria():
        asesoria = AsesoriaEspecializada("A001", "Consultoría Software", 80000, "Ing. Daniela")
        return sistema.agregar_servicio(asesoria)

    ahora = datetime.now()
    fecha = (ahora + timedelta(days=1)).strftime("%d/%m/%Y")
    siguiente = (ahora + timedelta(days=2)).strftime("%d/%m/%Y")
    pasada = (ahora - timedelta(days=1)).strftime("%d/%m/%Y")

    def comprobar_disponibilidad(servicio_id, dia, hora, duracion, esperado):
        disponible = sistema.consultar_disponibilidad(servicio_id, dia, hora, duracion)
        if disponible != esperado:
            raise AssertionError(f"Se esperaba disponibilidad {esperado}, se obtuvo {disponible}.")
        return "Disponible" if disponible else "Ocupado"

    # Descripción, acción y resultado de éxito/error esperado.
    operaciones = [
        ("Registrar cliente válido", lambda: sistema.registrar_cliente(
            "C101", "Ana Pérez", "ana@correo.com", "3001234567"), True),
        ("Registrar cliente con correo inválido", lambda: sistema.registrar_cliente(
            "C102", "Carlos Ruiz", "carlos-correo-mal", "3119876543"), False),
        ("Registrar cliente con teléfono inválido", lambda: sistema.registrar_cliente(
            "C103", "Beatriz Gómez", "beatriz@correo.com", "ABC3000000"), False),
        ("Registrar un segundo cliente válido", lambda: sistema.registrar_cliente(
            "C102", "Carlos Ruiz", "carlos@correo.com", "3119876543"), True),
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
        ("Crear R001: cliente uno, sala de 10:00 a 12:00", lambda: sistema.crear_reserva(
            "C101", "S001", 2, fecha=fecha, hora="10:00"), True),
        ("Comprobar que el horario de R001 está ocupado", lambda: comprobar_disponibilidad(
            "S001", fecha, "10:00", 2, False), True),
        ("Rechazar al cliente dos en el mismo horario", lambda: sistema.crear_reserva(
            "C102", "S001", 2, fecha=fecha, hora="10:00"), False),
        ("Rechazar un cruce parcial a las 11:00", lambda: sistema.crear_reserva(
            "C102", "S001", 2, fecha=fecha, hora="11:00"), False),
        ("Rechazar un horario que contiene a R001", lambda: sistema.crear_reserva(
            "C102", "S001", 4, fecha=fecha, hora="09:00"), False),
        ("Crear R002 justo cuando termina R001", lambda: sistema.crear_reserva(
            "C102", "S001", 1, fecha=fecha, hora="12:00"), True),
        ("Crear R003 de equipo por un día", lambda: sistema.crear_reserva(
            "C101", "E001", 1, fecha=fecha, hora="10:00"), True),
        ("Rechazar cruce de equipo al día siguiente", lambda: sistema.crear_reserva(
            "C102", "E001", 1, fecha=siguiente, hora="09:00"), False),
        ("Rechazar finalización anticipada sin observación", lambda: sistema.finalizar_reserva("R001"), False),
        ("Cancelar R001 y liberar su horario", lambda: sistema.cancelar_reserva("R001"), True),
        ("Comprobar que la cancelación libera el intervalo", lambda: comprobar_disponibilidad(
            "S001", fecha, "10:00", 2, True), True),
        ("Crear R004 para el cliente dos en el horario liberado", lambda: sistema.crear_reserva(
            "C102", "S001", 2, fecha=fecha, hora="10:00"), True),
        ("Rechazar otra cancelación de R001", lambda: sistema.cancelar_reserva("R001"), False),
        ("Rechazar finalizar una reserva cancelada", lambda: sistema.finalizar_reserva("R001"), False),
        ("Crear R005 de la misma sala en otra fecha", lambda: sistema.crear_reserva(
            "C101", "S001", 2, fecha=siguiente, hora="10:00"), True),
        ("Rechazar una observación vacía", lambda: sistema.finalizar_reserva(
            "R005", observacion="   \n  "), False),
        ("Finalizar R005 anticipadamente con observación", lambda: sistema.finalizar_reserva(
            "R005", observacion="El cliente solicitó terminar antes del tiempo reservado."), True),
        ("Comprobar que la finalización libera el horario restante", lambda: comprobar_disponibilidad(
            "S001", siguiente, "10:00", 2, True), True),
        ("Rechazar otra finalización de R005", lambda: sistema.finalizar_reserva(
            "R005", observacion="Segundo intento."), False),
        ("Rechazar fecha inexistente", lambda: sistema.crear_reserva(
            "C101", "S001", 2, fecha="31/02/2099", hora="10:00"), False),
        ("Rechazar hora incorrecta", lambda: sistema.crear_reserva(
            "C101", "S001", 2, fecha=fecha, hora="25:00"), False),
        ("Rechazar una reserva en el pasado", lambda: sistema.crear_reserva(
            "C101", "S001", 2, fecha=pasada, hora="10:00"), False),
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
