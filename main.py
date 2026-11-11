"""Punto de entrada: gestión de clientes y servicios de salas."""

from sistema import SistemaGestion


def main():
    try:
        sistema = SistemaGestion()
    except OSError as error:
        print(f"No se pudo crear el archivo de logs: {error}")
        print("Revisa los permisos de escritura de la carpeta del proyecto y de la carpeta temporal.")
        return
    try:
        from interfaz import Aplicacion

        ventana = Aplicacion(sistema)
        ventana.mainloop()
    except ImportError:
        sistema.logger.exception("No se pudieron importar las dependencias de la interfaz.")
        print("Instala CustomTkinter con: python -m pip install customtkinter==5.2.2")
        print("También necesitas una instalación de Python que incluya Tkinter.")
    except Exception:
        sistema.logger.exception("No se pudo iniciar o mantener la ventana principal.")
        print(f"No se pudo abrir la aplicación. Consulta el log: {sistema.ruta_log}")
    finally:
        sistema.cerrar()


if __name__ == "__main__":
    main()
