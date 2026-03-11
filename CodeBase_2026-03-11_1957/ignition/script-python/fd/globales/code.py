from fd.utilidades.tags import * 

class ParametrosGlobales:
	
	_codemp = '01'
	_place_id = 5
	_claveiDb = 'ClaveiDB'
	_scadaDb = 'FactoryDB'
	
	@staticmethod
	def obtieneCodEmp():
		return ParametrosGlobales._codemp
		
	@staticmethod
	def obtieneNombreBaseDatosClavei():
		return ParametrosGlobales._claveiDb
		
	@staticmethod
	def obtieneNombreBaseDatosScada():
		return ParametrosGlobales._scadaDb
	
	@staticmethod
	def obtieneIdFabrica():
		return ParametrosGlobales._place_id


class ParametrosEnTags:
	
	PATH_TAG_LIMITE_LINEAS_PUBLICAR_PLAN = '[rfid_tags]ProdOrders/LimiteLineasPublicarPlan'
	
	@staticmethod
	def obtieneLimiteLineasOrdenesProduccion():
		
		return GestorTags.leeValorDeUnTag(ParametrosEnTags.PATH_TAG_LIMITE_LINEAS_PUBLICAR_PLAN)