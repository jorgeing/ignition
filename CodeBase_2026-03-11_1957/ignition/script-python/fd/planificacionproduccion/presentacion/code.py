class PresentadorPlanEnGateway:
	
	TAG_VENTA_ORDENES_PENDIENTES = '/ventana_ordenes_pendientes_asignar'
	TAG_ESTADO_PLAN='/estado_plan'
	
	_consultador_plan = None
	_gestor_tags = None
	_path_udt = ""
	
	def __init__(self, limite_ordenes_produccion, path_udt_presentacion_plan):
		self._consultador_plan = fd.planificacionproduccion.plan.ConsultadorPlan(limite_ordenes_produccion)
		self._gestor_tags = fd.utilidades.tags.GestorTags
		self._path_udt = path_udt_presentacion_plan
		
	def actualizaPresentacionPlan(self):
		self.actualizaVentanaOrdenesPorAsignar()
		self.actualizaResumenPlanPorTurnoDescripcion()
		
	def actualizaVentanaOrdenesPorAsignar(self):
		path_ventana_ordenes = self._path_udt + self.TAG_VENTA_ORDENES_PENDIENTES
		ventana_ordenes = self._consultador_plan.obtienePlanEnVentana()
		self._gestor_tags.escribeTagsConReintento(path_ventana_ordenes, ventana_ordenes)
		
	def actualizaResumenPlanPorTurnoDescripcion(self):
		path_resumen_estado_plan = self._path_udt + self.TAG_ESTADO_PLAN
		estado_plan = self._consultador_plan.obtieneEstadoPlan()
		self._gestor_tags.escribeTagsConReintento(path_resumen_estado_plan, estado_plan)