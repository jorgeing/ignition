from fd.utilidades.dataset import *
class PlatoDucha:
	
	_numero_serie=None
	
	_info_plato_dataset=None
	
	_info_scada={}
	_info_erp={}

	def __init__(self, numero_serie_plato):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._numero_serie = numero_serie_plato
		self._consultaInfoScada()
		
	def obtieneNumeroSerie(self):
		return self._numero_serie
		
	def obtieneInfoScada(self):
		return self._info_scada
		
	def platoExiste(self):
		return self._info_plato_dataset != None and self._info_plato_dataset.getRowCount()>0
		
	def obtieneColor(self):
		return int(self._numero_serie[23:29])
		
	def obtieneDimension(self):
		return self._numero_serie[32:]
		
	def obtieneModelo(self):
		return int(self._numero_serie[29:32])
		
	def _consultaInfoScada(self):
		showertray_id = self._numero_serie
		parametros = {'showertray_id': showertray_id}
		self._info_plato_dataset = self._db.ejecutaNamedQuery('FD/Platos/InformacionPlatoDeNumeroSerie', parametros)
		if self.platoExiste():
			self._info_scada = ConversorFormatosDataset.filaDatasetADiccionario(self._info_plato_dataset, 0)
			



class EventoCreacionPlato:
	
	COLOR_TEMPORAL = 990000
	CLIENTE_TEMPORAL = 00000
	MOLDE_EN_PRODUCCION = 'mold-in-production'
	
	_numero_serie=""
	_sku = ''
	_id_cliente = 0
	_mold_id = None
	
	_logger = None
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("EventoCreacionPlato")
		self._logger.activaLogDebug()
		self._logger.desactivaLogDebug()
		
	def creaPlatoDeSku(self, sku, id_cliente, line_id = None, production_order_id_detailed = None, plan_id = None, largo = None, ancho = None):
		self._sku = sku
		self._id_cliente = id_cliente
		generador = fd.numerosserie.GeneradorNumeroSeriePlato.contruyeDesdeSku(sku, self._id_cliente, largo, ancho)
		self._numero_serie = generador.obtieneNumeroSerie()
		self._insertaPlatoNuevo(line_id, production_order_id_detailed, plan_id)
		self._logger.logInfo("Plato creado: "+str(self._numero_serie)+ "-"+ str(production_order_id_detailed))
		
	def creaPlatoDesdeMolde(self, mold_id, id_color, id_cliente, line_id, production_order_id_detailed = None, plan_id = None):
		self._mold_id = mold_id
		self._id_cliente = id_cliente
		self._sku = self._obtieneSkuDeOrdenProduccion(production_order_id_detailed)
		generador = fd.numerosserie.GeneradorNumeroSeriePlato.construyeDesdeMolde(mold_id, self._id_cliente, id_color)
		self._numero_serie = generador.obtieneNumeroSerie()
		self._insertaPlatoNuevo(line_id, production_order_id_detailed, plan_id)
		self._asociarPlatoAMolde()
		self._logger.logInfo("Plato creado: "+str(self._numero_serie)+ "-"+ str(production_order_id_detailed))
		
	def creaPlatoBackUpSiNecesario(self, mold_id, numero_serie_dentro, line_id):
		numero_serie = numero_serie_dentro
		numero_serie_valido = False
		try:
			numero_serie_valido = fd.numerosserie.NumeroSerie(numero_serie_dentro).esPlato()
			self._logger.logDebug('numero de serie es valido: '+str(numero_serie_valido))
		except:
			numero_serie_valido = False
		
		if not numero_serie_valido:
			try:
				print(mold_id)
				numero_serie = self.creaPlatoBackUp(mold_id, line_id)
				self._logger.logInfo("Se ha generado un plato de backup: " + str(numero_serie))
			except Exception as e:
				self._logger.logError("No se ha podido crear plato backup: "+ str(e))
				self._logger.logDebug('Backup no creado -> molde: '+str(mold_id)+' via: '+str(line_id))
				
		self._logger.logDebug('numero de serie: '+str(numero_serie))
		return numero_serie
		
	def creaPlatoBackUp(self, mold_id, line_id, color_id=None):
		if color_id ==None:
			color_id = self.COLOR_TEMPORAL
		
		self._mold_id = mold_id
		generador = fd.numerosserie.GeneradorNumeroSeriePlato.construyeDesdeMolde(self._mold_id, self.CLIENTE_TEMPORAL, color_id)
		self._numero_serie = generador.obtieneNumeroSerie()
		self._sku = self._generaPartNumberTemporal()
		self._insertaPlatoNuevo(line_id)
		self._asociarPlatoAMolde()
		return self._numero_serie
		
	def creaPlatoNuevoCorte(self, showertray_id_original, showertray_id_nuevo, mold_id, sku, cut_length, cut_width, sales_order_id, client_number, line_id = 102, production_order_id_detailed='', plan_id='', frame_options=''):
		self._showertray_id_original = showertray_id_original
		self._mold_id = mold_id
		self._place_id = fd.globales.ParametrosGlobales.obtieneIdFabrica()
		plato_ducha = PlatoDucha(showertray_id_original)
		self._dimension = plato_ducha.obtieneDimension()
		self._color_id = plato_ducha.obtieneColor()
		
		generador = fd.numerosserie.GeneradorNumeroSeriePlato.contruyeDesdeSku(sku, self._id_cliente, largo, ancho)
		self._showertray_id_nuevo = generador.obtieneNumeroSerie()
		
		#self._insertaPlatoNuevo(line_id, production_order_id_detailed, plan_id)
		
	def obtieneNumeroSerie(self):
		return self._numero_serie
		
	def _insertaPlatoNuevo(self, line_id, production_order_id_detailed = None, plan_id = None):
		parametros_plato_nuevo = self._generaParametrosInsertarPlatoNuevo(line_id, production_order_id_detailed, plan_id)
		self._logger.logInfo(str(parametros_plato_nuevo))
		insert_plato = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase').ejecutaNamedQuery('FD/Platos/InsertaPlatoCreado', parametros_plato_nuevo)
		if insert_plato != 1:
			raise ValueError('No se pudo instertar')
			
	def _asociarPlatoAMolde(self):
		parametros = self._generaParametrosActualizarEstadoMolde()
		self._db.ejecutaNamedQuery('FD/Moldes/ActualizaEstadoMoldLog', parametros)
		
	def _generaParametrosActualizarEstadoMolde(self):
		parametros = {
			'mold_id': self._mold_id,
			'status': self.MOLDE_EN_PRODUCCION,
			'showertray_id': self._numero_serie,
			'place_id': fd.globales.ParametrosGlobales.obtieneIdFabrica()
		}
		return parametros
		
	def _generaParametrosInsertarPlatoNuevo(self, line_id, production_order_id_detailed, plan_id): #alt_showertray_id = None, cut_length = None, cut_width = None, sales_order_id = None
		
		plato_ducha = PlatoDucha(self._numero_serie)
		color_id = plato_ducha.obtieneColor()
		dimension = plato_ducha.obtieneDimension()
		modelo_plato = plato_ducha.obtieneModelo()
		
		orden_produccion = self._intentaObtenerOrdenProduccionDeOrdenDetallada(production_order_id_detailed)
		
		parametros_plato_nuevo = {
			'client_id': self._id_cliente,
			'client_number': self._id_cliente,
			'color_id': color_id,
			'dimension': dimension,
			'model_id':modelo_plato,
			'mold_id':self._mold_id,
			'place_id': fd.globales.ParametrosGlobales._place_id,
			'showertray_id': self._numero_serie,
			'line_id':line_id,
			'production_order_id':orden_produccion,
			'production_order_id_detailed':production_order_id_detailed,
			'sku':self._sku,
			'plan_id':plan_id
		}
		return parametros_plato_nuevo
		
	def _generaPartNumberTemporal(self):
		return fd.moldes.Molde(self._mold_id).obtieneSKUModelo()[3]
		
	def _intentaObtenerOrdenProduccionDeOrdenDetallada(self, production_order_id_detailed):
		try:
			orden_produccion = fd.ordenesproduccion.OrdenProduccionScada(production_order_id_detailed).obtieneIdOrden()
			return orden_produccion
		except:
			return None
			
	def _obtieneSkuDeOrdenProduccion(self, production_order_id_detailed):
		try:
			sku = fd.ordenesproduccion.OrdenProduccionScada(production_order_id_detailed).obtieneSku()
		except:
			return None
			
	def _generaParametrosCreacionPlatoCorte(self):
		return {
			'client_id':client_id,
			'client_number':client_id,
			'color_id':color_id,
			'dimension':dimension,
			'model_id':model_id,
			'mold_id':mold_id,
			'place_id':place_id,
			'showertray_id': self._showertray_id,
			'line_id':self._line_id,
			'production_order_id':production_order_id,
			'production_order_id_detailed':production_order_id_detailed,
			'sku':sku,
			'cut_length':cut_length,
			'cut_width':cut_width,
			'sales_order_id':sales_order_id,
			'alt_showertray_id':original_showertray_id,
			'plan_id':plan_id,
			'frame_options':frame_options,
			'postprocessed_line':postprocessed_line
		}





