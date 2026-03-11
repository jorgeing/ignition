from java.text import SimpleDateFormat

class Etiquetas:
	
	@staticmethod
	def obtieneCarpetaPorSku(sku):
		db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		return db.ejecutaNamedQuery('FD/Etiquetas/ObtieneCarpetaPlantilla', {"sku": sku})
		
	@staticmethod
	def obtieneCarpetaPorCliente(cliente):
		db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		return db.ejecutaNamedQuery('FD/Etiquetas/ObtieneCarpetaPlantillaCliente', {"cliente": cliente})
		
	@staticmethod
	def obtieneSKU(consulta):
		return consulta["sku"]
		
	@staticmethod
	def obtieneCliente(consulta):
		if consulta.has_key("client_number"):
			return consulta["client_number"]
		elif consulta.has_key("client_code"):
			return consulta["client_code"]



class EtiquetaRFID(Etiquetas):
	
	TIPO_ETIQUETA = "rfid_label_template_json.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonDatosRFID'
	
	_impresora = ''
	_servidor = ''
	_showertray_id = ''
	_mold_id = ''
	_datos_diccionario = {}
	_db = None
	
	def __init__(self, via, showertray_id, mold_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaRFID')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		self._showertray_id = showertray_id
		self._mold_id = mold_id
		self._via = via
		
	def imprime(self):
		self._devuelveConsultaABbdd()
		ruta = self._obtieneRutaPlantilla()
		if self._compruebaIntegridadDatos(self._datos_diccionario):
			#self._logger.logInfo(self._datos_diccionario)
			datos_etiqueta = self._generaJsonConDatosAdicionales()
			gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
			http_post = gestor_impresor.imprime(datos_etiqueta)
			#self._logger.logInfo(http_post)
		else:
			fd.moduloetiquetas.modelosetiquetado.EtiquetaBackupVia(self._via, self._mold_id, self._showertray_id).imprime()
		
	def _generaJsonConDatosAdicionales(self):
		json_out = system.util.jsonEncode(self._datos_diccionario)
		return json_out
		
	def _devuelveConsultaABbdd(self):
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, {"showertray_id": self._showertray_id})
		self._datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		
	def _compruebaIntegridadDatos(self, datos_etiqueta):
		if datos_etiqueta["color_id"] is None or datos_etiqueta["color_id"] == '' or datos_etiqueta["color_id"] == 990000:
			return False
		else:
			return True
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _obtieneCarpetaPlantilla(self):
		try:
			sku = Etiquetas.obtieneSKU(self._datos_diccionario)
			cliente = Etiquetas.obtieneCliente(self._datos_diccionario)
			carpeta = ''
			carpeta_sku = Etiquetas.obtieneCarpetaPorSku(sku)
			carpeta_cliente = Etiquetas.obtieneCarpetaPorCliente(cliente)
			
			if carpeta_sku == 'adeo':
				carpeta = carpeta_sku
			elif carpeta_cliente == 'adeo':
				carpeta = carpeta_cliente
			else:
				carpeta = 'default'
			return carpeta
		except:
			return 'default'
		
		
		
