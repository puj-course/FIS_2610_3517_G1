#es quien dispara la orden para el patron Command
class CommandInvoker:
    def __init__(self):
        self.command = None

    def set_command(self, command):
        self.command = command

    def run(self):
        if self.command is None:
            raise ValueError("No se ha configurado un comando")
        return self.command.execute()