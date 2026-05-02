from models.caja import Caja

class CajaService:
    def __init__(self):
        self.caja: Caja = None

    def abrir(self, caja: Caja):
        self.caja = caja
        return caja

    def cerrar(self):
        self.caja = None
        return True

    def obtener(self):
        return self.caja