class EventoEmpaquetadoPlato:
	
	TABLA_EVENTO = 'pack_showertray'
	CAUSA_FIN_TRAZABILIDAD = 5
	ALMACEN_POR_DEFECTO = 1
	
	_id_impresora=0
	_trabajador=0
	_manual_print_reason = -1
	_scanner_id = -1
	_erp_integration = False
	
	
	_plato={}
	_corte_largo = None
	_corte_ancho = None
	_client_number = 0
	_numero_serie = ''
	

	def __init__(self, manual_print_reason, id_impresora, trabajador, scanner_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._manual_print_reason = manual_print_reason
		self._id_impresora = id_impresora
		self._trabajador = trabajador
		self._erp_integration = self._obtieneIntegracionERP()
		self._scanner_id = scanner_id
	
	def _obtieneIntegracionERP(self):
		parametros = {'worker_id': self._trabajador}
		erp_integration = self._db.ejecutaNamedQuery('FD/Platos/ObtieneERPIntegration', parametros)
		return erp_integration[0]["erp_integration"]
	
	def empaquetarPlato(self, numero_serie, corte_largo, corte_ancho, client_number):
		self._numero_serie = numero_serie
		self._plato = PlatoDucha(numero_serie)
		self._corte_largo = self._compruebaSiCorte(corte_largo)
		self._corte_ancho = self._compruebaSiCorte(corte_ancho)
		self._client_number = client_number
		
		if not self._platoYaEstaEnvasado():
			self._registraEnvasadoYFinalizaTrazabilidad()
			
		fd.moduloetiquetas.servicioetiquetado.EtiquetasEnvasa(self._plato.obtieneNumeroSerie(), self._id_impresora)
		
		EventoCountAsPoured(numero_serie).cuentaComoLlenado()
		
	def obtieneNumeroSerie(self):
		return self._numero_serie
		
	def _compruebaSiCorte(self, corte):
		if corte == 0 or corte == '':
			return None
		else:
			return corte
		
	def _registraEnvasadoYFinalizaTrazabilidad(self):
		parametros_empaquetar_plato = self._obtenerParametrosParaEmpaquetarPlato(self._manual_print_reason)
		self._db.ejecutaNamedQuery('FD/Platos/EmpaquetarPlato', parametros_empaquetar_plato)
		EventoFinTrazabilidad(self._numero_serie, self.CAUSA_FIN_TRAZABILIDAD).finalizaTrazabilidad()
		
	def _platoYaEstaEnvasado(self):
		ocurrencias = self._db.ejecutaNamedQuery("FD/Platos/YaExisteEventoShowertray", {'tabla':self.TABLA_EVENTO, 'showertray_id':self._plato.obtieneNumeroSerie()})
		return ocurrencias.getRowCount()>0
	
	def _obtenerParametrosParaEmpaquetarPlato(self, manual_print_reason):
		logger = system.util.getLogger('EventoEmpaquetadoPlato')
		logger.info('_obtieneCliente '+str(self._obtieneCliente()))
		parametros_empaquetar_plato = {
			"place_id": fd.globales.ParametrosGlobales.obtieneIdFabrica(),
			"showertray_id": self._plato.obtieneNumeroSerie(),
			"t_stamp": system.date.now(),
			"scanner_id": self._scanner_id,
			"client_number": self._obtieneCliente(),
			"printer_name": fd.utilidades.impresoras.InformacionImpresoras(self._id_impresora).obtieneNombreImpresora(),
			"worker_id": self._trabajador,
			"manual_print_reason": manual_print_reason,
			"sku": self._obtieneSku(),
			"color_id": self._obtieneColor(),
			"cut_length": self._corte_largo,
			"cut_width": self._corte_ancho,
			"erp_integration": self._erp_integration,
			"warehouse": self.ALMACEN_POR_DEFECTO
		}
		return parametros_empaquetar_plato
		
	def _obtieneColor(self):
		return self._plato.obtieneInfoScada()["color_id"]
		
	def _obtieneCliente(self):
		return self._plato.obtieneInfoScada()["client_number"]
		
	def _obtieneSku(self):
		return self._plato.obtieneInfoScada()["sku"]


class EventoScrapPlato:
	
	TABLA_EVENTO = 'scrap_showertrays'
	CAUSA_FIN_TRAZABILIDAD = 6
	
	_showertray_id = ''
	_usuario = ''
	_causa = ''
	
	def __init__(self, showertray_id, usuario, causa):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		self._usuario = usuario
		self._causa = causa
		
	def scrapeaPlato(self):
		creado = self.compruebaSiYaSeHaCreadoEvento()
		if creado.getRowCount() > 0:
			return "Plato ya actualizado"
		else:
			parametros = self._obtieneParametrosScrap()
			scrap = self._db.ejecutaNamedQuery('FD/Platos/ScrapPlatos', parametros)
			actualizado = ''
			#print(scrap)
			if scrap == 1:
				actualizado = "Plato dado de scrap"
				EventoFinTrazabilidad(self._showertray_id, self.CAUSA_FIN_TRAZABILIDAD).finalizaTrazabilidad()
			else:
				actualizado = "Ha sucedido un error"
			return actualizado
			
	def compruebaSiYaSeHaCreadoEvento(self):
		creado = self._db.ejecutaNamedQuery("FD/Platos/YaExisteEventoShowertray", {'tabla':self.TABLA_EVENTO, 'showertray_id':self._showertray_id})
		return creado
		
	def _obtieneParametrosScrap(self):
		ordenes_produccion = fd.clasesordenesprod.gestion.GestorOrdenesProduccion.obtieneOrdenProduccion(self._showertray_id)
		parametros = {
			"showertray_id": self._showertray_id,
			"username": self._usuario,
			"reason_id": self._causa,
			"production_order_id": ordenes_produccion[0]["production_order_id"], 
			"production_order_id_detailed": ordenes_produccion[0]["production_order_id_detailed"]
		}
		return parametros



class EventoRetrabajoPlato:
	
	_showertray_id = ''
	_usuario = ''
	_causa = ''
	_tabla_evento = ''
	
	def __init__(self, showertray_id, usuario, causa):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		self._usuario = usuario
		self._causa = causa
		
	def entradaRetrabajo(self):
		self._tabla_evento = 'rework_showertrays'
		creado = self._compruebaSiYaSeHaCreadoEvento()
		if creado.getRowCount() > 0:
			return "Plato ya actualizado"
		else:
			parametros = self._obtieneParametrosEntradaRetrabajo()
			entrada_retrabajo = self._db.ejecutaNamedQuery('FD/Platos/EntradaRetrabajo', parametros)
			actualizado = ''
			if entrada_retrabajo == 1:
				actualizado = "Plato enviado a retrabajo"
			else:
				actualizado = "Ha sucedido un error"
			return actualizado

		
	def salidaRetrabajo(self, largo, ancho):
		self._tabla_evento = 'rework_end_showertray'
		creado = self._compruebaSiYaSeHaCreadoEvento()
		if creado.getRowCount() > 0:
			return "Plato ya actualizado"
		else:
			parametros = self._obtieneParametrosSalidaRetrabajo(largo, ancho)
			#print(parametros)
			salida_retrabajo = self._db.ejecutaNamedQuery('FD/Platos/SalidaRetrabajo', parametros)
			actualizado = ''
			if salida_retrabajo == 1:
				actualizado = "Plato terminado retrabajo"
			else:
				actualizado = "Ha sucedido un error"
			return actualizado
		
	def _obtieneParametrosEntradaRetrabajo(self):
		parametros = {
			"showertray_id": self._showertray_id,
			"username": self._usuario,
			"causa": self._causa
		}
		return parametros
		
	def _obtieneParametrosSalidaRetrabajo(self, largo, ancho):
		parametros = {
			"showertray_id": self._showertray_id,
			"username": self._usuario,
			"causa": self._causa,
			"largo": largo, 
			"ancho": ancho
		}
		return parametros
		
	def _compruebaSiYaSeHaCreadoEvento(self):
		creado = self._db.ejecutaNamedQuery("FD/Platos/YaExisteEventoShowertray", {'tabla':self._tabla_evento , 'showertray_id':self._showertray_id})
		return creado
		
		


class EventoFinTrazabilidad:
	
	TABLA_EVENTO = 'fin_trazabilidad'
	
	_showertray_id = ''
	_causa = 0
	
	def __init__(self, showertray_id, causa):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		self._causa = causa
		
	def finalizaTrazabilidad(self):
		creado = self._compruebaSiYaSeHaCreadoEvento()
		if creado.getRowCount() > 0:
			return "Plato ya actualizado"
		else:
			trazabilidad_finalizada = self._db.ejecutaNamedQuery('FD/Platos/FinTrazabilidad', {'showertray_id': self._showertray_id, 'causa': self._causa})
			self._compruebaYLimpiaOrdenProduccion()
			EventoCountAsPoured(self._showertray_id).descuentaComoLlenado()
			return trazabilidad_finalizada
		
	def _compruebaSiYaSeHaCreadoEvento(self):
		creado = self._db.ejecutaNamedQuery("FD/Platos/YaExisteEventoShowertray", {'tabla':self.TABLA_EVENTO, 'showertray_id':self._showertray_id})
		return creado
	
	def _compruebaYLimpiaOrdenProduccion(self):
		if self._causa in (2, 3, 4):
			self._db.ejecutaNamedQuery("FD/Platos/LimpiaOrdenProduccion", {'showertray_id':self._showertray_id})



class EventoImpresionEtiquetas:
	
	_showertray_id = ''
	_mold_id = ''
	_nombre_impresora = ''
	
	def __init__(self, showertray_id, mold_id, nombre_impresora):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		self._mold_id = mold_id
		self._nombre_impresora = nombre_impresora
		
	def insertaPlatoYaImpreso(self):
		parametros = self._obtieneParametrosInsertarImpresion()
		self._db.ejecutaNamedQuery('FD/Platos/InsertaEtiquetaHaSidoImpresa', parametros)
			
	def compruebaSiPlatoYaHaSidoImpreso(self):
		cantidad_impresa = self._db.ejecutaNamedQuery('FD/Platos/CompruebaSiEtiquetaYaFueImpresa', {"showertray_id": self._showertray_id, "rfid": True})
		return cantidad_impresa
			
	def _obtieneParametrosInsertarImpresion(self):
		parametros = {
			'showertray_id': self._showertray_id,
			'mold_id': self._mold_id,
			'printer_ip': self._nombre_impresora,
			'place_id': fd.globales.ParametrosGlobales.obtieneIdFabrica()
			}
		return parametros
		



class EventoCortePlato:
	
	LINE_ID_CORTE = 3
	CAUSA_RETRABAJO = 11
	
	def __init__(self, diccionario):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = diccionario['showertray_id']
		self._cut_length = diccionario['cut_length']
		self._cut_width = diccionario['cut_width']
		self._sales_order = diccionario['sales_order']
		self._scanner_id = diccionario['scanner_id']
		self._client_number = diccionario['client_number']
		self._worker_id = diccionario['worker_id']
		self._sku = diccionario['sku']
		self._impresora = diccionario['impresora']
		self._production_order_id = diccionario['production_order_id']
		self._frame_options = diccionario['frame_options']
		self._place_id = diccionario['place_id']
		
	def creaPlatoCorte(self): # Quizas no haga falta que sea publico sino privado
		pass
		
	def _obtieneDatosPlatoOriginal(self):
		consultaNamedQuery = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("FactoryDB", "CodeBase")
		informacion_plato = consultaNamedQuery.ejecutaNamedQuery('FD/Platos/InformacionPlatoDeNumeroSerie', {"showertray_id": self._showertray_id})
		return fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(informacion_plato, 0)
		
	def _compruebaExistenciaEnvasador(self): 
		try:
			self._db.ejecutaNamedQuery('FD/Platos/ObtieneERPIntegration', {'worker_id': self._worker_id})[0]
			return True
		except:
			return False
		
	def _registraEnvasado(self): #Si plato es != None para envasar plato original
		if self._compruebaExistenciaEnvasador():
			if self._obtieneDatosPlatoOriginal():
				pass
		
	def _obtieneClienteDeOrdenProduccion(self): #U obtiene cliente de Sales ORder
		pass
		
	def _generaNuevoShowertrayId(self):
		pass
		
	def _enviaARetrabajo(self):
		EventoRetrabajoPlato(self._showertray_id, self._worker_id, self.CAUSA_RETRABAJO).entradaRetrabajo()
		
	def _imprimeEtiqueta(self):
		fd.moduloetiquetas.servicioetiquetado.EtiquetasVia(self.LINE_ID_CORTE, self._molde, self._showertray_id).etiquetaRfidCorteDekor()
		
	def _platoSalidaDeVia(self):
		EventoFinDeLinea(self._showertray_id, self.LINE_ID_CORTE)
		

class EventoSalidaLlenado:
	
	def __init__(self, showertray_id, mold_id="", line_id=1):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		if mold_id:
			self._mold_id = mold_id
		else:
			self._mold_id = self._obtieneMoldId()
		self._line_id = line_id
		self._place_id =  fd.globales.ParametrosGlobales.obtieneIdFabrica()
		
	def registraEvento(self):
		params={"mold_id":self._mold_id, "showertray_id":self._showertray_id, "t_stamp": system.date.now(), "place_id":self._place_id, "line_id":self._line_id}
		db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'rfid_project')
		result=db.ejecutaNamedQuery('FD/Platos/SalidaLlenado',params)
		params=None
		result=[]
		return
		
	def _obtieneMoldId(self):
		consultaNamedQuery = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("FactoryDB", "CodeBase")
		informacion_plato = consultaNamedQuery.ejecutaNamedQuery('FD/Platos/InformacionPlatoDeNumeroSerie', {"showertray_id": self._showertray_id})
		return informacion_plato[0]["mold_id"]

