from sistema import SistemaGestion
from modelos import ReservaSala, AlquilerEquipo, AsesoriaEspecializada

def ejecutar_simulaciones():
    print("=== INICIANDO SIMULACIONES FASE 4 ===")
    sistema = SistemaGestion()

    # 1. Registro valido de cliente
    sistema.ejecutar(
        "Op 1: Registrar cliente valido",
        lambda: sistema.registrar_cliente("C101", "Ana Pérez", "ana@correo.com", "3001234567")
    )

    # 2. Error por correo invalido
    sistema.ejecutar(
        "Op 2: Registrar cliente correo invalido",
        lambda: sistema.registrar_cliente("C102", "Carlos Ruiz", "carlos-correo-mal", "3119876543")
    )

    # 3. Error por telefono invalido
    sistema.ejecutar(
        "Op 3: Registrar cliente telefono invalido",
        lambda: sistema.registrar_cliente("C103", "Beatriz Gómez", "beatriz@correo.com", "ABC3000000")
    )

    # 4. Registrar servicio de sala
    sistema.ejecutar(
        "Op 4: Registrar servicio de sala",
        lambda: sistema.registrar_servicio("S001", "Sala Ejecutiva", 45000, 15)
    )

    # 5. Error por servicio duplicado
    sistema.ejecutar(
        "Op 5: Intentar duplicar servicio S001",
        lambda: sistema.registrar_servicio("S001", "Sala Confe", 30000, 10)
    )

    # 6. Registrar alquiler de equipo
    def crear_equipo():
        eq = AlquilerEquipo("E001", "Laptop Gamer", 25000, 100000)
        sistema._servicios.append(eq)
        return eq

    sistema.ejecutar("Op 6: Registrar alquiler equipo", crear_equipo)

    # 7. Registrar asesoria especializada
    def crear_asesoria():
        asesoria = AsesoriaEspecializada("A001", "Consultoría Software", 80000, "Ing. Daniela")
        sistema._servicios.append(asesoria)
        return asesoria

    sistema.ejecutar("Op 7: Registrar asesoria", crear_asesoria)

    # 8. Cotizacion correcta
    sistema.ejecutar(
        "Op 8: Cotizar sala S001 por 5 horas",
        lambda: sistema.cotizar("S001", 5, impuesto=19, descuento=10)
    )

    # 9. Error cotizar servicio inexistente
    sistema.ejecutar(
        "Op 9: Cotizar servicio inexistente",
        lambda: sistema.cotizar("S999", 3)
    )

    # 10. Error cotizar duracion negativa
    sistema.ejecutar(
        "Op 10: Cotizar duracion negativa",
        lambda: sistema.cotizar("S001", -4)
    )

    print(f"\nPruebas finalizadas. Operaciones registradas: {sistema.operaciones}")
    sistema.cerrar()

if __name__ == "__main__":
    ejecutar_simulaciones()