class EtiquetaLogistica(Etiquetas):
	
	TIPO_ETIQUETA = "logistic_label_template_json.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosPorID'
	RUTA_CONSULTA_INFO_PLATO = 'FD/Platos/InformacionPlatoDeNumeroSerie'
	RUTA_CONSULTA_INFO_ARTICULO = 'FD/Platos/InformacionArticuloImpresionEtiquetas'
	
	LISTA_ID_CLIENTES_GENERICOS = [99999, 2182, 218]
	
	_logger = None
	
	_impresora = ''
	_servidor = ''
	_showertray_id = ''
	_datos_diccionario = {}
	_info_plato = {}
	_info_articulo = {}
	_db = None
	
	def __init__(self, showertray_id, impresora):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaLogistica')
		self._impresora = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneNombreImpresora()
		self._servidor = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneServidorImpresion()
		self._showertray_id = showertray_id
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		#self._logger.logInfo('ruta: '+str(ruta)+' datos_etiqueta: - '+str(datos_etiqueta))
		etiqueta = gestor_impresor.imprime(datos_etiqueta)
		return etiqueta
		
	def _generaJsonConDatosAdicionales(self):
		self._obtieneDatosImpresion()
		consulta = self._datos_diccionario
		json_out = system.util.jsonEncode(consulta)
		print(json_out)
		return json_out
	
	def _obtieneDatosImpresion(self):
		self._obtieneInfoPlato()
		self._obtieneInfoArticulo()
		self._datos_diccionario = self._construyeParametrosImpresion()
	
	def _obtieneInfoPlato(self):
		info_plato = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA_INFO_PLATO, {"showertray_id": self._showertray_id})
		self._info_plato = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(info_plato, 0)
		self._compruebaClienteGenerico()
		self._compruebaDimensionesCorte()
	
	def _compruebaClienteGenerico(self):
		client_id = self._info_plato['client_number']
		if client_id in self.LISTA_ID_CLIENTES_GENERICOS:
			self._corrigeClienteGenerico()
	
	def _corrigeClienteGenerico(self):
		modelo = self._info_plato['model']
		corrector_etiquetas = fd.moduloetiquetas.correctorclientesetiquetas.CorrectorClientes(modelo)
		cliente_corregido = corrector_etiquetas.corrigeClienteGenerico()
		self._info_plato['client_number'] = cliente_corregido
	
	def _compruebaDimensionesCorte(self):
		dimensiones_corte = self._info_plato['cut_dimension']
		if dimensiones_corte:
			self._info_plato['display_dimension'] = dimensiones_corte
	
	def _obtieneInfoArticulo(self):
		parametros = {
			'sku': self._info_plato['sku'],
			'client_number': self._info_plato['client_number']
		}
		info_articulo = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA_INFO_ARTICULO, parametros)
		self._info_articulo = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(info_articulo, 0)
	
	def _construyeParametrosImpresion(self):
		parametros_impresion = {
			'showertray_id': self._info_plato['showertray_id'],
			'mold_number': self._info_plato['mold_number'],
			'display_date': self._info_plato['label_date'],
			'color': self._info_plato['display_color'],
			'dimension': self._info_plato['display_dimension'],
			'sku': self._info_plato['sku'],
			'client_sku': self._limpiaSaltoDeLineas(self._info_articulo['client_sku']),
			'ean': self._limpiaSaltoDeLineas(self._info_articulo['ean']),
			'client_ean': self._limpiaSaltoDeLineas(self._info_articulo['client_ean']),
			'description': self._info_articulo['description'],
			'client_code': str(self._info_plato['client_number']),
			'model_name': self._info_plato['model'],
			'packaging_worker': self._info_plato['packaging_worker'],
			'color_id': self._info_plato['color_id'],
			'additional_1': self._info_articulo['additional_1'],
			'additional_2': self._info_articulo['additional_2'],
			'cut_dimension': self._info_plato['cut_dimension'],
			'showertray_indx': self._info_plato['showertray_indx'],
			'client_name': self._filtraClienteGrupoEmpresarialIlicitano(),
			'production_order': self._info_plato['production_order_id'],
			'lote': self._generaLoteDeCreated(),
			'peso_bruto': self._info_articulo['peso'],
			'peso_neto': self._info_articulo['peso_neto'],
			'desc_articulo': self._info_articulo['desc_articulo']
		}
		return parametros_impresion
	
	def _filtraClienteGrupoEmpresarialIlicitano(self):
		return 'OMS' if self._info_plato['client_number'] == 2182 or self._info_plato['client_number'] == 99999 else self._info_plato['client_name']
	
	def _limpiaSaltoDeLineas(self, texto):
		if not texto:
			return ''
		else:
			return texto.replace('\r\n', '\n').replace('\r', '\n').strip()
	
	def _generaLoteDeCreated(self):
		fecha_created = self._info_plato['created']
		formato = SimpleDateFormat("yyMMddHHmmss")
		lote = formato.format(fecha_created)
		return lote
	
	def _obtieneParametrosConsulta(self):
		return {"s_id": self._showertray_id, "company_code": self.COD_EMP}
		
	def _obtieneRutaPlantilla(self):
		carpeta_preliminar = self._obtieneCarpetaPlantilla()
		#carpeta_definitiva = self._compruebaCarpetaPlantillaEtiquetaLarga(carpeta_preliminar)
		return carpeta_preliminar + "/" + self.TIPO_ETIQUETA #Cambiar por carpeta definitiva
		
	def _obtieneCarpetaPlantilla(self): 
		sku = Etiquetas.obtieneSKU(self._datos_diccionario)
		cliente = Etiquetas.obtieneCliente(self._datos_diccionario)
		carpeta = ''
		carpeta_sku = Etiquetas.obtieneCarpetaPorSku(sku)
		print(carpeta_sku)
		carpeta_cliente = Etiquetas.obtieneCarpetaPorCliente(cliente)
		print(carpeta_cliente)
		
		if carpeta_sku :
			carpeta = carpeta_sku
		elif carpeta_cliente :
			carpeta = carpeta_cliente
		else:
			carpeta = 'default'
		return carpeta
	
	def _compruebaCarpetaPlantillaEtiquetaLarga(self, carpeta_preliminar):
		carpeta_definitiva = ''
		if carpeta_preliminar == 'adeo' or carpeta_preliminar == 'easy':
			carpeta_definitiva = 'adeo_long'
		else:
			carpeta_definitiva = carpeta_preliminar
		return carpeta_definitiva
		