class EventoFinDeLinea:
	
	ULTIMO_MOLDE_EN_VIA = "[rfid_tags]Events/last_output_mold"
	
	def __init__(self, showertray_id, line_id = 1):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		self._line_id = line_id
		self._place_id =  fd.globales.ParametrosGlobales.obtieneIdFabrica()
		self._insertaFinalDeLinea()
		self._actualizaTag()
		
	def _insertaFinalDeLinea(self):
		parametros = self._generaParametrosInsercion()
		self._db.ejecutaNamedQuery("FD/Platos/InsertaPlatoSalidaVia", parametros)
		
	def _generaParametrosInsercion(self):
		return {
			"mold_id": self._obtieneMoldId(),
			"showertray_id": self._showertray_id,
			"place_id": self._place_id,
			"line_id": self._line_id
			}
			
	def _obtieneMoldId(self):
		consultaNamedQuery = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("FactoryDB", "CodeBase")
		informacion_plato = consultaNamedQuery.ejecutaNamedQuery('FD/Platos/InformacionPlatoDeNumeroSerie', {"showertray_id": self._showertray_id})
		return informacion_plato[0]["mold_id"]
		
	def _actualizaTag(self):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self.ULTIMO_MOLDE_EN_VIA, self._mold_id)


class EventoRegistroCheckPoint:
		
	TIPO_LINEA_PINTURA = "P"
	TIPO_LINEA_DESMOLDEO = "D"
		
	_showertray_id=None
	_mold_id = None
	_nombre_check_point =None
	_id_linea=0
	_t_stamp = None
	_tipo_linea = None
	
	_db = None
		
	def __init__(self, showertray_id, mold_id, nombre_check_point, id_linea, tipo_linea, t_stamp = None):
		
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto("FactoryDB", "CodeBase")
		
		self._showertray_id = showertray_id
		self._mold_id = mold_id
		self._nombre_check_point = nombre_check_point
		self._id_linea = id_linea
		self._tipo_linea = tipo_linea
		if t_stamp:
			self._t_stamp = t_stamp
		else:
			self._t_stamp = system.date.now()
			
	def registraCheckpoint(self):
		params = {
			'showertray_id' : self._showertray_id,
			'mold_id' : self._mold_id,
			'nombre_check_point' : self._nombre_check_point,
			'id_linea': self._id_linea,
			'tipo_linea': self._tipo_linea,
			't_stamp':self._t_stamp
		}
		self._db.ejecutaNamedQuery('FD/Platos/RegistraCheckpoint', params)

