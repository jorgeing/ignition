class ComprobadorOrdenesProduccionWIP:
	
	_logger = None
	_asignador_ordenes = None
	
	
	_wip_sin_orden = []
	_n_wip_sin_orden = 0
	_n_platos_no_asignados = 0
	_n_platos_reasignados = 0
	_limite_ordenes = 100000
	
	def __init__(self):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("ComprobadorOrdenesProduccionWIP")
		#self._logger.activaLogDebug()
		self._asignador_ordenes = fd.ordenesproduccion.AsignadorOrdenProduccion.obtieneAsignadorConUUID()
		self._ejecutador_named_queries = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		
	def compruebaWipYAsignaOrdenes(self):
		self._logger.logInfo("Inicio comprobador de ordenes de produccion")
		self._obtieneWipSinOrdenProduccion()
		
		if self._hayWipSinOrdenProduccion():
			self._intentaAsignarOrdenAWip()
			
		self._logger.logInfo("Fin comprobador de ordenes. Platos sin orden detectados: " + str(self._n_wip_sin_orden) + " - Platos reasignados: "+str(self._n_platos_reasignados))
	
	def _obtieneWipSinOrdenProduccion(self):
		"FD/OrdenesProduccionScada/ObtieneWipSinOrdenProduccion"
		query = "select * from rfid.esos_wip_serial_numbers_screens ewsns where production_order_id_detailed = '' and sku not like '' and creation_line in (1,2)"
		self._wip_sin_orden = system.db.runQuery(query)
		self._n_wip_sin_orden = self._wip_sin_orden.getRowCount()
		self._reiniciaContadoresAsignacion()
	
	def _reiniciaContadoresAsignacion(self):
		self._n_platos_no_asignados = 0
		self._n_platos_reasignados = 0
	
	def _hayWipSinOrdenProduccion(self):
		return self._wip_sin_orden and self._wip_sin_orden.getRowCount()>0
	
	def _intentaAsignarOrdenAWip(self):
		for plato in self._wip_sin_orden:
			self._intentaAsignarOrdenAPlato(plato)
					
	def _intentaAsignarOrdenAPlato(self, plato):
		self._logger.logDebug(str(plato['sku']))
		showertray_id = plato["showertray_id"]
		codigo_sku = plato["sku"]
		manejador_sku = fd.sku.ManejadorSku(codigo_sku)
		sku_molde = manejador_sku.obtieneSkuMolde()
		id_color = manejador_sku.obtieneIdColor()
		
		orden_asignada = self._asignador_ordenes.obtieneYBloqueaOrdenProduccion(sku_molde, id_color, self._limite_ordenes)
		
		self._incrementaContadoresAsignacion(orden_asignada)
				
	def _incrementaContadoresAsignacion(self, orden_asignada):
		if orden_asignada:
			self._incrementaNumeroPlatosAsignados()
		else:
			self._incrementaNumeroPlatosNoAsignados()
				
	def _incrementaNumeroPlatosNoAsignados(self):
		self._n_platos_no_asignados = self._n_platos_no_asignados + 1
		
	def _incrementaNumeroPlatosAsignados(self):
		self._n_platos_reasignados = self._n_platos_reasignados + 1