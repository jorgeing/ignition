from fd.utilidades.turnoproduccion import DatosTurno


class AdherenciaPlan:
	
	RUTA_SELECT_ORDENES_PLANIFICADAS_EN_RANGO = 'FD/MetricasProduccion/ObtieneOrdenesPlanificadasEnRangoFechas'
	RUTA_SELECT_ORDENES_PRODUCIDAS_EN_RANGO = 'FD/MetricasProduccion/ObtieneOrdenesProducidasEnRangoFechas'
	RUTA_SELECT_ORDENES_PLANIFICADAS_EN_FECHA = 'FD/MetricasProduccion/ObtieneOrdenesPlanificadasEnFecha'
	RUTA_SELECT_ORDENES_PRODUCIDAS_EN_FECHA = 'FD/MetricasProduccion/ObtieneOrdenesProducidasEnFecha'
	RUTA_INSERT_ADHERENCIA = 'FD/MetricasProduccion/InsertaHistoricoAdherencia'
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
	
	def calculaAdherenciaRango(self, fecha_inicio, fecha_fin):
		ordenes_planificadas_en_rango = self._obtieneOrdenesPlanificadasEnRango(fecha_inicio, fecha_fin)
		ordenes_producidas_en_rango = self._obtieneOrdenesProducidasEnRango(fecha_inicio, fecha_fin)
		self._calculaAdherencia(ordenes_planificadas_en_rango, ordenes_producidas_en_rango)
	
	def calculaAdherenciaFecha(self, fecha):
		ordenes_planificadas_en_fecha = self._obtieneOrdenesPlanificadasEnFecha(fecha)
		print(str(ordenes_planificadas_en_fecha))
		ordenes_producidas_en_fecha = self._obtieneOrdenesProducidasEnFecha(fecha)
		print(str(ordenes_producidas_en_fecha))
		self._calculaAdherencia(ordenes_planificadas_en_fecha, ordenes_producidas_en_fecha)
	
	def _obtieneOrdenesPlanificadasEnRango(self, fecha_inicio, fecha_fin):
		params = {
			'fecha_inicio': fecha_inicio,
			'fecha_fin': fecha_fin
		}
		ordenes_planificadas = self._db.ejecutaNamedQuery(self.RUTA_SELECT_ORDENES_PLANIFICADAS_EN_RANGO, params)
		ordenes_planificadas = system.dataset.toPyDataSet(ordenes_planificadas)
		return ordenes_planificadas
	
	def _obtieneOrdenesProducidasEnRango(self, fecha_inicio, fecha_fin):
		params = {
			'fecha_inicio': fecha_inicio,
			'fecha_fin': fecha_fin
		}
		ordenes_producidas = self._db.ejecutaNamedQuery(self.RUTA_SELECT_ORDENES_PRODUCIDAS_EN_RANGO, params)
		ordenes_producidas = system.dataset.toPyDataSet(ordenes_producidas)
		return ordenes_producidas
	
	def _obtieneOrdenesPlanificadasEnFecha(self, fecha):
		ordenes_planificadas = self._db.ejecutaNamedQuery(self.RUTA_SELECT_ORDENES_PLANIFICADAS_EN_FECHA, {'fecha': fecha})
		ordenes_planificadas = system.dataset.toPyDataSet(ordenes_planificadas)
		return ordenes_planificadas
	
	def _obtieneOrdenesProducidasEnFecha(self, fecha):
		ordenes_producidas = self._db.ejecutaNamedQuery(self.RUTA_SELECT_ORDENES_PRODUCIDAS_EN_FECHA, {'fecha': fecha})
		ordenes_producidas = system.dataset.toPyDataSet(ordenes_producidas)
		return ordenes_producidas
	
	def _calculaAdherencia(self, ordenes_planificadas, ordenes_producidas):
		ordenes_por_dia = self._obtieneDiccionarioPlanificacionPorDia(ordenes_planificadas)
		ordenes_producidas_segun_plan = self._obtieneOrdenesProducidasSegunPlan(ordenes_por_dia, ordenes_producidas)
		ordenes_producidas_fuera_plan = self._obtieneOrdenesProducidasFueraPlan(ordenes_por_dia, ordenes_producidas)
		dataset_adherencias = self._generaDatasetAdherencias(ordenes_por_dia, ordenes_producidas_segun_plan, ordenes_producidas_fuera_plan)
		self._insertaAdherenciaEnHistorico(dataset_adherencias)
	
	def _obtieneDiccionarioPlanificacionPorDia(self, ordenes_planificadas):
		ordenes_por_dia = {}
		for orden in ordenes_planificadas:
			fecha_plan = orden['planning_day']
			fecha_producida = DatosTurno(fecha_plan).obtieneFechaTurno()
			fecha_formateada = self._formateaFechaAString(fecha_producida)
			orden = orden['production_order_id']
			
			if fecha_formateada not in ordenes_por_dia:
				ordenes_por_dia[fecha_formateada] = set()
			
			ordenes_por_dia[fecha_formateada].add(orden)
		return ordenes_por_dia
	
	def _obtieneOrdenesProducidasSegunPlan(self, ordenes_por_dia, ordenes_producidas):
		ordenes_producidas_en_plan_por_dia = {}
		
		for orden in ordenes_producidas:
			fecha = orden['production_day']
			fecha_formateada = self._formateaFechaAString(fecha)
			orden = orden['production_order_id']
			
			if fecha_formateada in ordenes_por_dia and orden in ordenes_por_dia[fecha_formateada]:
				ordenes_producidas_en_plan_por_dia[fecha_formateada] = ordenes_producidas_en_plan_por_dia.get(fecha_formateada, 0) + 1
		
		return ordenes_producidas_en_plan_por_dia
	
	def _obtieneOrdenesProducidasFueraPlan(self, ordenes_por_dia, ordenes_producidas):
		ordenes_producidas_fuera_plan_por_dia = {}
		
		for orden in ordenes_producidas:
			fecha = orden['production_day']
			fecha_formateada = self._formateaFechaAString(fecha)
			orden = orden['production_order_id']
			
			if fecha_formateada in ordenes_por_dia and orden not in ordenes_por_dia[fecha_formateada]:
				ordenes_producidas_fuera_plan_por_dia[fecha_formateada] = ordenes_producidas_fuera_plan_por_dia.get(fecha_formateada, 0) + 1
		
		return ordenes_producidas_fuera_plan_por_dia
	
	def _formateaFechaAString(self, fecha):
		return system.date.format(fecha, "yyyy-MM-dd")
	
	def _generaDatasetAdherencias(self, ordenes_por_dia, ordenes_producidas_segun_plan, ordenes_producidas_fuera_plan):
		dias = sorted(ordenes_por_dia.keys())
		
		datos_adherencia = []
		for fecha in dias:
			total_planificadas = len(ordenes_por_dia[fecha])
			total_producidas_segun_plan = ordenes_producidas_segun_plan.get(fecha, 0)
			total_producidas_fuera_plan = ordenes_producidas_fuera_plan.get(fecha, 0)
			
			if total_planificadas > 0:
				adherencia = float(total_producidas_segun_plan) / float(total_planificadas)
			else:
				adherencia = None
			
			datos_adherencia.append([fecha, total_planificadas, total_producidas_segun_plan, total_producidas_fuera_plan, adherencia])
			
		cabeceras = ["fecha", "ordenes_planificadas", "ordenes_producidas_segun_plan", "ordenes_producidas_fuera_plan", "adherencia"]
		dataset_adherencias = system.dataset.toDataSet(cabeceras, datos_adherencia)
		dataset_adherencias = system.dataset.toPyDataSet(dataset_adherencias)
		return dataset_adherencias
		
	def _insertaAdherenciaEnHistorico(self, dataset_adherencias):
		for fila in dataset_adherencias:
			params = {
                "fecha": fila['fecha'],
                "ordenes_planificadas": fila['ordenes_planificadas'],
                "ordenes_producidas_segun_plan": fila['ordenes_producidas_segun_plan'],
                "ordenes_producidas_fuera_plan": fila['ordenes_producidas_fuera_plan'],
                "adherencia": fila['adherencia']
            }
			self._db.ejecutaNamedQuery(self.RUTA_INSERT_ADHERENCIA, params)