class GeneradorListadoSKU:
	
	def __init__(self, modelo, cliente, color, largo, ancho):
		self._consulta = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		self._modelo = modelo
		self._cliente = cliente
		self._color = str(color).zfill(4)
		self._largo = str(largo).zfill(3)
		self._ancho = str(ancho).zfill(3)
	
	def generaListadoSKU(self):
		listado_sku = self._obtieneListadoInicial()
		listado_sku_filtrado = self._filtraListadoSKU(listado_sku)
		listado_sku_filtrado_formateado = self._formateaListadoSKU(listado_sku_filtrado)
		return listado_sku_filtrado_formateado
		
	def _obtieneListadoInicial(self):
		parametros_plato = {'modelo': self._modelo, 'cliente': self._cliente}
		dataset_inicial = self._consulta.ejecutaNamedQuery('FD/Platos/ObtieneListadoSKUDeModleoYCliente', parametros_plato)
		#listado_inicial = [fila[0] for fila in dataset_inicial]
		return dataset_inicial

	def _filtraListadoSKU(self, listado_sku):
		listado_filtrado_color = self._filtraListadoPorColor(listado_sku)
		listado_filtrado_largo = self._filtraListadoPorLargo(listado_filtrado_color)
		listado_filtrado_ancho = self._filtraListadoPorAncho(listado_filtrado_largo)
		return listado_filtrado_ancho
		
	def _filtraListadoPorColor(self, listado_sku):
		if self._color:
			listado_filtrado_color = []
			for sku in listado_sku:
				if sku[0][9:13] == self._color:
					listado_filtrado_color.append(sku)
			return listado_filtrado_color
		else:
			return listado_sku
	
	def _filtraListadoPorLargo(self, listado_sku):
		if self._largo != '000':
			listado_filtrado_largo = []
			for sku in listado_sku:
				if sku[0][3:6] == self._largo:
					listado_filtrado_largo.append(sku) 
			return listado_filtrado_largo
		else:
			return listado_sku
		
	def _filtraListadoPorAncho(self, listado_sku):
		if self._ancho != '000':
			listado_filtrado_ancho = []
			for sku in listado_sku:
				if sku[0][6:9] == self._ancho:
					listado_filtrado_ancho.append(sku)
			return listado_filtrado_ancho
		else:
			return listado_sku	
	
	def _formateaListadoSKU(self, listado_sku_filtrado):
		return [{'id': i + 1, 'SKU': fila[0]} for i, fila in enumerate(listado_sku_filtrado)]
		
		
