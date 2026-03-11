class MonitorDeposito:
	
	_udt_deposito = {}
	_base_datos = None
	
	def __init__(self, udt_deposito):
		self._base_datos = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("FactoryDB", "CodeBase")
		self._udt_deposito = udt_deposito
		
	def obtieneUdt(self):
		return self._udt_deposito
		
	
	def obtienePlatosRestantesEstimadosConPlanActual(self):
		volumen_promedio_actual = self._obtieneVolumenPromedioPlanActual()
		densidad_actual = self._obtieneDensidadMasaActual()
		masa_restante_en_deposito = self._udt_deposito["masa_disponible_para_llenar"]
		return fd.maquinas.amasadora.calculos.calculaPlatosAPartirDeKgDeMasa(masa_restante_en_deposito, densidad_actual, volumen_promedio_actual)
		
	def _obtieneVolumenPromedioPlanActual(self):
		inicio = system.date.getDate(1900, 1, 1)
		fin = system.date.now()
		volumen = 24.0
			
		return volumen
		
	def _obtieneDensidadMasaActual(self):
		return 1.45