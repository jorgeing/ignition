#En construccion

from fd.utilidades.logger import LoggerBase
from fd.utilidades.sql import EjecutadorNamedQueriesConContexto
from fd.utilidades.dataset import ConversorFormatosDataset
from time import sleep

class SelectorOrdenProduccion:
	
	_logger = None
	_id_candado = ""
	_asignador_ordenes = None
	_consultador_plan = None
	_limite_ventana = None
	_linea_produccion = 0
	_udt_seleccion = None
	
	_sku_molde = ""
	_id_color = None
	
	_orden_produccion_asignada = None
	
	def __init__(self, linea_produccion, limite_ventana):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("SelectorOrdenProduccion")
		self._logger.activaLogDebug()
		
		self._id_candado = "input_" + str(linea_produccion)
		self._limite_ventana = limite_ventana
		self._linea_produccion = linea_produccion
		
		self._asignador_ordenes = fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_candado)
		self._consultador_plan = fd.planificacionproduccion.plan.ConsultadorPlan(limite_ventana)
		self._obtieneUdtSeleccion()
	
	def actualizaYAsignaSeleccionOrdenProduccion(self, sku_molde, id_color):
		self._sku_molde = sku_molde
		self._id_color = id_color
		
		self._actualizaDatasetSelectorOrdenesProduccion()
		self._asignaOrdenDeProduccion()
		return self._orden_produccion_asignada

	def _actualizaDatasetSelectorOrdenesProduccion(self):
		self._udt_seleccion.refrescaUdtParaRecalcular()
		
		dataset_compatibles = self._consultador_plan.obtieneOrdenesEnVentanaCompatiblesConMoldeYColor(
			self._sku_molde, self._id_color
		)
		self._udt_seleccion.actualizaOrdenesCompatibles(dataset_compatibles)
		self._logger.logDebug('Dataset Compatibles: ' + str(dataset_compatibles))
		
	def _asignaOrdenDeProduccion(self):
		self._asignador_ordenes.desbloqueaOrdenProduccion()
		self._obtieneYBloqueaOrdenCompatible()
		self._actualizaUdtSelector()
	
	def _obtieneYBloqueaOrdenCompatible(self):
		self._udt_seleccion.estableceEstadoSeleccionOrden(self._udt_seleccion._CONSULTANDO)
		try:
			id_detallado = self._asignador_ordenes.obtieneYBloqueaOrdenProduccion(
				self._sku_molde, self._id_color, self._limite_ventana
			)
			self._logger.logDebug('Id detallado asignado: ' + str(id_detallado))
			self._orden_produccion_asignada = fd.ordenesproduccion.OrdenProduccionDetallada(id_detallado)
			self._udt_seleccion.estableceEstadoSeleccionOrden(self._udt_seleccion._PENDIENTE_ENVIO_PLC)
		except Exception as e:
			self._logger.logError('Error obteniendo/bloqueando orden compatible: ' + str(e))
			self._orden_produccion_asignada = None
	
	def _actualizaUdtSelector(self):
		if self._orden_produccion_asignada:
			self._udt_seleccion.actualizaOrdenSeleccionada(self._orden_produccion_asignada)
		else:
			self._udt_seleccion.estableceEstadoSeleccionOrden(self._udt_seleccion._ERROR_CONSULTA)
		
	def _obtieneUdtSeleccion(self):
		self._udt_seleccion = fd.clasesordenesprod.udt.udtSeleccionOrdenesVia.contruyeUdtSeleccionDesdeRutaEstandarYVia(
			self._linea_produccion
		)
		
class SelectorColor:
	
	_linea_produccion = 0
	_udt_seleccion = None

	def __init__(self, linea_produccion):
		self._linea_produccion = linea_produccion
		self._udt_seleccion = fd.clasesordenesprod.udt.udtSeleccionOrdenesVia.contruyeUdtSeleccionDesdeRutaEstandarYVia(
			linea_produccion
		)
	
	def actualizaColorSelector(self):
		colores_compatibles = self._udt_seleccion.obtieneColoresActivosCabina()
		botones_colores = self._construyeBotonesColores(colores_compatibles)
		self._udt_seleccion.actualizaColoresCompatiblesSelector(botones_colores)
	
	def _construyeBotonesColores(self, colores_compatibles):
		botones = []
		selectedStyle = {"classes": ""}
		unselectedStyle = {"classes": ""}
		
		for color in colores_compatibles:
			boton = {
				"text": u"{lname}/{id}".format(lname=str(color.get("lname","")), id=str(color.get("id",""))),
				"value": color.get("id"),
				"selectedStyle": selectedStyle,
				"unselectedStyle": unselectedStyle
			}
			botones.append(boton)
			
		return system.util.jsonEncode(botones)
	
