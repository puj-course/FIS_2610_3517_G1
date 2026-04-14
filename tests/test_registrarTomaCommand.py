from backend.services.toma_service import TomaService
from backend.commands.regisToma_command import RegisToma_command
from backend.commands.invoker import CommandInvoker


def main():
    try:
        receiver = TomaService()

        command = RegisToma_command(
            receiver=receiver,
            paciente_id=2,
            medicamento_id=1,
            recordatorio_id=1,
            fecha_programada="2026-04-12 08:00:00",
            fecha_hora_toma="2026-04-12 08:03:00",
            estado="tomada",
            observaciones="Prueba manual desde test_registrar_toma_command.py"
        )

        invoker = CommandInvoker()
        invoker.set_command(command)

        resultado = invoker.run()

        print("Resultado exitoso:")
        print(resultado)

    except ValueError as e:
        print("Error de validación:")
        print(str(e))

    except LookupError as e:
        print("Error de búsqueda:")
        print(str(e))

    except FileExistsError as e:
        print("Error de conflicto/duplicado:")
        print(str(e))

    except RuntimeError as e:
        print("Error interno:")
        print(str(e))

    except Exception as e:
        print("Error inesperado:")
        print(str(e))


if __name__ == "__main__":
    main()
