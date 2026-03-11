from fd.utilidades.tags import * 

class ParametrosGlobales:
	"""Clase que contiene los parámetros globales de configuración del sistema."""
	
	_codemp = '01'
	_place_id = 5
	_claveiDb = 'ClaveiDB'
	_scadaDb = 'FactoryDB'
	
	@staticmethod
	def obtieneCodEmp():
		"""Retorna el código de empresa configurado en el sistema.

		Returns:
			str: Código de empresa.
		"""
		return ParametrosGlobales._codemp
		
	@staticmethod
	def obtieneNombreBaseDatosClavei():
		"""Retorna el nombre de la base de datos de Clavei.

		Returns:
			str: Nombre de la base de datos de Clavei.
		"""
		return ParametrosGlobales._claveiDb
		
	@staticmethod
	def obtieneNombreBaseDatosScada():
		"""Retorna el nombre de la base de datos del sistema SCADA.

		Returns:
			str: Nombre de la base de datos SCADA.
		"""
		return ParametrosGlobales._scadaDb
	
	@staticmethod
	def obtieneIdFabrica():
		"""Retorna el identificador de la fábrica configurado en el sistema.

		Returns:
			int: Identificador de la fábrica.
		"""
		return ParametrosGlobales._place_id


class ParametrosEnTags:
	"""Clase que gestiona los parámetros del sistema almacenados en tags del SCADA."""
	
	PATH_TAG_LIMITE_LINEAS_PUBLICAR_PLAN = '[rfid_tags]ProdOrders/LimiteLineasPublicarPlan'
	
	@staticmethod
	def obtieneLimiteLineasOrdenesProduccion():
		"""Retorna el límite de líneas para publicar en el plan de órdenes de producción.

		Returns:
			El valor del tag que indica el número máximo de líneas a publicar.
		"""
		
		return GestorTags.leeValorDeUnTag(ParametrosEnTags.PATH_TAG_LIMITE_LINEAS_PUBLICAR_PLAN)
