from fd.utilidades.logger import LoggerBase
from fd.utilidades.sql import EjecutadorNamedQueriesConContexto
from fd.utilidades.dataset import ConversorFormatosDataset

class EventoObtieneYActualizaOrdenesCompatibles:
	
	_logger = None
	_via_produccion = None
	_estado_ordenes_compatibles = None
	_udt_seleccion = None
	_info_rfid = None
	_ruta_ventana_actual = '[rfid_tags]ProdOrders/LimiteLineasPublicarPlan'
	
	LIMITE_VENTANA_AMPLIADO = 3000
	
	def __init__(self, via_produccion):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EventoActualizaOrdenesCompatibles')
		self._via_produccion = via_produccion
		self._obtieneUdtSeleccion()
		self._info_rfid = fd.rfid.infozonas.DatosZonaRFID('line'+str(self._via_produccion)+'_paint_input')
		
	def obtieneOrdenYActualizaSelector(self):
		selectorVia = self._obtieneSelectorVia()
		sku_molde = self._info_rfid.obtieneSkuMolde()
		id_color = self._udt_seleccion.obtieneColorActual()
		orden_seleccionada = selectorVia.actualizaYAsignaSeleccionOrdenProduccion(sku_molde, id_color)
		self._reestableceTagsVentanaYRecalculo()
		
		self._logger.logInfo("Resultado seleccion orden para via "+ str(self._via_produccion) + str(sku_molde) +" " + str(id_color) + ":"+str(orden_seleccionada) )
		return orden_seleccionada
		
	def _obtieneLimiteVentana(self):
		if self._udt_seleccion.usaLimiteVentanaAmpliado():
			limite_ventana = self.LIMITE_VENTANA_AMPLIADO
		else:
			limite_ventana = fd.utilidades.tags.GestorTags.leeValorDeUnTag(self._ruta_ventana_actual)
		return limite_ventana
		
	def _obtieneSelectorVia(self):
		limite_ventana = self._obtieneLimiteVentana()
		selectorVia = fd.clasesordenesprod.selectores.SelectorOrdenProduccion(self._via_produccion, limite_ventana)
		return selectorVia
		
	def _obtieneUdtSeleccion(self):
		path = "[rfid_tags]seleccionOrdenes/OrdenesVia" + str(self._via_produccion)
		self._udt_seleccion = fd.clasesordenesprod.udt.udtSeleccionOrdenesVia(path)
	
	def _reestableceTagsVentanaYRecalculo(self):
		self._udt_seleccion.resetUsarLimiteVentanaAmpliado()
		self._udt_seleccion.resetRecalculaOrdenProduccion()

class EventoEntradaMoldeCabinaPintura:
	_logger = None
	
	_via_produccion = 0
	_udt_seleccion_ordenes = None
	
	def __init__(self, via_produccion):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("EventoEntradaMoldeCabinaPintura")
		self._logger.activaLogDebug()
		self._via_produccion = via_produccion
		self._udt_seleccion_ordenes = fd.ordenesproduccion.udtSeleccionOrdenesVia.contruyeUdtSeleccionDesdeRutaEstandarYVia(via_produccion)
		
	def entradaMolde(self):
		self._logger.logDebug("Entrando molde a cabina " + str(self._via_produccion) +  ": "+self._udt_seleccion_ordenes.obtieneIdMoldeEntrada())
		try:
			self._transfiereOrdenProduccion()
			self._udt_seleccion_ordenes.transfiereEntradaACabinaSiMoldesDistintos()
		except Exception as e:
			self._logger.logError("Error en la entrada del molde: "+str(e))

	def _transfiereOrdenProduccion(self): 
		id_candado_origen = 'input_' + str(self._via_produccion)
		self._logger.logDebug('ID Candado Origen :' + str (id_candado_origen))
		id_candado_destino = 'paint_' + str(self._via_produccion)
		self._logger.logDebug('ID Candado Destino: ' + str(id_candado_destino))
		fd.ordenesproduccion.AsignadorOrdenProduccion(id_candado_origen).transfiereOrdenProduccion(id_candado_destino)


