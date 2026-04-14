####################################################################################
#	Forma minima que todo comando debe seguir.
#
#####################################################################################

class Command:
    def execute(self):
        raise NotImplementedError("El comando debe implementar execute()")
