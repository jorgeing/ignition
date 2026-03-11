from math import log, floor
from datetime import datetime, timedelta

class PlanificadorProduccion:
	
	_ordenes_pendientes = []
	_pedidos = []
	_stock = []
	_wip = []
	_moldes_disponibles = []
	_planificacion_existente = []
	
	def __init__(self):
		self._consultasPlanificacion = ConsultasPlanificacion()
		self._priorizador = Priorizador()
		self._gestorMoldes = GestorDisponibilidadMoldes()
		self._programadorTurnos = ProgramadorTurnos()
		self._escritorPlan = EscritorPlanificacion()
	
	def generaPlanificacion(self):
		self._obtieneDatosPlanificacion()
		ordenes_sin_cubrir = self._filtraOrdenesCubiertas()
		print(str(len(ordenes_sin_cubrir)))
		ordenes_priorizadas = self._anyadePrioridadOrdenes(ordenes_sin_cubrir)
		print(str(len(ordenes_priorizadas)))
		ordenes_seleccionadas, ordenes_sin_molde = self._seleccionaOrdenesPorDisponibilidadMoldes(ordenes_priorizadas)
		print(str(len(ordenes_seleccionadas)))
		print(str(len(ordenes_sin_molde)))
		planificacion = self._programaTurnosProduccion(ordenes_seleccionadas)
		self._insertaPlanificacionNueva(planificacion)
		
	def _obtieneDatosPlanificacion(self):
		self._ordenes_pendientes = self._consultasPlanificacion.obtieneOrdenesProduccionPendientes()
		self._pedidos = self._consultasPlanificacion.obtienePedidos()
		self._stock = self._consultasPlanificacion.obtieneStockActual()
		self._wip = self._consultasPlanificacion.obtieneWipActual()
		self._moldes_disponibles = self._consultasPlanificacion.obtieneMoldesDisponibles()
		self._planificacion_existente = self._consultasPlanificacion.obtienePlanificacionExistente()
	
	def _filtraOrdenesCubiertas(self): 
		sku_en_stock = self._obtieneSkuEnStock()#STOCK NO CUENTA AQUI
		sku_en_wip = self._obtieneSkuEnWIP()#WIP de SCADA
		ordenes_en_planificacion = self._obtieneOrdenesEnPlanificacion()#NO RESTARLAS, REPLANIFICARLAS
		ordenes_sin_cubrir = self._obtieneOrdenesSinCubrir(sku_en_stock, sku_en_wip, ordenes_en_planificacion)
		return ordenes_sin_cubrir
	
	def _obtieneSkuEnStock(self):
		stock_sku = {}
		for articulo in self._stock:
			sku = articulo.get('SKU')
			cantidad = articulo.get('StockActual')
			stock_sku[sku] = stock_sku.get(sku, 0) + cantidad
		return stock_sku
	
	def _obtieneSkuEnWIP(self):
		wip_sku = {}
		for articulo in self._wip:
			sku = articulo.get('sku')
			cantidad = articulo.get('cantidad', 0)
			wip_sku[sku] = wip_sku.get(sku, 0) + cantidad
		return wip_sku
	
	def _obtieneOrdenesEnPlanificacion(self):
		return set([plato['PordOrder'] for plato in self._planificacion_existente])
	
	def _obtieneOrdenesSinCubrir(self, sku_en_stock, sku_en_wip, ordenes_en_planificacion):
		ordenes_validas = []
		for orden in self._ordenes_pendientes:
			sku = orden.get('CodArt')
			orden_produccion = orden.get('NumOrd')
			cantidad_orden = orden.get('Cantidad', 0)
			
			stock_disponible = sku_en_stock.get(sku, 0)
			wip_disponible = sku_en_wip.get(sku, 0)
			
			cantidad_necesaria = cantidad_orden - stock_disponible - wip_disponible
			
			if orden_produccion not in ordenes_en_planificacion and cantidad_necesaria > 0:
				ordenes_validas.append(orden)
		return ordenes_validas
	
	def _anyadePrioridadOrdenes(self, ordenes_sin_cubrir):
		return self._priorizador.anyadePrioridad(ordenes_sin_cubrir, self._pedidos)
	
	def _seleccionaOrdenesPorDisponibilidadMoldes(self, ordenes_priorizadas):
		return self._gestorMoldes.obtieneOrdenesConDisponibilidadDeMolde(ordenes_priorizadas, self._moldes_disponibles)
	
	def _programaTurnosProduccion(self, ordenes_seleccionadas):
		return self._programadorTurnos.asignaTurnosAOrdenes(ordenes_seleccionadas)
		
	def _insertaPlanificacionNueva(self, planificacion):
		self._escritorPlan.insertaPlanificacion(planificacion)


