class ConsultadorPlan:
	
	_ventana_lineas_produccion = 0
	_ejecutador_named_queries = None
	
	def __init__(self,ventana_lineas_produccion=100000):
		self._ventana_lineas_produccion = ventana_lineas_produccion
		self._ejecutador_named_queries = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		
	def obtieneTodoPlan(self):
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneTodasOrdenesPlan', {})
		
	def obtienePlanEnVentana(self):
		parametros = {'limite_ordenes':self._ventana_lineas_produccion}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneVentanaOrdenesProduccion', parametros)
		
	def obtieneOrdenesPendientesAsignar(self):
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneOrdenesProduccionPendientesAsignar', {})
		
	def obtieneOrdenesEnVentanaCompatiblesConMoldeYColor(self, sku_molde, id_color):
		parametros = {'limite_ordenes':self._ventana_lineas_produccion, 'sku_molde':sku_molde, 'id_color':id_color}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneOrdenesEnVentanaCompatiblesConMoldeYColor',parametros)
		
	def obtieneResumenPlanTurnoSku(self, timestamp_turno):
		parametros = {'campo_referencia':'sku', 'turno':timestamp_turno}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneResumenPlanTurno',parametros)
		
	def obtieneResumenPlanTurnoDescripcion(self, timestamp_turno):
		parametros = {'campo_referencia':'descripcion', 'turno':timestamp_turno}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneResumenPlanTurno',parametros)
	
	def obtieneResumenPlanVentanaSku(self):
		parametros = {'campo_referencia':'sku', 'limite_ventana': self._ventana_lineas_produccion}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneResumenPlanVentana',parametros)
		
	def obtieneResumenPlanVentanaDescripcion(self):
		parametros = {'campo_referencia':'descripcion', 'limite_ventana': self._ventana_lineas_produccion}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneResumenPlanVentana',parametros)
		
	def obtieneEstadoPlan(self):
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneEstadoPlan',{})