class EtiquetaA4(Etiquetas):
	
	TIPO_ETIQUETA = "custom_label_template_json.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonDatosCustom'
	RUTA_CONSULTA_INFO_PLATO = 'FD/Platos/InformacionPlatoDeNumeroSerie'
	RUTA_CONSULTA_INFO_ARTICULO = 'FD/Platos/InformacionArticuloImpresionEtiquetas'
	
	LISTA_ID_CLIENTES_GENERICOS = [99999, 2182, 218]
	
	_impresora = ''
	_servidor = ''
	_showertray_id = ''
	_datos_diccionario = {}
	
	_db = None
	
	def __init__(self, impresora, showertray_id): 
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraA4(impresora)
		self._servidor = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneServidorImpresion()
		self._showertray_id = showertray_id
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaA4')
		#self._logger.logInfo('impresora A4 seleccionada: '+str(self._impresora))
		
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		#self._logger.logInfo('A4datos_etiqueta: '+str(datos_etiqueta))
		ruta = self._obtieneRutaPlantilla()
		#self._logger.logInfo(ruta)
		if not ruta:
			return
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		gestor_impresor.imprime(datos_etiqueta)
		
	def _generaJsonConDatosAdicionales(self):
		#self._devuelveConsultaABbdd()#ANTIGUO
		self._obtieneDatosImpresion()
		json_out = system.util.jsonEncode(self._datos_diccionario)
		return json_out
		
	def _devuelveConsultaABbdd(self):#ANTIGUO
		parametros = self._obtieneParametrosConsulta()
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, parametros)
		self._datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
	
	def _obtieneDatosImpresion(self):#REVISAR
		self._obtieneInfoPlato()
		self._obtieneInfoArticulo()
		self._datos_diccionario = self._construyeParametrosImpresion()
	
	def _obtieneInfoPlato(self):
		info_plato = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA_INFO_PLATO, {"showertray_id": self._showertray_id})
		self._info_plato = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(info_plato, 0)
		self._compruebaClienteGenerico()
		self._compruebaDimensionesCorte()
	
	def _compruebaClienteGenerico(self):
		client_id = self._info_plato['client_number']
		if client_id in self.LISTA_ID_CLIENTES_GENERICOS:
			self._corrigeClienteGenerico()
	
	def _corrigeClienteGenerico(self):
		modelo = self._info_plato['model']
		corrector_etiquetas = fd.moduloetiquetas.correctorclientesetiquetas.CorrectorClientes(modelo)
		cliente_corregido = corrector_etiquetas.corrigeClienteGenerico()
		self._info_plato['client_number'] = cliente_corregido
	
	def _compruebaDimensionesCorte(self):
		dimensiones_corte = self._info_plato['cut_dimension']
		if dimensiones_corte:
			self._info_plato['display_dimension'] = dimensiones_corte
	
	def _obtieneInfoArticulo(self):
		parametros = {
			'sku': self._info_plato['sku'],
			'client_number': self._info_plato['client_number']
		}
		info_articulo = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA_INFO_ARTICULO, parametros)
		self._info_articulo = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(info_articulo, 0)
	
	def _construyeParametrosImpresion(self):
		parametros_impresion = {
			'showertray_id': self._info_plato['showertray_id'],
			'mold_number': self._info_plato['mold_number'],
			'display_date': self._info_plato['label_date'],
			'color': self._info_plato['display_color'],
			'dimension': self._info_plato['display_dimension'],
			'sku': self._info_plato['sku'],
			'client_sku': self._info_articulo['client_sku'],
			'ean': self._info_articulo['ean'],
			'client_ean': self._info_articulo['client_ean'],
			'description': self._info_articulo['description'],
			'client_code': str(self._info_plato['client_number']),
			'model_name': self._info_plato['model'],
			'packaging_worker': self._info_plato['packaging_worker'],
			'color_id': self._info_plato['color_id'],
			'additional_1': self._info_articulo['additional_1'],
			'additional_2': self._info_articulo['additional_2'],
			'cut_dimension': self._info_plato['cut_dimension'],
			'showertray_indx': self._info_plato['showertray_indx'],
			'librec1': self._info_articulo['librec1'],
			'librec2': self._info_articulo['librec2'],
			'librec3': self._info_articulo['librec3'],
			'librec4': self._info_articulo['librec4'],
			'librec5': self._info_articulo['librec5'],
			'librec6': self._info_articulo['librec6'],
			'librec7': self._info_articulo['librec7'],
			'librec8': self._info_articulo['librec8'],
			'librec9': self._info_articulo['librec9'],
			'librec10': self._info_articulo['librec10'],
			'peso': self._info_articulo['peso']
		}
		return parametros_impresion
		
	def _obtieneParametrosConsulta(self):
		return {"showertray_id": self._showertray_id, "cod_emp": self.COD_EMP}
		
	def _obtieneRutaPlantilla(self):
		carpeta_plantilla = self._obtieneCarpetaPlantilla()
		if not carpeta_plantilla:
			return
		return carpeta_plantilla + "/" + self.TIPO_ETIQUETA
		
	def _obtieneCarpetaPlantilla(self):
		sku = Etiquetas.obtieneSKU(self._datos_diccionario)
		cliente = Etiquetas.obtieneCliente(self._datos_diccionario)
		carpeta = ''
		carpeta_sku = Etiquetas.obtieneCarpetaPorSku(sku)
		carpeta_cliente = Etiquetas.obtieneCarpetaPorCliente(cliente)
		if carpeta_sku != '':
			carpeta = carpeta_sku
		elif carpeta_cliente != '':
			carpeta = carpeta_cliente
		else:
			carpeta = 'default'
		return carpeta
		
		