class ConsultasPlanificacion:
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def obtieneOrdenesProduccionPendientes(self):
		return self._ejecutaConsulta('FD/PlanificadorProduccion/ObtieneOrdenesProduccionPendientes')
	
	def obtieneStockActual(self):
		return self._ejecutaConsulta('FD/PlanificadorProduccion/ObtieneStockActual')
	
	def obtienePedidos(self):
		return self._ejecutaConsulta('FD/PlanificadorProduccion/ObtienePedidosPendientes')
	
	def obtieneWipActual(self):
		return self._ejecutaConsulta('FD/PlanificadorProduccion/ObtieneWipActual')
	
	def obtieneMoldesDisponibles(self):
		return self._ejecutaConsulta('FD/PlanificadorProduccion/ObtieneMoldesActivos')
	
	def obtienePlanificacionExistente(self):
		return self._ejecutaConsulta('FD/PlanificadorProduccion/ObtienePlanificacionExitente')
	
	def _ejecutaConsulta(self, ruta_consulta, parametros = None):
		if parametros is None:
			parametros = {}
		
		resultado_dataset = self._db.ejecutaNamedQuery(ruta_consulta, parametros)
		resultado_lista = self._formateaDatasetALista(resultado_dataset)
		return resultado_lista
	
	def _formateaDatasetALista(self, dataset):
		return fd.utilidades.dataset.ConversorFormatosDataset.datasetAListaDeDiccionarios(dataset)


class Priorizador:
	
	BASE_LOGARITMICA = 2.718
	GRANULARIDAD = 1
	
	def __init__(self):
		self._fecha_actual = self._obtieneFechaActual()
	
	def anyadePrioridad(self, ordenes_produccion, pedidos):
		pedidos_indexados = self._indexaPedidosPorClaveCompuesta(pedidos)
		ordenes_priorizadas = self._obtieneOrdenesPriorizadas(ordenes_produccion, pedidos_indexados)
		return ordenes_priorizadas
	
	def _obtieneFechaActual(self):
		return datetime.now().date()
	
	def _indexaPedidosPorClaveCompuesta(self, pedidos):
		pedidos_indexados = {}
		for pedido in pedidos:
			clave_pedido = self._generaClaveCompuesta(pedido)
			pedidos_indexados[clave_pedido] = pedido
		return pedidos_indexados
	
	def _generaClaveCompuesta(self, diccionario):
		return "{}_{}_{}".format(
			diccionario.get('CodPed', ''),
			diccionario.get('CodSer', ''),
			diccionario.get('CodEje', '')
		)
	
	def _obtieneOrdenesPriorizadas(self, ordenes_produccion, pedidos_indexados):
		ordenes_priorizadas = []
		for orden in ordenes_produccion:
			orden_priorizada = self._asignaPrioridadAOrden(orden, pedidos_indexados)
			ordenes_priorizadas.append(orden_priorizada)
		return ordenes_priorizadas
	
	def _asignaPrioridadAOrden(self, orden, pedidos_indexados):
		clave_orden = self._generaClaveCompuesta(orden)
		cpsd = self._obtieneCPSD(clave_orden, pedidos_indexados)
		bufer = self._calculaBuffer(cpsd)
		prioridad = self._calculaPrioridad(bufer)
		
		orden_priorizada = orden.copy()
		orden_priorizada['buffer'] = bufer
		orden_priorizada['prioridad'] = prioridad
		return orden_priorizada
	
	def _obtieneCPSD(self, clave_orden, pedidos_indexados):
		pedido = pedidos_indexados.get(clave_orden)
		if pedido and pedido.get('FecSer'):
			cpsd = self._parseaFecha(pedido['FecSer'])
		else:
			cpsd = None
		return cpsd
	
	def _parseaFecha(self, fecha):
		try:
			return datetime.strptime(fecha[:10], '%Y-%m-%d').date()
		except:
			try:
				return datetime.strptime(fecha[:10], "%d/%m/%Y").date()
			except:
				return None
	
	def _calculaBuffer(self, cpsd):
		if cpsd is not None:
			bufer = (cpsd - self._fecha_actual).days
		else:
			bufer = 9999
		return bufer
	
	def _calculaPrioridad(self, bufer):
		try:
			if bufer >= 0:
				return floor(self.GRANULARIDAD * log(bufer + 1, self.BASE_LOGARITMICA))
			else:
				return -floor(self.GRANULARIDAD * log(-(bufer - 1), self.BASE_LOGARITMICA))
		except:
			return 999

