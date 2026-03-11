
class RecursoBloqueadoException(Exception):
    
    def __init__(self, mensaje):
		super(RecursoBloqueadoException, self).__init__(mensaje)
        
class AccesoBaseDatosException(Exception):
    
    def __init__(self, mensaje):
		super(AccesoBaseDatosException, self).__init__(mensaje)
		
class NoEncontradoException(Exception):
    
    def __init__(self, id):
		super(NoEncontradoException, self).__init__("Elemento con id "+str(id) + " no encontrado")
		
class ErrorLecturaTagException(Exception):
	
	def __init__(self, mensaje):
		super(ErrorLecturaTagException, self).__init__(mensaje)
		
class NumeroSerieException(Exception):
	
	def __init__(self, mensaje):
		super(NumeroSerieException, self).__init__("Numero de serie no válido: " + mensaje)
		
class InventarioException(Exception):
	
	def __init__(self, mensaje):
		super(InventarioException, self).__init__("No se pudo actualizar inventario: " + mensaje)
		
class IdSolicitadoException(Exception):
	
	def __init__(self, mensaje):
		super(IdSolicitadoException, self).__init__("El ID del recurso solicitado es incorrecto: " + mensaje) 
		
class AsignacionRFIDInteriorPlatos(Exception):
	
	def __init__(self, mensaje):
		super(AsignacionRFIDInteriorPlatos, self).__init__("No se ha podido asignar RFID al plato: " + mensaje)
		
class CreacionCodificacionEInstert(Exception):
	
	def __init__(self, mensaje):
		super(CreacionCodificacionEInstert, self).__init__("No se ha podido insertar codificacion en la BBDD: " + mensaje) 