
class PlanificadorOrdenes:
	
	RUTA_UPDATE_FECHAS_ORDEN = 'FD/PlanificacionProduccion/PlanificacionManual/ActualizaFechasOrden'
	
	def __init__(self, ordenes_produccion, fecha_inicio, turno_inicio):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._ordenes_produccion = ordenes_produccion
		self._datetime_inicio = self._obtieneDatetimeTurno(fecha_inicio, turno_inicio)
	
	def _obtieneDatetimeTurno(self, fecha, turno):
		hora_turno = self._obtieneHoraTurno(turno)
		datatime_turno = fecha + ' ' + hora_turno
		return datatime_turno
		
	def _obtieneHoraTurno(self, turno):
		hora_turno = ''
		if turno == 'mañana':
			hora_turno = '06:00:00'
		elif turno == 'tarde':
			hora_turno = '14:00:00'
		else:
			hora_turno = '22:00:00'
		return hora_turno
	
	def planificaOrdenes(self):
		for orden in self._ordenes_produccion:
			parametros_orden = self._obtieneParametrosOrden(orden)
			self._db.ejecutaNamedQuery(self.RUTA_UPDATE_FECHAS_ORDEN, parametros_orden)
	
	def _obtieneParametrosOrden(self, orden):
		parametros_orden = {
			'orden_produccion': orden['prodorderdetailed'],
			'inicio_estimado': self._datetime_inicio
		}
		return parametros_orden

class BorradorOrdenes:
	
	RUTA_DELETE_ORDEN = 'FD/PlanificacionProduccion/PlanificacionManual/EliminaOrden'
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = system.util.getLogger('BorradorOrdenes')
	
	def eliminaOrdenes(self, listado_id_ordenes):
		for id_orden in listado_id_ordenes:
			self._db.ejecutaNamedQuery(self.RUTA_DELETE_ORDEN, {'orden_produccion': id_orden})
	
	def eliminaOrden(self, id_orden):
		self._db.ejecutaNamedQuery(self.RUTA_DELETE_ORDEN, {'orden_produccion': id_orden})

class ArchivadorOrdenes:
	
	RUTA_INSERT_ARCHIVAR = 'FD/PlanificacionProduccion/PlanificacionManual/ArchivaOrdenFinalizada'
	RUTA_SELECT_INFO_ORDEN = 'FD/PlanificacionProduccion/PlanificacionManual/ObtieneInfoOrden'
	RUTA_SELECT_ORDENES_TURNO = 'FD/PlanificacionProduccion/PlanificacionManual/ObtieneOrdenesDeTurnoAArchivar'
	RUTA_SELECT_ORDENES_CANDIDATAS_ARCHIVAR = 'FD/PlanificacionProduccion/PlanificacionManual/ObtieneOrdenesCandidatasAArchivarPorTiempo'
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def archivaOrdenes(self, ordenes_produccion):
		for orden in ordenes_produccion:
			self._insertaOrdenEnHistorico(orden)
			self._eliminaOrdenEnOrigen(orden)
	
	def archivaTurnoCompleto(self, fecha, turno):
		datatime_turno = self._obtieneDatetimeTurno(fecha, turno)
		ordenes_en_turno = self._obtieneOrdenesDelTurno(datatime_turno)
		self.archivaOrdenes(ordenes_en_turno)
	
	def archivaOrdenesMasivo(self, horas_margen):
		ordenes_candidatas = self._obtieneOrdenesCandidatasArchivar(horas_margen)
		self.archivaOrdenes(ordenes_candidatas)
	
	def _insertaOrdenEnHistorico(self, orden):
		parametros_orden = self._obtieneParametrosOrden(orden)
		self._db.ejecutaNamedQuery(self.RUTA_INSERT_ARCHIVAR, parametros_orden)
	
	def _obtieneParametrosOrden(self, orden):
		info_orden = self._obtieneInfoOrden(orden)
		if info_orden is None:
			return None
		parametros_orden = {
		  "codemp": info_orden['codemp'],
		  "pordorder": info_orden['pordorder'],
		  "referencia": info_orden['referencia'],
		  "cantidadtotal": info_orden['cantidadtotal'],
		  "unidadesproducidas": info_orden['unidadesproducidas'],
		  "pendientes": info_orden['pendientes'],
		  "nomcli": info_orden['nomcli'],
		  "codcli": info_orden['codcli'],
		  "codped": info_orden['codped'],
		  "codeje": info_orden['codeje'],
		  "codser": info_orden['codser'],
		  "description": info_orden['description'],
		  "prodorderdetailed": info_orden['prodorderdetailed'],
		  "archiveid": info_orden['archiveid'],
		  "archiverecordid": info_orden['archiverecordid'],
		  "productionline": info_orden['productionline'],
		  "codejeped": info_orden['codejeped'],
		  "codserped": info_orden['codserped'],
		  "linped": info_orden['linped'],
		  "firstlaunchdate": info_orden['firstlaunchdate'],
		  "inicioestimado": info_orden['inicioestimado'],
		  "finestimado": info_orden['finestimado'],
		  "estimated_finish_date_full_order": info_orden['estimated_finish_date_full_order'],
		  "motivo_archivo": self._obtieneMotivoArchvio(orden)
		}
		return parametros_orden
	
	def _obtieneInfoOrden(self, orden):
		info_orden_datset = self._db.ejecutaNamedQuery(self.RUTA_SELECT_INFO_ORDEN, {'pordorder': orden['prodorderdetailed']})
		if info_orden_datset.getRowCount() == 0:
			return None
		info_orden = info_orden_datset[0]
		return info_orden
		
	def _eliminaOrdenEnOrigen(self, orden):
		id_orden = orden['prodorderdetailed']
		BorradorOrdenes().eliminaOrden(id_orden)
		
	def _obtieneDatetimeTurno(self, fecha, turno):
		hora_turno = self._obtieneHoraTurno(turno)
		datatime_turno = fecha + ' ' + hora_turno
		return datatime_turno
		
	def _obtieneHoraTurno(self, turno):
		hora_turno = ''
		if turno == 'mañana':
			hora_turno = '06:00:00'
		elif turno == 'tarde':
			hora_turno = '14:00:00'
		else:
			hora_turno = '22:00:00'
		return hora_turno
		
	def _obtieneOrdenesDelTurno(self, datatime_turno):
		return self._db.ejecutaNamedQuery(self.RUTA_SELECT_ORDENES_TURNO, {'turno': datatime_turno})
	
	def _obtieneMotivoArchvio(self, orden):
	    try:
	        valor = orden['motivo_archivo']
	    except Exception:
	        return 'Finalizada'
	    
	    return valor or 'Finalizada'
	
	def _obtieneOrdenesCandidatasArchivar(self, horas_margen):
		turno_actual = fd.utilidades.turnoproduccion.DatosTurno(system.date.now()).obtieneTimestampInicio()
		parametros = {
			'turno': turno_actual,
			'horas_margen': horas_margen
		}
		ordenes_candidatas = self._db.ejecutaNamedQuery(self.RUTA_SELECT_ORDENES_CANDIDATAS_ARCHIVAR, parametros)
		
		return ordenes_candidatas

class GestorUrgenciaOrdenes:
	
	RUTA_ACTUALIZA_URGENCIA = 'FD/PlanificacionProduccion/PlanificacionManual/ActualizaUrgenciaOrden'
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def actualizaUrgencia(self, ordenes_produccion):
		for orden in ordenes_produccion:
			self._db.ejecutaNamedQuery(self.RUTA_ACTUALIZA_URGENCIA, {'pordorder': orden['prodorderdetailed']})
		
	
	