class GestorDisponibilidadMoldes:
	
	PORCENTAJE_DISPONIBILIDAD = 100 #PARAMETRO MODIFICABLE A POSTERIORI
	MAX_VUELTAS = 30 #PARAMETRO MODIFICABLE A POSTERIORI
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
	
	def obtieneOrdenesConDisponibilidadDeMolde(self, ordenes_priorizadas, moldes_disponibles):
		moldes_indexados = self._indexaMoldesDisponiblesPorClaveCompuesta(moldes_disponibles)
		ordenes_seleccionadas, ordenes_sin_molde = self._asignaOrdenesAMoldesDisponibles(ordenes_priorizadas, moldes_indexados)
		return ordenes_seleccionadas, ordenes_sin_molde
	
	def _indexaMoldesDisponiblesPorClaveCompuesta(self, moldes_disponibles):
		moldes_indexados = {}
		for molde in moldes_disponibles:
			sku = molde.get('molde', '')
			disponibilidad = self._calculaDisponibilidadMolde(molde)
			moldes_indexados[sku] = disponibilidad
		return moldes_indexados
	
	def _calculaDisponibilidadMolde(self, molde):
		activos = molde.get('activos', 0)
		disponibilidad = activos * self.MAX_VUELTAS * (self.PORCENTAJE_DISPONIBILIDAD/100.0)
		disponibilidad_redondeada = self._redondeaDisponiblidadMoldes(disponibilidad)
		return disponibilidad_redondeada
	
	def _redondeaDisponiblidadMoldes(self, disponibilidad):
		if disponibilidad > 0 and disponibilidad <= 1:
			disponibilidad_redondeada = 1
		else:
			disponibilidad_redondeada = int(floor(disponibilidad))
		return disponibilidad_redondeada
	
	def _asignaOrdenesAMoldesDisponibles(self, ordenes, moldes_disponibles): #Filtrar Corte (102) y Dekor (103)
		seleccionadas = []
		sin_molde = []
		for orden in ordenes:
			sku_molde = self._obtieneSkuMoldeDeOrden(orden)
			cantidad_orden = orden.get('Cantidad', 0)
			if sku_molde in moldes_disponibles:
				capacidad = moldes_disponibles[sku_molde]
				if capacidad >= cantidad_orden:
					seleccionadas.append(orden)
				else:
					sin_molde.append(orden)
			else:
				sin_molde.append(orden)
		return seleccionadas, sin_molde
	
	def _obtieneSkuMoldeDeOrden(self, orden):
		sku_plato = orden.get('CodArt')
		resultado_sku_molde = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneSkuMoldeDeSkuPlato', {'sku_plato': sku_plato})
		if resultado_sku_molde:
			sku_molde = resultado_sku_molde.getValueAt(0, 'moldsku')
		else:
			sku_molde = 'Sin Resultado'
		return sku_molde
	
