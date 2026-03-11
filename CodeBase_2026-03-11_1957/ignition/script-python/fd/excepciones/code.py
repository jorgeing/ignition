class RecursoBloqueadoException(Exception):
	"""Excepción lanzada cuando un recurso está bloqueado y no puede ser accedido."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el mensaje de error proporcionado.

		Args:
			mensaje (str): Descripción del error de bloqueo del recurso.
		"""
		super(RecursoBloqueadoException, self).__init__(mensaje)

class AccesoBaseDatosException(Exception):
	"""Excepción lanzada cuando ocurre un error al acceder a la base de datos."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el mensaje de error proporcionado.

		Args:
			mensaje (str): Descripción del error de acceso a la base de datos.
		"""
		super(AccesoBaseDatosException, self).__init__(mensaje)

class NoEncontradoException(Exception):
	"""Excepción lanzada cuando un elemento no se encuentra en el sistema."""

	def __init__(self, id):
		"""Inicializa la excepción indicando el identificador del elemento no encontrado.

		Args:
			id: Identificador del elemento que no fue encontrado.
		"""
		super(NoEncontradoException, self).__init__("Elemento con id "+str(id) + " no encontrado")

class ErrorLecturaTagException(Exception):
	"""Excepción lanzada cuando ocurre un error al leer un tag del sistema SCADA."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el mensaje de error proporcionado.

		Args:
			mensaje (str): Descripción del error de lectura del tag.
		"""
		super(ErrorLecturaTagException, self).__init__(mensaje)

class NumeroSerieException(Exception):
	"""Excepción lanzada cuando un número de serie no tiene un formato válido."""

	def __init__(self, mensaje):
		"""Inicializa la excepción indicando el número de serie inválido.

		Args:
			mensaje (str): Número de serie o descripción del error de validación.
		"""
		super(NumeroSerieException, self).__init__("Numero de serie no válido: " + mensaje)

class InventarioException(Exception):
	"""Excepción lanzada cuando no se puede actualizar el inventario."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el detalle del error de inventario.

		Args:
			mensaje (str): Descripción del motivo por el que no se pudo actualizar el inventario.
		"""
		super(InventarioException, self).__init__("No se pudo actualizar inventario: " + mensaje)

class IdSolicitadoException(Exception):
	"""Excepción lanzada cuando el ID del recurso solicitado es incorrecto."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el ID incorrecto proporcionado.

		Args:
			mensaje (str): ID incorrecto o descripción del error de identificación.
		"""
		super(IdSolicitadoException, self).__init__("El ID del recurso solicitado es incorrecto: " + mensaje)

class AsignacionRFIDInteriorPlatos(Exception):
	"""Excepción lanzada cuando no se puede asignar un RFID al interior de un plato."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el detalle del error de asignación RFID.

		Args:
			mensaje (str): Descripción del motivo por el que no se pudo asignar el RFID.
		"""
		super(AsignacionRFIDInteriorPlatos, self).__init__("No se ha podido asignar RFID al plato: " + mensaje)

class CreacionCodificacionEInstert(Exception):
	"""Excepción lanzada cuando no se puede insertar una codificación en la base de datos."""

	def __init__(self, mensaje):
		"""Inicializa la excepción con el detalle del error de inserción.

		Args:
			mensaje (str): Descripción del motivo por el que no se pudo insertar la codificación.
		"""
		super(CreacionCodificacionEInstert, self).__init__("No se ha podido insertar codificacion en la BBDD: " + mensaje)
