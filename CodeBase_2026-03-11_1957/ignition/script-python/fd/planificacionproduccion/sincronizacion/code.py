class SincronizadorPlanProduccion():
	
	_logger = None
	constructor_sql = fd.utilidades.sql.ConstructorSQL
	_plan_consultado = []
	_string_valores_insertar = ""
	_transaccion = ""
	
	_named_queries_scada = None
	_named_queries_clavei = None
	
	def __init__(self, ):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("SincronizadorPlanProduccion")
		self._logger.activaLogDebug()
		self._named_queries_scada = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("FactoryDB", "CodeBase")
		self._named_queries_clavei = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("ClaveiDB", "CodeBase")
		
	def sincronizaPlan(self):
		try:
			self._iniciaTransaccionScada()
			self._logger.logDebug("Iniciando consulta plan")
			self._consultaPlanEnClavei()
			self._importaPlanAScada()
			self._ejecutaActualizacionOrdenesProduccion()
			
			self._commitTransaccionScada()
		except Exception as e:
			self._logger.logError("Error actualizando plan: "+ str(e))
			self._rollbackTransaccionScada()
			raise Exception("Error actualizando plan: "+ str(e))
		
	def _iniciaTransaccionScada(self):
		self._transaccion = self._named_queries_scada.iniciaTransaccion(isolation_level = system.db.SERIALIZABLE, timeout = 60000)
		
	def _commitTransaccionScada(self):
		self._named_queries_scada.commitTransaccion()
		
	def _rollbackTransaccionScada(self):
		self._named_queries_scada.rollbackTransaccion()
		
	def _importaPlanAScada(self):
		self._logger.logDebug("Limpiando plan anterior")
		self._limpiaPlanEnScada()
		self._logger.logDebug("Actualizando plan")
		self._insertaPlanEnScada()
		
	def _consultaPlanEnClavei(self):
		cod_emp = fd.globales.ParametrosGlobales.obtieneCodEmp()
		self._plan_consultado = self._named_queries_clavei.ejecutaNamedQuery('FD/ConsultasClavei/ObtieneOrdenesProduccionAllLines', {"codemp":cod_emp})
		if self._plan_consultado.getRowCount == 0:
			raise Exception("_obtieneOrdenesProduccionDeClavei - No se ha encontrado ordenes de produccion en Clavei")
	
	def _insertaPlanEnScada(self):
		self._construyeListadoValoresAInsertar()
		params = {'values': self._string_valores_insertar}
		self._named_queries_scada.ejecutaNamedQuery('FD/ConsultasClavei/InsertaPlanEnScada',params)
		
	def _limpiaPlanEnScada(self):
		self._named_queries_scada.ejecutaNamedQuery('FD/PlanificacionProduccion/SincronizacionPlan/LimpiaPlan', {})
	
	def _ejecutaActualizacionOrdenesProduccion(self):
		self._eliminaOrdenesCanceladasPrevias()
		self._actualizaOrdenesCreadasOModificadasConPlan()
		self._actualizaOrdenesCanceladasPlan()
	
	def _eliminaOrdenesCanceladasPrevias(self):
		canceladas = self._named_queries_scada.ejecutaNamedQuery('FD/PlanificacionProduccion/SincronizacionPlan/EliminaOrdenesCanceladasPrevias',{})
		self._logger.logInfo("Ordenes canceladas previas eliminadas" + str(canceladas))
	
	def _actualizaOrdenesCreadasOModificadasConPlan(self):
		actualizadas = self._named_queries_scada.ejecutaNamedQuery('FD/PlanificacionProduccion/SincronizacionPlan/ActualizaOrdenesConPlan',{})
		self._logger.logInfo("Ordenes insertadas o modificadas " + str(actualizadas))
		
	def _actualizaOrdenesCanceladasPlan(self):
		actualizadas = self._named_queries_scada.ejecutaNamedQuery('FD/PlanificacionProduccion/SincronizacionPlan/AcualizaOrdenesCanceladasConPlan',{})
		self._logger.logInfo("Ordenes canceladas " + str(actualizadas))
	
	def _construyeListadoValoresAInsertar(self):
		self._string_valores_insertar = self.constructor_sql.generaStringValoresParaInsertMasivo(self._plan_consultado, self._construyeMapeoColumnasTipo())
	
	
	def _construyeMapeoColumnasTipo(self):
		mapeo_columnas = [
			self.constructor_sql.creaMapeo('ProdOrderDetailed', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('PordOrder', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('Referencia', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('description', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('CantidadTotal', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('UnidadesProducidas', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('Pendientes', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('InicioEstimado', self.constructor_sql.TIPO_COLUMNA_FECHA),
			self.constructor_sql.creaMapeo('FinEstimado', self.constructor_sql.TIPO_COLUMNA_FECHA),
			self.constructor_sql.creaMapeo('ArchiveID', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('ArchiveRecordID', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('FirstLaunchTime', self.constructor_sql.TIPO_COLUMNA_FECHA),
			self.constructor_sql.creaMapeo('EstimatedFinishDateFullOrder', self.constructor_sql.TIPO_COLUMNA_FECHA),
			self.constructor_sql.creaMapeo('ProductionLine', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('NomCli', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('CodCli', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('CodPed', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('CodEje', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('CodSer', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('CodEjePed', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('CodSerPed', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('LinPed', self.constructor_sql.TIPO_COLUMNA_NUMERO),
			self.constructor_sql.creaMapeo('Observaciones', self.constructor_sql.TIPO_COLUMNA_TEXTO),
			self.constructor_sql.creaMapeo('FinalProductOrder', self.constructor_sql.TIPO_COLUMNA_TEXTO)
		]
		
		return mapeo_columnas