class EtiquetaUSA(Etiquetas):
	
	TIPO_ETIQUETA = "molde_usa.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosPorID'
	
	_impresora = ''
	_showertray_id = ''
	_servidor = ''
	_datos_diccionario = {}
	
	_db = None
	
	def __init__(self, via, showertray_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._showertray_id = showertray_id
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaUSA')
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		http_post = gestor_impresor.imprime(datos_etiqueta)
		return http_post
		
	def _generaJsonConDatosAdicionales(self):
		consulta = self._devuelveConsultaABbdd()
		json_out = system.util.jsonEncode(consulta)
		return json_out
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _devuelveConsultaABbdd(self):
		parametros = self._obtieneParametrosConsulta()
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, parametros)
		#self._logger.logInfo("showertray_id: "+str(self._showertray_id)+" - datos: "+str(datos))
		datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		return datos_diccionario
		
	def _obtieneParametrosConsulta(self):
		return {"s_id": self._showertray_id, "company_code": self.COD_EMP}
		
class EtiquetaSchulte(Etiquetas):
	
	TIPO_ETIQUETA = "molde_schulte.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosPorID'
	
	_impresora = ''
	_showertray_id = ''
	_servidor = ''
	_datos_diccionario = {}
	
	_db = None
	
	def __init__(self, via, showertray_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._showertray_id = showertray_id
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaSchulte')
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		http_post = gestor_impresor.imprime(datos_etiqueta)
		return http_post
		
	def _generaJsonConDatosAdicionales(self):
		consulta = self._devuelveConsultaABbdd()
		json_out = system.util.jsonEncode(consulta)
		return json_out
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _devuelveConsultaABbdd(self):
		parametros = self._obtieneParametrosConsulta()
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, parametros)
		#self._logger.logInfo("showertray_id: "+str(self._showertray_id)+" - datos: "+str(datos))
		datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		return datos_diccionario
		
	def _obtieneParametrosConsulta(self):
		return {"s_id": self._showertray_id, "company_code": self.COD_EMP}