class EventoCompruebaOrdenPlatoPintado:

	_logger = None
	_via_produccion = 0
	_udt = None

	_estado_salida = 0   # 2 OK, 3 sugiere colores
	_ral_color = 0
	_id_modelo = ''
	_nombre_sku = ''
	_nombre_largo_modelo = ''
	_sku_molde = ''

	def __init__(self, via_produccion):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("EventoCompruebaOrdenPlatoPintado")
		self._via_produccion = via_produccion
		self._udt = fd.clasesordenesprod.udt.udtSeleccionOrdenesVia.contruyeUdtSeleccionDesdeRutaEstandarYVia(via_produccion)

	def validaCreacionDelPlato(self):
		try:
			self._udt.estableceEstadoSeleccionOrden(self._udt._CONSULTANDO)

			contexto = self._cargaContexto()
			if not contexto['id_molde']:
				self._udt.estableceEstadoSeleccionOrden(self._udt._NO_MOLDE)
				return self._respuestaNoOk('')

			self._cargaModelo(contexto['id_molde'])

			decision = self._determinaPermisoDePinturaYReasignacion(contexto)

			self._aplicaEfectos(decision, contexto)

			self._udt.estableceEstadoSeleccionOrden(
				self._udt._ESTADO_SELECCION_ENVIADO_PLC if decision['permite_pintura'] else self._udt._ERROR_CONSULTA
			)

			return self._formateaRespuesta(contexto['id_molde'], decision)

		except Exception as e:
			self._logger.logError("Error en validaCreacionDelPlato: " + str(e))
			self._udt.estableceEstadoSeleccionOrden(self._udt._ERROR_CONSULTA)
			return self._respuestaNoOk('')

	def _cargaContexto(self):
		self._udt.limpiaOrdenEnCabinaSiMismoMolde()

		id_molde_estimado = self._udt.obtieneIdMoldeEstimadoEnCabina()
		id_molde_rfid     = self._udt.obtieneIdMoldeEstimadoEnCabina()
		rssi              = self._udt.obtieneRSSI()
		plato_dentro_rfid = self._udt.obtienePlatoDentroRFID()
		self._ral_color   = self._udt.obtieneColorActual()

		orden_json_txt = self._udt.obtieneOrdenProduccionPreferida_JSON()
		try:
			orden_dict = system.util.jsonDecode(orden_json_txt) if orden_json_txt else {}
		except:
			orden_dict = {}

		id_molde = self._eligeMolde(id_molde_estimado, id_molde_rfid, rssi, plato_dentro_rfid)

		self._logger.logInfo("Molde estimado={e} rfid={r} rssi={s} elegido={m}".format(
			e=id_molde_estimado, r=id_molde_rfid, s=rssi, m=id_molde
		))

		return {
			'id_molde': id_molde,
			'orden': self._parseaOrden(orden_dict)
		}

	def _eligeMolde(self, estimado, rfid, rssi, plato_dentro):
		if (rfid not in (None, '')) and (rssi is not None and rssi > -49) and (plato_dentro in (None, '')):
			return rfid
		return estimado

	def _parseaOrden(self, orden):
		if not isinstance(orden, dict):
			return {'id': '', 'sku': '', 'color': 0}
		return {
			'id':    orden.get('prod_order', '') or '',
			'sku':   orden.get('sku', '') or '',
			'color': orden.get('color', 0) or 0
		}

	def _cargaModelo(self, id_molde):
		self._id_modelo, self._nombre_sku, self._nombre_largo_modelo, self._sku_molde = fd.moldes.Molde(id_molde).obtieneSKUModelo()

	def _determinaPermisoDePinturaYReasignacion(self, contexto):

		orden = contexto['orden']

		if orden['id']:
			if self._esValidaConOrden(orden):
				return self._devuelveOk()
			nueva_orden = self._recalculaNuevaOrden()
			if nueva_orden['nuevo_id']:
				return self._devuelveOkReasigna(nueva_orden)
			return self._devuelveNoOk()

		if self._esColorCompatibleConModelo():
			return self._devuelveOk()
		return self._devuelveNoOk()

	def _esValidaConOrden(self, orden):
		try:
			info_orden = fd.ordenesproduccion.OrdenProduccionSeleccionada(orden['id']).obtieneInfo()
			fila_info_orden = info_orden[0] if isinstance(info_orden, list) and info_orden else (info_orden if isinstance(info_orden, dict) else {})
			sku_op   = fila_info_orden.get('sku', fila_info_orden.get('product_ref', orden['sku']))
			color_op = int(sku_op[9:13]) if (sku_op and len(sku_op) >= 13) else int(orden['color'] or 0)

			molde_ok = (self._sku_molde == (sku_op or '')[:9])
			color_ok = int(self._ral_color) == int(color_op)
			return molde_ok and color_ok
		except Exception as e:
			self._logger.logWarning("Error validando contra orden: " + str(e))
			return False

	def _esColorCompatibleConModelo(self):
		colores = self._obtieneIdsColoresCompatibles()
		return str(self._ral_color) in colores if colores else False

	def _obtieneIdsColoresCompatibles(self):
		colores_compatibles = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase').ejecutaNamedQuery(
			'FD/OrdenesProduccionScada/ObtieneColoresCompatiblesConModelo', {'id_modelo': self._id_modelo}
		)
		try:
			colores_crudo = colores_compatibles[0][0] if colores_compatibles.getValueAt(0,0) else ""
			return colores_crudo[1:-1].split(',') if colores_crudo else []
		except:
			return []

	def _recalculaNuevaOrden(self):
		try:
			id_candado = 'paint_' + str(self._via_produccion)
			asignador = fd.ordenesproduccion.AsignadorOrdenProduccion(id_candado)
			id_det = asignador.obtieneYBloqueaOrdenProduccion(self._sku_molde, self._ral_color, 10000)

			info_orden = fd.ordenesproduccion.OrdenProduccionSeleccionada(id_det).obtieneInfo()
			fila = info_orden[0] if isinstance(info_orden, list) and info_orden else (info_orden if isinstance(info_orden, dict) else {})

			return {
				'nuevo_id':    fila.get('production_order_id', fila.get('id_orden_produccion_detallada', '')) or '',
				'nuevo_sku':   fila.get('sku', fila.get('product_ref', '')) or '',
				'nuevo_color': int(fila.get('color_id', -1)),
				'nuevo_codcli': int(fila.get('codcli', self._udt._CLIENTE_DEFECTO))
			}
		except Exception:
			return {'nuevo_id':'', 'nuevo_sku':'', 'nuevo_color':-1, 'nuevo_codcli': self._udt._CLIENTE_DEFECTO}

	def _devuelveOk(self):
		return {'permite_pintura': True, 'reasignar': False, 'nuevo_id':'', 'nuevo_sku':'', 'nuevo_color':-1, 'nuevo_codcli': self._udt._CLIENTE_DEFECTO}

	def _devuelveOkReasigna(self, nuevo):
		return dict({'permite_pintura': True, 'reasignar': True}, **nuevo)

	def _devuelveNoOk(self):
		return {'permite_pintura': False, 'reasignar': False, 'nuevo_id':'', 'nuevo_sku':'', 'nuevo_color':-1, 'nuevo_codcli': self._udt._CLIENTE_DEFECTO}

	def _aplicaEfectos(self, decision, contexto):
		self._ajustaEstadoColor()

		if decision['reasignar'] and decision['nuevo_id'] and decision['nuevo_sku']:
			self._udt.reescribeOrdenProduccion(decision['nuevo_id'], decision['nuevo_sku'], decision['nuevo_color'], decision['nuevo_codcli'])

		nombre_modelo = (self._nombre_largo_modelo or '').ljust(10, ' ')
		self._udt.fijaMoldeUsado(contexto['id_molde'], nombre_modelo, self._estado_salida)

	def _ajustaEstadoColor(self):
		if self._esColorCompatibleConModelo():
			self._estado_salida = 2
			return

		ids_colores = self._obtieneIdsColoresCompatibles()
		datos_colores = []
		if ids:
			lista_id_colores = '(' + ','.join(str(id_color) for id_color in ids_colores) + ')'
			lista_colores = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase').ejecutaNamedQuery(
				'FD/OrdenesProduccionScada/ObtieneListaColoresPorID', {'lista_id_colores': lista_id_colores}
			)
			for color in lista_colores:
				datos_colores.append((color['id'], color['lname']))

		self._udt.escribeListaColoresCompatiblesPLC(datos_colores)
		self._estado_salida = 3

	def _formateaRespuesta(self, id_molde, decision):
		if decision['permite_pintura'] and decision['reasignar']:
			return self._respuestaOkReescribe(id_molde, decision['nuevo_sku'], decision['nuevo_id'])
		if decision['permite_pintura']:
			return self._respuestaOk(id_molde)
		return self._respuestaNoOk(id_molde)

	def _respuestaOk(self, id_molde):
		return {'json':{
			'id_molde': id_molde, 'estado_ok': True,
			'nuevo_sku':'', 'nuevo_id_orden_produccion':'',
			'permite_pintura': True,
			'reescribir_sku': False, 'reescribir_id_orden_produccion': False
		}}

	def _respuestaOkReescribe(self, id_molde, nuevo_sku, nuevo_id):
		return {'json':{
			'id_molde': id_molde, 'estado_ok': True,
			'nuevo_sku': nuevo_sku, 'nuevo_id_orden_produccion': nuevo_id,
			'permite_pintura': True,
			'reescribir_sku': True, 'reescribir_id_orden_produccion': True
		}}

	def _respuestaNoOk(self, id_molde):
		return {'json':{
			'id_molde': id_molde, 'estado_ok': False,
			'nuevo_sku':'', 'nuevo_id_orden_produccion':'',
			'permite_pintura': False,
			'reescribir_sku': False, 'reescribir_id_orden_produccion': False
		}}
		