class EventoCountAsPoured:
	
	RUTA_ACTUALIZA_CONTEO = 'FD/Platos/ActualizaConteoLlenado'
	RUTA_RAZONES_SCRAP_NO_LLENADO = 'FD/Platos/ObtieneRazonesScrapNoLlenado'
	RUTA_RAZONES_FIN_TRAZABILIDAD_NO_LLENADO = 'FD/Platos/ObtieneRazonesFinTrazabilidadNoLlenado'
	POUR_LINE_VALIDAS = [1, 2]
	
	def __init__(self, showertray_id):
		self._consulta = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		self._showertray_id = showertray_id
		self._info_plato = PlatoDucha(showertray_id).obtieneInfoScada()
		self._razones_scrap_descontar = self._obtieneRazonesScrapQueDescuentan()
		self._razones_fin_trazabilidad_descontar = self._obtieneRazonesFinTrazabilidadQueDescuentan()
	
	def cuentaComoLlenado(self):
		if not self._info_plato['count_as_poured'] and self._info_plato['mold_id'] and (self._info_plato['pour_line'] in self.POUR_LINE_VALIDAS or not self._info_plato['pour_line']):
			parametros = {
				'count_as_poured': True,
				'showertray_id': self._showertray_id
			}
			self._consulta.ejecutaNamedQuery(self.RUTA_ACTUALIZA_CONTEO, parametros)
	
	def descuentaComoLlenado(self):
		if self._info_plato['count_as_poured'] and (self._info_plato['scrap_reason'] in self._razones_scrap_descontar or self._info_plato['causa_fin_trazabilidad'] in self._razones_fin_trazabilidad_descontar):
			parametros = {
				'count_as_poured': False,
				'showertray_id': self._showertray_id
			}
			self._consulta.ejecutaNamedQuery(self.RUTA_ACTUALIZA_CONTEO, parametros)
	
	def _obtieneRazonesScrapQueDescuentan(self):
		razones_scrap_crudo = self._consulta.ejecutaNamedQuery(self.RUTA_RAZONES_SCRAP_NO_LLENADO, {})
		razones_scrap = [razon['id'] for razon in razones_scrap_crudo]
		return razones_scrap
	
	def _obtieneRazonesFinTrazabilidadQueDescuentan(self):
		razones_fin_trazabilidad_crudo = self._consulta.ejecutaNamedQuery(self.RUTA_RAZONES_FIN_TRAZABILIDAD_NO_LLENADO, {})
		razones_fin_trazabilidad = [razon['id'] for razon in razones_fin_trazabilidad_crudo]
		return razones_fin_trazabilidad
		
		