class FiltroColoresPlatosDelPlan:
	_datos_platos_plan = None
	
	_ejecutador_named_queries_contexto = None

	def __init__(self, datos_platos_plan):
		self._datos_platos_plan = system.dataset.toPyDataSet(datos_platos_plan)
		self._ejecutador_named_queries_contexto = EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		
	def obtieneColoresAFiltrar(self):
		opciones_filtro = self._obtieneOpcionesFiltro()
		return opciones_filtro
	
	def _obtieneOpcionesFiltro(self):
		id_colores_plan = self._obtieneIdColoresEnPlan()
		colores_compatibles = self._obtieneColoresCompatibles(id_colores_plan)
		opciones_filtro = self._construyeOpcionesFiltro(colores_compatibles)
		return opciones_filtro
	
	def _obtieneIdColoresEnPlan(self):
		id_colores_plan = '(' + ','.join(str(fila['color_id']) for fila in self._datos_platos_plan) + ')'
		return id_colores_plan

	
	def _obtieneColoresCompatibles(self, id_colores_plan):
		colores_compatibles = self._ejecutador_named_queries_contexto.ejecutaNamedQuery('FD/OrdenesProduccionScada/ObtieneListaColoresPorID', {'lista_id_colores': id_colores_plan})
		return colores_compatibles
	
	def _construyeOpcionesFiltro(self, colores_compatibles):
		opciones_filtro = []
		opciones_filtro.append({"value":-1,"label":"Todos"})
		for fila in colores_compatibles:
			opcion_filtro = {"value":fila["id"], "label":fila["lname"]+'/'+str(fila["id"])}
			opciones_filtro.append(opcion_filtro)
		return opciones_filtro