class EtiquetaMoldes(Etiquetas):
	
	TIPO_ETIQUETA = "mold_attention_json.btw"
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosMoldes'
	
	_impresora = ''
	_servidor = ''
	_mold_id = ''
	_datos_diccionario = {}
	
	_db = None
	
	
	def __init__(self, via, mold_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._mold_id = mold_id
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		http_post = gestor_impresor.imprime(datos_etiqueta)
		return http_post
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _generaJsonConDatosAdicionales(self):
		self._devuelveConsultaABbdd()
		consulta = self._datos_diccionario
		json_out = system.util.jsonEncode(consulta)
		return json_out
		
	def _devuelveConsultaABbdd(self):
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, {"mold_id": self._mold_id})
		self._datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)

class EtiquetaLimpiezaPlayasMoldes(Etiquetas):
	
	TIPO_ETIQUETA = "mold_limpieza_playa_json.btw"
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosMoldes'
	
	_impresora = ''
	_servidor = ''
	_mold_id = ''
	_datos_diccionario = {}
	
	_db = None
	
	def __init__(self, via, mold_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._mold_id = mold_id
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		http_post = gestor_impresor.imprime(datos_etiqueta)
		return http_post
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _generaJsonConDatosAdicionales(self):
		self._devuelveConsultaABbdd()
		consulta = self._datos_diccionario
		json_out = system.util.jsonEncode(consulta)
		return json_out
		
	def _devuelveConsultaABbdd(self):
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, {"mold_id": self._mold_id})
		self._datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)

class EtiquetaTagMoldes(Etiquetas):
	
	TIPO_ETIQUETA =  'etiqueta_tag_molde_json.btw'
	RUTA_CONSULTA_INFO_MOLDE = 'FD/Etiquetas/ObtieneJsonConDatosPorIDMolde'
	
	_db = None

	def __init__(self, id_molde, epc_etiqueta_dec):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraAreaMoldes()
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()  
		self._id_molde = id_molde
		self._epc_etiqueta_dec = epc_etiqueta_dec
		self._epc_etiqueta_hex = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal.convierteUuidDecimalEnHexadecimal(epc_etiqueta_dec)
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaTagMoldes')
	
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		#self._logger.logInfo('datos_etiqueta: '+str(datos_etiqueta))
		ruta = self._obtieneRutaPlantilla()
		#self._logger.logInfo(ruta)
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		gestor_impresor.imprime(datos_etiqueta)
	
	def _generaJsonConDatosAdicionales(self):
		self._obtieneDatosImpresion()
		json_out = system.util.jsonEncode(self._datos_diccionario)
		return json_out
	
	def _obtieneDatosImpresion(self):
		self._obtieneInfoMolde()
		self._datos_diccionario = self._construyeParametrosImpresion()
	
	def _obtieneInfoMolde(self):
		info_molde = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA_INFO_MOLDE, {"id_molde": self._id_molde})
		self._info_molde = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(info_molde, 0)
	
	def _construyeParametrosImpresion(self):
		parametros_impresion = {
			'epc_etiqueta_dec': self._epc_etiqueta_dec,
			'epc_etiqueta_hex': self._epc_etiqueta_hex,
			'descripcion_molde': self._generaDescripcionMolde(),
			'numero_molde': self._info_molde['numero_molde'],
			'id_modelo_molde': self._info_molde['model_id'],
			'sku_molde': self._info_molde['mold_sku'],
			'fecha_alta_molde': self._info_molde['fecha_alta']
		}
		return parametros_impresion
	
	def _generaDescripcionMolde(self):
		return self._info_molde['modelo_nombre_largo'] + ' - ' + str(self._info_molde['length']) + ' X ' + str(self._info_molde['width'])
	
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
	
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta

