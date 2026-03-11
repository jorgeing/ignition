
class TareasProgramadasOrdenesProduccion:
	_loggerBase = fd.utilidades.LoggerBase("GestorOrdenesProduccionPostprocesados")
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def actualizaInfoRegistrosPendientesAsignarOrdenClave(self):
		logger = _loggerBase.obtieneLoggerEstandarizado("actualizaInfoRegistrosPendientesAsignarOrdenClave", fd.utilidades.LoggerEstandarizado.LOG_DEBUG)
		
		ordenes_pendientes_procesar = self._obtieneColaRegistrosPendientesAsignarOrdenProduccion()
		logger.logDebug('Ordenes pendientes de procesar: '+str(data_production_orders_cut))
		
		for orden in ordenes_pendientes_procesar:
			self._procesaOrdenPendiente(orden)
				
				
	def _obtieneColaRegistrosPendientesAsignarOrdenProduccion(self):
		query_cola_ordenes_pendientes = 'select * from rfid.queue_of_manually_launched_orders'
		cola_ordenes_pendientes = system.db.runQuery(query_cola_ordenes_pendientes, 'FactoryDB')
		return cola_ordenes_pendientes
		
		
	def _procesaOrdenPendiente(self, orden):
		try:
			indx = int(orden["indx"])
			registro_neworders = self._obtieneRegistroNewordersDeClavei(indx)

			self._insertaRegistroNewordersInfoEnClavei(orden, registro_neworders)
			logger.logDebug('Orden procesada: ' + str(orden) + ' // ' + str(registro_neworders))
			
			self._actualizaOrdProdCab()
			logger.logDebug("Actualizado ordprodcab:"+ str(orden) + ' // ' + str(registro_neworders))
			
			self._eliminaOrdenDeColaPendientesAsignarOrdenProduccion(self, indx)
		
		except Exception as e:
			raise e
			
		
		
	def _obtieneRegistroNewordersDeClavei(self, indx ):
		query_neworders = 'SELECT trim(CodEmp) as codemp , trim(CodSer) as codser, trim(SeriePedido) as codserped  , CodEje as codeje  , NumeroOrden as numord from FDOS_NEWORDERS fn where ID = ? and estado != 99'
		datos_neworders = system.db.runPrepQuery(query_neworders, [indx], 'ClaveiDB')
		if datos_neworders.getRowCount>0:
			return datos_neworders[0]
		else:
			raise Exception("_obtieneRegistroNewordersDeClavei - No se ha encontrado la orden en Clavei con indice: "+ str(indx))
		
		
	def _insertaRegistroNewordersInfoEnClavei(self, orden, registro_neworders):
		indx = int(orden["indx"])
		fecinicio = system.date.format(orden["start_date"])
		fecfin = system.date.format(orden["due_date"])
		id_orden_produccion = fd.utilidades.construyeIdOrdenProduccion(registro_neworders["codemp"], registro_neworders["codeje"], registro_neworders["numorden"])
			
		params_insert_newordersinfo = self._generaParametrosInsertNewordersInfo(orden, registro_neworders)
		
		try:
			update = self._db.ejecutaNamedQuery('FD/PlanificacionProduccion/InsertarOrdenProduccionInfo', params_insert_newordersinfo)
		except:
			raise Exception("_insertaRegistroNewordersInfoEnClavei - No se ha podido actualizar orden de produccion:" +str(params_insert_newordersinfo))
	
	def _generaParametrosInsertNewordersInfo(self, orden, registro_neworders):
		params_insert_newordersinfo = {
			"PlanDate":fecinicio,
			"FinalProductOrder":str(orden["final_prodorder"]),
			"FecEstimada":fecinicio,
			"FecEstimadaFin":fecfin,
			"linped":int(orden["linped"]),
			"CodArt":str(orden["sku"]),
			"CodPed":str(int(registro_neworders["numord"])),
			"exactprodorder":str(id_orden_produccion),
			"CodEje":str(registro_neworders["codeje"]),
			"CodEmp":str(registro_neworders["codemp"]),
			"codserped":str(registro_neworders["codserped"]),
			"Generador":'scada'
		}
		return params_insert_newordersinfo
		
	def _actualizaOrdProdCab(self, orden, registro_neworders):
		try:
			params_ordprodcab = self._generaParametrosActualizaOrdProdCab(orden, registro_neworders)
		
			self._db.ejecutaNamedQuery('PlanificacionProduccion/ActualizaOrdProdCabDesdeInfo', params_ordprodcab)
		except Exception as e:
			raise Exception("_actualizaOrdProdCab - No se ha podido actualizar Ordprodcab con datos: " + str(orden)+ " // " + str(registro_neworders))
			
	def _generaParametrosActualizaOrdProdCab(self, orden, registro_neworders):
		
		fecinicio = system.date.format(orden["start_date"])
		params_ordprodcab= {
				'codemp':str(registro_neworders["codemp"]), 
				'codeje':str(registro_neworders["codeje"]),
				'codser':str(registro_neworders["codser"]),
				'numord':int(registro_neworders["numord"]), 
				'linped':int(orden["linped"]),
				'obs': str(orden["observation"]),
				'fecestimadaini':fecinicio
			}
		
		return params_ordprodcab
			
	def _eliminaOrdenDeColaPendientesAsignarOrdenProduccion(self, indx):
		query_eliminar = 'delete from rfid.queue_of_manually_launched_orders where indx = ?'
		eliminados = system.db.runPrepUpdate(query_delete, [indx], "FactoryDB")
		if eliminados == 0:
			raise Exception("_eliminaOrdenDeColaPendientesAsignarOrdenProduccion - No se ha podido eliminar la orden con índice: "+ indx)
	
	def _actualizarOrdenesProduccionClavei():
		self._db.ejecutaNamedQuery('FD/PlanificacionProduccion/GeneraTablaOrdenesProduccionClavei')