class ProgramadorTurnos:
	
	CAPACIDAD_TURNO = 400 #PARAMETRO MODIFICABLE A POSTERIORI
	
	def __init__(self):
		self._turnos = self._defineTurnos()
		self._fecha_actual = self._calculaFechaInicio()
	
	def _defineTurnos(self):
		duracion_horas = 8
		return [
			{'nombre': 'Noche', 'hora': 22, 'duracion':duracion_horas},
			{'nombre': 'Mañana', 'hora': 6, 'duracion':duracion_horas},
			{'nombre': 'Tarde', 'hora': 14, 'duracion':duracion_horas}
		]
	
	def _calculaFechaInicio(self):
		ahora = datetime.now()
		domingo_22h = self._obtieneFechaDomingo(ahora)
		viernes_22h = self._obtieneFechaViernes(domingo_22h)
		
		if ahora <= domingo_22h:
			fecha_inicio =  domingo_22h
		elif ahora > viernes_22h:
			fecha_incio = self._obtieneProximoDomingo(domingo_22h)
		else:
			fecha_inicio = self._obtieneProximoInicioTurno(ahora)
		return fecha_inicio
		
	
	def _obtieneFechaDomingo(self, ahora):
		delta = (6 - ahora.weekday()) % 7
		domingo = ahora + timedelta(days=delta)
		domingo_formateado = domingo.replace(hour=22, minute=0, second=0, microsecond=0)
		return domingo_formateado
	
	def _obtieneFechaViernes(self, domingo_22h):
		return domingo_22h + timedelta(days=5)
	
	def _obtieneProximoDomingo(self, domingo_22h):
		return domingo_22h + timedelta(days=7)
	
	def _obtieneProximoInicioTurno(self, ahora):
		turno = self._obtieneTurno(ahora)
		inicio_turno = ahora.replace(hour=turno["hora"], minute=0, second=0, microsecond=0)
		if ahora > inicio_turno:
			proximo_inicio = self._avanzaTurno(inicio_turno, turno)
		else:
			proximo_inicio = inicio_turno
		return proximo_turno
	
	def asignaTurnosAOrdenes(self, ordenes_seleccionadas):
		ordenes_pendientes_ordenadas = self._ordenaOrdenesSeleccionadasPorPrioridad(ordenes_seleccionadas)
		ordenes_planificadas = self._planificaOrdenesPendientes(ordenes_pendientes_ordenadas)
		return ordenes_planificadas
	
	def _ordenaOrdenesSeleccionadasPorPrioridad(self, ordenes):
		return sorted(ordenes, key=lambda o: o.get("prioridad", 0))
	
	def _planificaOrdenesPendientes(self, ordenes_pendientes):
		planificadas = []
		while ordenes_pendientes:
			turno = self._obtieneTurno(self._fecha_actual)
			print(turno['nombre'])
			bloque = self._llenaTurno(ordenes_pendientes)
			for orden in bloque:
				orden_planificada = orden.copy()
				orden_planificada['fecha_programada'] = self._fecha_actual
				orden_planificada['turno'] = turno['nombre']
				planificadas.append(orden_planificada)
			ordenes_pendientes = self._recalculaOrdenesPendientes(ordenes_pendientes, bloque)
			self._fecha_actual = self._avanzaTurno(self._fecha_actual, turno)
		return planificadas
	
	def _obtieneTurno(self, fecha):
		hora = fecha.hour
		turno = self._buscaTurnoPorHora(hora)
		if turno:
			turno_actual = turno
		else:
			turno_actual = self._buscaSiguienteTurno(hora)
		return turno_actual
	
	def _buscaTurnoPorHora(self, hora):
		for turno in self._turnos:
			if turno['hora'] == hora:
				return turno
			else:
				return None
	
	def _buscaSiguienteTurno(self, hora_actual):
		horas = sorted(turno['hora'] for turno in self._turnos)
		for hora in horas:
			if hora_actual < hora:
				return self._buscaTurnoPorHora(hora)
		return self._turnos[0]
	
	def _llenaTurno(self, ordenes):
		asignadas = []
		resto = self.CAPACIDAD_TURNO
		for orden in ordenes:
			cantidad = orden.get('Cantidad',0)
			if cantidad <= resto:
				asignadas.append(orden)
				resto -= cantidad
		return asignadas
	
	def _recalculaOrdenesPendientes(self, ordenes_pendientes, bloque):
		return [orden for orden in ordenes_pendientes if orden not in bloque]
	
	def _avanzaTurno(self, fecha, turno_actual):
		turno_siguiente = fecha + timedelta(hours=turno_actual['duracion'])
		turno_siguiente_formateado = turno_siguiente.replace(minute=0, second=0, microsecond=0)
		return turno_siguiente_formateado
	
class EscritorPlanificacion:
	
	RUTA_QUERY = 'FD/PlanificadorProduccion/InsertaOrdenesPlanificadas'	
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
	
	def insertaPlanificacion(self, planificacion):
		for entrada in planificacion:
			self._insertaEntrada(entrada)
	
	def _insertaEntrada(self, entrada):
		parametros = self._preparaParametrosEntrada(entrada)
		self._db.ejecutaNamedQuery(self.RUTA_QUERY, parametros)
	
	def _preparaParametrosEntrada(self, entrada):
		return {
			'CodEmp': entrada.get('CodEmp'),
			'ProdOrder': self._generaCodigoProdOrder(entrada),
			'Referencia': entrada.get('CodArt'),
			'CantidadTotal': entrada.get('Cantidad'),
			'UnidadesProducidas': 0,
			'Pendientes': entrada.get('Cantidad'),
			'InicioEstimado': entrada.get('fecha_programada'),
			'FinEstimado': entrada.get('fecha_programada'),
			'CodCli': entrada.get('CodCli'),
			'NomCli': self._obtieneNombreCliente(entrada),
			'CodPed': entrada.get('CodPed'),
			'CodSer': entrada.get('CodSer'),
			'CodEje': entrada.get('CodEje'),
			'ProductionLine': 101,
			'Estado': 1,
			'Observaciones': entrada.get('Obs', '')
		}
	
	def _generaCodigoProdOrder(self, entrada):
		return entrada.get('CodEmp').strip() + '_' + str(entrada.get('CodEje')) + '_' + str(entrada.get('NumOrd'))
	
	def _obtieneNombreCliente(self, entrada):
		codcli = entrada.get('CodCli')
		resultado_nomcli = self._db.ejecutaNamedQuery('FD/Utilidades/ObtieneNombreCliente', {'CodCli': codcli})
		if resultado_nomcli:
			nomcli = resultado_nomcli.getValueAt(0, 'NomCli')
		else:
			nomcli = 'FORMS AND DESIGN IN SHOWER TRAY, S.L.'
		return nomcli
	