class EventoSalidaMoldeCabinaPintura:
	_logger = None
	
	_via_produccion = 0
	_id_bloqueo = ''
	_udt = None

	def __init__(self, via_produccion):
		self._logger = system.util.getLogger("EventoSalidaMoldeCabinaPintura")
		self._via_produccion = via_produccion
		self._udt = fd.clasesordenesprod.udt.udtSeleccionOrdenesVia.contruyeUdtSeleccionDesdeRutaEstandarYVia(via_produccion)
		self._id_bloqueo = 'paint_' + str(via_produccion)

	def creaPlatoEnPLC(self):
		try:
			contexto = self._cargaContexto()
			orden_produccion = self._obtieneOrdenProduccionBloqueada()
			self._logger.info("Orden bloqueada: {}".format(orden_produccion))

			codigo_cliente = self._obtieneCodigoClienteDeOrdenProduccion(orden_produccion)
			nuevo_color = contexto['nuevo_color']
			self._logger.info("Color creado en cabina: {}".format(nuevo_color))
			if nuevo_color < 0:
				raise Exception("Color inválido ({})".format(nuevo_color))

			id_molde = self._decideIdMolde(contexto)
			id_plato = self._creaPlatoYObtieneId(id_molde, nuevo_color, codigo_cliente, orden_produccion, contexto['id_plan'])

			self._udt.escribeUltimoMoldePintado(id_molde)
			self._actualizaEstadoMolde(id_plato, id_molde)
			self._udt.escribeMoldeEntrante('')      
			self._udt.escribeEstadoCabinaPintura(0)
			self._liberaOrdenProduccionBloqueada()

			return id_plato

		except Exception as e:
			self._logger.error("Error en registraSalidaDeCabina: " + str(e))

	def _cargaContexto(self):
		return {
			'id_molde_crear':    self._udt.obtieneIdMoldeACrear(),
			'id_molde_estimado': self._udt.obtieneIdMoldeEstimadoEnCabina(),
			'id_molde_rfid':     self._udt.obtieneIdMoldeEstimado(),
			'rssi':              self._udt.obtieneRSSI(),
			'plato_dentro':      self._udt.obtienePlatoDentroRFID(),
			'id_plan':           self._udt.obtieneIdPlanActual(),
			'nuevo_color':       self._udt.obtieneColorCreadoEnCabina()
		}

	def _obtieneOrdenProduccionBloqueada(self):
		self._logger.info('ID bloqueo: ' + str(self._id_bloqueo))
		orden_produccion = fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_bloqueo).obtieneOrdenProduccionBloqueada()
		self._logger.info('Orden produccion bloqueada: ' + str(orden_produccion))
		if not orden_produccion:
			self._logger.warn("No hay orden bloqueada en {}, asigna blanco".format(self._id_bloqueo))
			return ''
		return orden_produccion

	def _obtieneCodigoClienteDeOrdenProduccion(self, orden_produccion):
		info_orden = fd.ordenesproduccion.OrdenProduccionSeleccionada(orden_produccion).obtieneInfo()
		if not info_orden:
			return 9999
		try:
			return int(info_orden[0]['codcli'])
		except:
			return 9999

	def _decideIdMolde(self, contexto):
		if contexto['id_molde_crear']:
			return contexto['id_molde_crear']
		if contexto['id_molde_rfid'] and contexto['rssi'] is not None and contexto['rssi'] > -49 and (contexto['plato_dentro'] in (None, '')):
			return contexto['id_molde_rfid']
		return contexto['id_molde_estimado']

	def _creaPlatoYObtieneId(self, id_molde, nuevo_color, codigo_cliente, orden_produccion, id_plan):
		evento = fd.platos.EventoCreacionPlato()
		evento.creaPlatoDesdeMolde(id_molde, nuevo_color, codigo_cliente, self._via_produccion, orden_produccion, id_plan)
		return evento.obtieneNumeroSerie()

	def _actualizaEstadoMolde(self, id_plato_creado, id_molde):
		estado_nuevo = 'mold-in-production'
		fd.moldes.EventoActualizaEstadoMolde().actualizaEstadoMolde(id_molde, estado_nuevo, id_plato_creado)

	def _liberaOrdenProduccionBloqueada(self):
		fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_bloqueo).desbloqueaOrdenProduccion()