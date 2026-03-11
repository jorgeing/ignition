import uuid

class PeticionesAsignacionOrdenes:
	
	@staticmethod
	def realizaPeticionYEsperaProceso(part_number, ventana_ordenes):
		id_p = PeticionesAsignacionOrdenes.insertaPeticion(part_number, ventana_ordenes)
		return PeticionesAsignacionOrdenes.esperaPeticionProcesada(id_p)
	
	@staticmethod	
	def insertaPeticion(part_number, ventana_ordenes):
		id_peticion = str(uuid.uuid4())
		query = 'insert into rfid.cola_asignacion_ordenes (id_peticion, t_stamp, part_number, production_order_id, procesada, ventana_ordenes) values (?, ?, ?, ?, ?, ?)'
		valores_consulta =[id_peticion, system.date.now(), part_number, None, False, ventana_ordenes]
		system.db.runPrepUpdate(query, valores_consulta)
		return id_peticion
		
	@staticmethod
	def esperaPeticionProcesada(id_peticion, ms_timeout = 1000):
		ms_transcurridos = 0
		inicio = system.date.now()
		while ms_transcurridos < ms_timeout:
			orden = PeticionesAsignacionOrdenes.recuperaPeticion(id_peticion)
			if orden and orden["procesada"]:
				return orden
			ms_transcurridos = system.date.millisBetween(inicio, system.date.now())
			
		return None
		
	@staticmethod
	def recuperaPeticion(id_peticion):
		query = 'select * from rfid.cola_asignacion_ordenes where id_peticion = ?'
		dataset = system.db.runPrepQuery(query, [id_peticion])
		if dataset.getRowCount()>0:
			orden_recuperada =  fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(dataset, 0)
			if orden_recuperada["procesada"]:
				PeticionesAsignacionOrdenes._eliminaPeticion(id_peticion)
			return orden_recuperada
		else:
			return None
			
	@staticmethod
	def _eliminaPeticion(id_peticion):
		query = 'delete from rfid.cola_asignacion_ordenes where id_peticion = ?'
		system.db.runPrepUpdate(query,[id_peticion])
		
	@staticmethod
	def peticionDesbloqueoOrden(id_orden):
		query = 'update rfid.open_production_orders_all_lines_manuales opoalm set bloqueada = false where prodorderdetailed = ?'
		system.db.runPrepUpdate(query,[id_orden])

class ProcesadorUnicoDePeticionesAsignacionOrdenes:
	
	_db = None
	_logger = None
	_plan_actual = None
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._cronometro = fd.utilidades.contrometro.CronometroTareas()
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("ProcesadorUnicoDePeticionesAsignacionOrdenes")
		
	def compruebaColaYAsignaOrdenes(self):
		
		self._desbloqueaOrdenesYaUtilizadas()
		self._cronometro.registraEvento("Ordenes desbloqueadas")
		dataset_peticiones_pendientes = self._obtienePeticionesPendientesDeProcesar()
		self._cronometro.registraEvento("Peticiones pendientes obtenidas")
		if dataset_peticiones_pendientes.getRowCount()==0:
			return
			
		self._recorrePeticionesPendientesYAsignaOrdenes(dataset_peticiones_pendientes)
		self._cronometro.registraEvento("Peticiones asignadas")
		self._logger.logInfo("Tiempos de asignacion: "+str(self._cronometro.listaEventos()))

	def _obtienePeticionesPendientesDeProcesar(self):
		query_peticiones_pendientes = 'select * from rfid.cola_asignacion_ordenes where not procesada'
		dataset_peticiones_pendientes = system.db.runPrepQuery(query_peticiones_pendientes) 
		return dataset_peticiones_pendientes
		
	def _recorrePeticionesPendientesYAsignaOrdenes(self, dataset_peticiones_pendientes):
		self._plan_actual = self._obtieneListadoOrdenesProduccion()
		self._cronometro.registraEvento("Obteniendo plan actual")
		self._logger.logInfo("Procesando peticiones asignacion de orden de produccion: "+str(dataset_peticiones_pendientes))
		for peticion in dataset_peticiones_pendientes:
			orden = self._seleccionaOrdenProduccion(peticion["part_number"],peticion["ventana_ordenes"])
			self._actualizaPeticionConOrdenAsignadaYBloqueo(peticion["id_peticion"],orden)
			
	def _obtieneListadoOrdenesProduccion(self):
		plan_actual = self._db.ejecutaNamedQuery('FD/PlanificacionProduccion/PlanificacionManual/ObtieneOrdenesPendientesDelPlanActualOrdenadas',{})
		return plan_actual
		
	def _seleccionaOrdenProduccion(self, part_number, limite_lineas):		
		ventana_real = min(limite_lineas, self._plan_actual.getRowCount())
		for i in range(ventana_real):
			orden_del_plan = self._plan_actual[i]
			part_number_plan = orden_del_plan["part_number"]
			if part_number == part_number_plan:
				self._plan_actual = system.dataset.toPyDataSet(system.dataset.deleteRow(self._plan_actual, i))
				return orden_del_plan["prodorderdetailed"]
		
	def _actualizaPeticionConOrdenAsignadaYBloqueo(self, id_peticion, orden_asignada):
		transaccion = system.db.beginTransaction("FactoryDB", timeout = 5000 )
		try:
			query_actualizacion = "UPDATE rfid.cola_asignacion_ordenes SET production_order_id = ?, procesada = True WHERE id_peticion = ?"
			system.db.runPrepUpdate(query_actualizacion, [orden_asignada, id_peticion], tx=transaccion)
			query_actualizacion_bloqueo = "UPDATE rfid.open_production_orders_all_lines_manuales SET bloqueada = True WHERE prodorderdetailed = ?"
			system.db.runPrepUpdate(query_actualizacion_bloqueo, [orden_asignada], tx= transaccion)
			system.db.commitTransaction(transaccion)
		except Exception as e:
			self._logger.logError(str(e))
			system.db.rollbackTransaction(transaccion)
		finally:
			system.db.closeTransaction(transaccion)
			
	def _desbloqueaOrdenesYaUtilizadas(self):
		query = """
					with ordenes_bloqueadas as (select * from rfid.open_production_orders_all_lines_manuales opoalm where opoalm.bloqueada ),
					ordenes_bloqueadas_ya_usadas as (
					select * from 
					ordenes_bloqueadas ob join
					rfid.showertray_lifecycle sl on ob.prodorderdetailed = sl.production_order_id_detailed 
					)
					update rfid.open_production_orders_all_lines_manuales opoalm set bloqueada = false 
					from ordenes_bloqueadas_ya_usadas obyu where opoalm.prodorderdetailed  = obyu.prodorderdetailed
					"""
		system.db.runPrepUpdate(query, [])