class EtiquetaBackupVia(Etiquetas):
	
	TIPO_ETIQUETA = "etiqueta_backup_json.btw"
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonDatosRFID'
	
	_impresora = ''
	_servidor = ''
	_mold_id = ''
	_showertray_id = ''
	_datos_diccionario = {}
	
	_db = None
	
	def __init__(self, via, mold_id, showertray_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		self._showertray_id = showertray_id
		self._mold_id = mold_id
		
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = "/default/"+self.TIPO_ETIQUETA
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		http_post = gestor_impresor.imprime(datos_etiqueta)
		return http_post
		
	def _generaJsonConDatosAdicionales(self):
		self._devuelveConsultaABbdd()
		json_out = system.util.jsonEncode(self._datos_diccionario)
		return json_out
		
	def _devuelveConsultaABbdd(self):
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, {"showertray_id": self._showertray_id})
		datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		#datos_diccionario["showertray_id"] = self._showertray_id
		self._datos_diccionario = datos_diccionario





class EtiquetaRFIDCorteDekor(Etiquetas):
	
	TIPO_ETIQUETA = "cut_dekor_template_json.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Platos/InformacionPlatoDeNumeroSerie'
	
	_impresora = ''
	_servidor = ''
	_showertray_id = ''
	_datos_diccionario = {}
	
	_db = None
	
	def __init__(self, via, showertray_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = fd.utilidades.impresoras.ConfiguracionImpresoras().obtieneImpresoraRFID(via)
		self._servidor = fd.utilidades.impresoras.InformacionPorNombreImpresoras(self._impresora).obtieneServidorImpresion()
		self._showertray_id = showertray_id
		self._via = via
		
	def imprime(self):
		self._devuelveConsultaABbdd()
		ruta = self._obtieneRutaPlantilla()
		if self._compruebaSiEsDekorOCorte(self._datos_diccionario):
			datos_etiqueta = self._generaJsonConDatosAdicionales()
			gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
			http_post = gestor_impresor.imprime(datos_etiqueta)
		
	def _generaJsonConDatosAdicionales(self):
		json_out = system.util.jsonEncode(self._datos_diccionario)
		return json_out
		
	def _devuelveConsultaABbdd(self):
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, {"showertray_id": self._showertray_id})
		self._datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		
	def _compruebaSiEsDekorOCorte(self, datos_etiqueta): #modifiar
		if datos_etiqueta["rfid_additional_instructions"] == 'CORTE' or datos_etiqueta["rfid_additional_instructions"] == 'DEKOR':
			return True
		else:
			return False
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA


class EtiquetaUbicacionInventario(Etiquetas):
	
	TIPO_ETIQUETA = "etiqueta_ubicacion_inventario.btw"
	
	_impresora = ''
	_servidor = ''
	_ubicacion = ''
	_almacen = ''
	_codigo_barras = ''
	
	def __init__(self, ubicacion, almacen, codigo_barras, impresora):
		self._impresora = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneNombreImpresora()
		self._servidor = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneServidorImpresion()
		self._ubicacion = ubicacion
		self._almacen = almacen
		self._codigo_barras = codigo_barras
	
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		gestor_impresor.imprime(datos_etiqueta)
		
	def _generaJsonConDatosAdicionales(self):
		parametros = {
			'ubicacion': self._ubicacion,
			'almacen': self._almacen,
			'codigo_barras': self._codigo_barras
		}
		json_out = system.util.jsonEncode(parametros)
		return json_out
	
	def _obtieneRutaPlantilla(self):
		return "ubicaciones_inventario/" + self.TIPO_ETIQUETA
		




class EtiquetasInteriores:
	
	TIPO_ETIQUETA = "etiqueta_vacia_json.btw"
	
	
	def __init__(self, impresora):
		self._impresora = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneNombreImpresora()
		self._servidor = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneServidorImpresion()
		
	def imprime(self):
		ruta = self._obtieneRutaPlantilla()
		datos_etiqueta = {}
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		gestor_impresor.imprime(system.util.jsonEncode(datos_etiqueta))
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		