# MOVIDO A EVENTOS COMO EventoSalidaMoldeCabinaPintura	
class GestorSalidaMoldesDeCabinaPintura:
	logger = system.util.getLogger("GestorSalidaMoldesDeCabinaPintura")
	
	_via_produccion = 0
	_id_bloqueo = ''
	_id_molde_a_crear = None
	_id_molde_estimado = None
	_id_molde_rfid = None
	_rssi = None
	_plato_dentro_rfid = None
	_id_plan = None
	
	_ruta_id_plan = '[rfid_tags]ProdOrders/CurrentPlanId'
	_ruta_ultimo_molde_pintado = ''
	_ruta_molde_entrante = ''
	_ruta_id_molde_a_crear = ''
	_ruta_id_molde_estimado = ''
	_ruta_id_molde_rfid = ''
	_ruta_rssi = ''
	_ruta_plato_dentro_rfid = ''
	_ruta_estado_cabina_pintura = ''
	_ruta_color_crudo = ''
	
	def __init__(self, via_produccion):
		self._via_produccion = via_produccion
		if via_produccion == 1:
			self._id_bloqueo = 'paint_1'
			self._ruta_molde_entrante = '[rfid_tags]Antennas/Molds/line1_paint_input/mold_id_anterior'
			self._ruta_ultimo_molde_pintado = '[rfid_tags]seleccionOrdenes/OrdenesVia1/UltimoMoldePintado'
			self._ruta_id_molde_a_crear = '[rfid_tags]seleccionOrdenes/OrdenesVia1/IdMoldeCrear'
			self._ruta_id_molde_estimado = '[rfid_tags]seleccionOrdenes/OrdenesVia1/MoldeEnCabina'
			self._ruta_id_molde_rfid = '[rfid_tags]seleccionOrdenes/OrdenesVia1/IdMoldeEstimado'
			self._ruta_rssi = '[rfid_tags]seleccionOrdenes/OrdenesVia1/MaxRSSI'
			self._ruta_plato_dentro_rfid = '[rfid_tags]seleccionOrdenes/OrdenesVia1/PlatoDentroRFID'
			self._ruta_estado_cabina_pintura = '[rfid_tags]seleccionOrdenes/OrdenesVia1/EstadoCabina'
			self._ruta_color_crudo = '[rfid_tags]seleccionOrdenes/OrdenesVia1/RalCreadoEnCabina'
		else:
			self._id_bloqueo = 'paint_2'
			self._ruta_molde_entrante = '[rfid_tags]Antennas/Molds/line2_paint_input/mold_id_anterior'
			self._ruta_ultimo_molde_pintado = '[rfid_tags]seleccionOrdenes/OrdenesVia2/UltimoMoldePintado'
			self._ruta_id_molde_a_crear = '[rfid_tags]seleccionOrdenes/OrdenesVia2/IdMoldeCrear'
			self._ruta_id_molde_estimado = '[rfid_tags]seleccionOrdenes/OrdenesVia2/MoldeEnCabina'
			self._ruta_id_molde_rfid = '[rfid_tags]seleccionOrdenes/OrdenesVia2/IdMoldeEstimado'
			self._ruta_rssi = '[rfid_tags]seleccionOrdenes/OrdenesVia2/MaxRSSI'
			self._ruta_plato_dentro_rfid = '[rfid_tags]seleccionOrdenes/OrdenesVia2/PlatoDentroRFID'
			self._ruta_estado_cabina_pintura = '[rfid_tags]seleccionOrdenes/OrdenesVia2/EstadoCabina'
			self._ruta_color_crudo = '[rfid_tags]seleccionOrdenes/OrdenesVia2/RalCreadoEnCabina'
	
	def creaPlatoEnPLC(self):
		logger = system.util.getLogger("creaPlatoEnPLC")
		try:
			self._obtieneDatosNecesarios()
			orden_produccion = self._obtieneOrdenProduccionBloqueada()
			self.logger.info("orden de produccion -> "+str(orden_produccion))
			codigo_cliente = self._obtieneCodigoClienteDeOrdenProduccion(orden_produccion)
			nuevo_color = self._obtieneColorNuevo()
			print('Nuevo Color: ' + str(nuevo_color))
			if nuevo_color >= 0:
				try:
					id_molde = self._obtieneIdMolde()
					id_plato_creado = self._creaPlatoEnPLCYObtieneId(id_molde, nuevo_color, codigo_cliente, orden_produccion)
					self._actualizaUltimoMoldePintado(id_molde)
					self._actualizaEstadoMolde(id_plato_creado, id_molde)
					self._actualizaMoldeEntrante()
					self._actualizaEstadoCabinaPintura()
					self._liberaOrdenProduccionBloqueada()
					return id_plato_creado
				except Exception as e:
					logger.error("Error creando plato: "+str(e))
		except Exception as e:
				logger.error("Error obteniendo color: "+str(e))
	
	def _obtieneDatosNecesarios(self):
		self._id_molde_a_crear = system.tag.readBlocking(self._ruta_id_molde_a_crear)[0].value
		self._id_molde_estimado = system.tag.readBlocking(self._ruta_id_molde_estimado)[0].value
		self._id_molde_rfid = system.tag.readBlocking(self._ruta_id_molde_rfid)[0].value
		self._rssi = system.tag.readBlocking(self._ruta_rssi)[0].value
		self._plato_dentro_rfid = system.tag.readBlocking(self._ruta_plato_dentro_rfid)[0].value
		self._id_plan = system.tag.readBlocking(self._ruta_id_plan)[0].value
		
	def _obtieneOrdenProduccionBloqueada(self):
		logger = system.util.getLogger("obtieneOrdenProduccionBloqueada")
		logger.info('ID bloqueo: ' + str(self._id_bloqueo))
		orden_produccion = fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_bloqueo).obtieneOrdenProduccionBloqueada()
		logger.info('orden produccion bloqueada: ' + str(orden_produccion))
		if not orden_produccion:
			logger.warn("error obteniendo orden bloqueada en paint_1, asignando blanco")
			orden_produccion = ''
		return orden_produccion
	
	def _obtieneCodigoClienteDeOrdenProduccion(self, orden_produccion):
		datos_orden_produccion = fd.ordenesproduccion.OrdenProduccionSeleccionada(orden_produccion).obtieneInfo()
		if datos_orden_produccion == '':
			codigo_cliente = 9999
		else:
			codigo_cliente = int(datos_orden_produccion[0]['codcli'])
		return codigo_cliente
	
	def _obtieneColorNuevo(self):
		color_crudo = system.tag.readBlocking(self._ruta_color_crudo)[0].value
		nuevo_color = int(color_crudo)
		return nuevo_color
	
	def _obtieneIdMolde(self):
		if self._id_molde_a_crear != '' and self._id_molde_a_crear != None:
			id_molde = self._id_molde_a_crear
		else:
			if (self._id_molde_rfid != '' and self._id_molde_rfid != None) and self._rssi > -49 and (self._plato_dentro_rfid == None or self._plato_dentro_rfid == ''):
				id_molde = self._id_molde_rfid
			else:
				id_molde = self._id_molde_estimado
		return id_molde
		
	def _creaPlatoEnPLCYObtieneId(self, id_molde, nuevo_color, codigo_cliente, orden_produccion):
		evento_creacion_plato = fd.platos.EventoCreacionPlato(codigo_cliente)
		evento_creacion_plato.creaPlatoDesdeMolde(id_molde, nuevo_color, self._via_produccion, orden_produccion, self._id_plan)
		id_plato_creado = evento_creacion_plato.obtieneNumeroSerie()
		return id_plato_creado
	
	def _actualizaUltimoMoldePintado(self, id_molde):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._ruta_ultimo_molde_pintado, id_molde)
	
	def _actualizaEstadoMolde(self, id_plato_creado, id_molde):
		estado_nuevo = 'mold-in-production'
		fd.moldes.EventoActualizaEstadoMolde().actualizaEstadoMolde(id_molde, estado_nuevo, id_plato_creado)
	
	def _actualizaMoldeEntrante(self):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._ruta_molde_entrante, '')
	
	def _actualizaEstadoCabinaPintura(self):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._ruta_estado_cabina_pintura, 0)
	
	def _liberaOrdenProduccionBloqueada(self):
		fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_bloqueo).desbloqueaOrdenProduccion()