class EtiquetaLargaLogistica:
	
	TIPO_ETIQUETA = "long_label_template_json.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosPorID'
	
	_impresora = ''
	_servidor = ''
	_showertray_id = ''
	_datos_diccionario = {}
	
	_db =None
	
	def __init__(self, showertray_id, impresora):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaLargaLogistica')
		self._impresora = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneNombreImpresora()
		self._servidor = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneServidorImpresion()
		self._showertray_id = showertray_id
		
	def imprime(self):
		datos_etiqueta = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		#self._logger.logInfo('ruta: '+str(ruta)+' datos_etiqueta: - '+str(datos_etiqueta))
		etiqueta = gestor_impresor.imprime(datos_etiqueta)
		return etiqueta
		
	def _generaJsonConDatosAdicionales(self):
		self._devuelveConsultaABbdd()
		consulta = self._datos_diccionario
		json_out = system.util.jsonEncode(consulta)
		print(json_out)
		return json_out
		
	def _devuelveConsultaABbdd(self):
		parametros = self._obtieneParametrosConsulta()
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, parametros)
		self._datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		
	def _obtieneParametrosConsulta(self):
		return {"s_id": self._showertray_id, "company_code": self.COD_EMP}
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _obtieneCarpetaPlantilla(self):
		sku = Etiquetas.obtieneSKU(self._datos_diccionario)
		cliente = Etiquetas.obtieneCliente(self._datos_diccionario)
		carpeta = ''
		carpeta_sku = Etiquetas.obtieneCarpetaPorSku(sku)
		carpeta_cliente = Etiquetas.obtieneCarpetaPorCliente(cliente)
		
		if carpeta_sku :
			carpeta = carpeta_sku
		elif carpeta_cliente :
			carpeta = carpeta_cliente
		else:
			carpeta = 'default'
		return carpeta


class EtiquetaPedidos(Etiquetas):
	
	TIPO_ETIQUETA = "info_pedido_json.btw"
	RUTA_CONSULTA = 'FD/Etiquetas/ObtieneJsonConDatosPedido'
	
	_impresora = ''
	_servidor = ''
	_numero_pedido = ''
	_anyo_pedido = ''
	_datos_diccionario = []
	
	_db = None
	
	def __init__(self, impresora, numero_pedido, anyo_pedido):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EtiquetaPedidos')
		self._impresora = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneNombreImpresora()
		self._servidor = fd.utilidades.impresoras.InformacionImpresoras(impresora).obtieneServidorImpresion()
		self._numero_pedido = numero_pedido
		self._anyo_pedido = anyo_pedido
		
	def imprime(self):
		datos_etiquetas = self._generaJsonConDatosAdicionales()
		ruta = self._obtieneRutaPlantilla()
		#self._logger.logInfo('ruta: '+str(ruta)+' datos_etiquetas: - '+str(datos_etiquetas))
		gestor_impresor = fd.moduloetiquetas.impresionetiquetas.ImpresorEtiquetas(self._impresora, ruta, self._servidor)
		etiquetas_impresas = []
		for etiqueta_json in datos_etiquetas:
			#self._logger.logDebug('Imprimiendo etiqueta con payload: ' + str(etiqueta_json))
			res = gestor_impresor.imprime(etiqueta_json)
			etiquetas_impresas.append(res)
		return etiquetas_impresas
		
	def _obtieneCarpetaPlantilla(self):
		carpeta = 'etiquetas_adicionales'
		return carpeta
		
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaPlantilla() + "/" + self.TIPO_ETIQUETA
		
	def _generaJsonConDatosAdicionales(self):
		self._devuelveConsultaABbdd()
		lista_etiquetas_json = []
		for etiqueta in self._datos_diccionario:
			json_out = system.util.jsonEncode(etiqueta)
			lista_etiquetas_json.append(json_out)
		return lista_etiquetas_json
		
	def _devuelveConsultaABbdd(self):
		datos = self._db.ejecutaNamedQuery(self.RUTA_CONSULTA, {"numero_pedido": self._numero_pedido, "anyo_pedido": self._anyo_pedido})
		self._datos_diccionario = []
		try:
			cantidad_etiquetas = datos.getRowCount()
		except:
			cantidad_etiquetas = 0

		for i in range(cantidad_etiquetas):
			pedido = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, i)
			cantidad = pedido.get('cantidad')
			try:
				cantidad = int(cantidad) if cantidad is not None else 1
			except:
				cantidad = 1
			if cantidad <= 0:
				cantidad = 1

			for _ in range(cantidad):
				self._datos_diccionario.append(dict(pedido))