from fd.utilidades.impresoras import *
import json

class eventoImpresionEtiquetasArticulo:
	_impresora = None
	_sku = None
	_cliente = None
	_cantidad = 0
	
	def __init__(self, id_impresora, cantidad, sku, cliente):
		self._impresora = id_impresora
		self._sku = sku
		self._cliente = cliente
		self._cantidad = cantidad
		
	def imprimeEtiquetaArticulo(self):
		puerto_path = ':9081/Integration/etiqueta_articulo/Execute'
		url_bartender = self._contruyeUrlEtiquetaArticulo(puerto_path)
		parametros = self._generaParametrosParaImpresionEtiquetaArticulos()
		parametros_json = self._codificacionJson(parametros)
		self._ejecucionEndpoint(url_bartender, parametros_json)
		
	def imprimeEtiquetaMarmite(self):
		puerto_path = ':9081/Integration/logistic_labels_angelina/Execute'
		url_bartender = self._contruyeUrlEtiquetaArticulo(puerto_path)
		parametros = self._generaParametrosParaImpresionEtiquetaMarmite()
		parametros_json = self._codificacionJson(parametros)
		self._ejecucionEndpoint(url_bartender, parametros_json)
		
	def _contruyeUrlEtiquetaArticulo(self, puerto_path):
		servidor_impresion = fd.utilidades.impresoras.InformacionImpresoras(self._impresora).obtieneServidorImpresion()
		url_bartender = 'http://'+ servidor_impresion + puerto_path
		return url_bartender
		
	def _generaParametrosParaImpresionEtiquetaArticulos(self):
		parametros = {
			'cod_emp':'01',
			'impresora': fd.utilidades.impresoras.InformacionImpresoras(self._impresora).obtieneNombreImpresora(),
			'sku': self._sku,
			'cod_cli': self._cliente,
			'cantidad': self._cantidad
		}
		return parametros
		
	def _generaParametrosParaImpresionEtiquetaMarmite(self):
		parametros = {
			'cod_emp':'01',
			'impresora': fd.utilidades.impresoras.InformacionImpresoras(self._impresora).obtieneNombreImpresora(),
			'sku': self._sku
		}
		return parametros
		
	def _codificacionJson(self, parametros):
		parametros_json = system.util.jsonEncode(parametros)
		return parametros_json
		
	def _ejecucionEndpoint(self, url_bartender, parametros_json):
		try:
			system.net.httpPost(url_bartender, 'text', parametros_json)
		except Exception as e:
			raise Exception('No se ha podido enviar peticion hhtp: ' + str(e)) 






class eventoImpresionEtiquetas:
	_sku = ''
	_id_cliente = ''
	_numero_serie = ''
	_escaner = 0
	_trabajador = 0
	_impresora = 0
	_cantidad = 1
	_informacion_impresora = None
	
	def __init__(self, sku, id_cliente, escaner, trabajador, id_impresora):
		self._sku = sku
		self._id_cliente = id_cliente
		generador_numero_serie = fd.numerosserie.GeneradorNumeroSeriePlato.contruyeDesdeSku(self._sku, self._id_cliente)
		self._numero_serie = generador_numero_serie.obtieneNumeroSerie().encode('ascii')
		self._escaner = escaner
		self._trabajador = trabajador
		self._informacion_impresora = InformacionImpresoras(id_impresora)
		
		
	def imprimirEtiquetasRFID(self, impresora_rfid):
		pass
		
	def imprimirEtiquetasManual(self, manual_print_reason, corte_largo = '', corte_ancho = ''):
		manual_print_reason=-1
		parametros = self._obtenerParametrosParaEmpaquetarPlato(manual_print_reason, corte_largo = '', corte_ancho = '')
		# A4
		
	def imprimirEtiquetasPlatosEnvasados(self):
		pass
		
		
		
	def _obtieneColorDeSku(self):
		return self._sku[9:13]
		
	def _compruebaSiHayCorte(self, corte):
		if corte == 0 or corte == '':
			corte = 'null'
		return corte
		
	def _contruyeUrlImpresion(self): #SOLO RESIBLOCK CAMBIAR!!!!!!
		servidor_impresion = self._informacion_impresora.obtieneServidorImpresion()
		url_bartender = 'http://'+ servidor_impresion +':9081/Integration/logistic_labels_v4_quantity/Execute'
		return url_bartender
		
	def _etiquetasEspeciales(self):
		pass
		
	def _compruebaSiNecesitaEtiquetasRFID(self):
		pass
		#pyevents.eventFunctions.printLineLabel(mold_id,url,rfid,printer_name,printing )
		#printLineLabel(rfid_mold_id,url,rfid,rfid_printer_name,printing, showertray_id)
		#[rfid_tags]Tests/tag_test_1.value
		






class ImpresionEtiquetas:
	
	TIPO_ETIQUETA_RFID = "rfid_label_template_json.btw"
	TIPO_ETIQUETA_LOGISTICA = "logistic_label_template_json.btw"
	TIPO_ETIQUETA_A4 = "custom_label_template.btw"
	TIPO_ETIQUETA_USA = "molde_usa.btw"
	COD_EMP = fd.globales.ParametrosGlobales.obtieneCodEmp()
	
	_impresora = ''
	_showertray_id = ''
	_codigo_empresa = ''
	_tipo_etiqueta = ''
	
	def __init__(self, impresora, showertray_id, codigo_empresa, tipo_etiqueta = TIPO_ETIQUETA_LOGISTICA):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._impresora = impresora
		self._showertray_id = showertray_id
		self._codigo_empresa = codigo_empresa
		self._tipo_etiqueta = tipo_etiqueta
		
	def generaJsonConParametrosImpresion(self):
		parametros = {
			"showertray_id": self._showertray_id,
			"impresora": self._impresora,
			"cod_emp": '01',
			"ruta_plantilla": self._obtieneRutaPlantilla(),
			"additional_data": self._generaJsonConDatosAdicionales()
		}
		return parametros
		
	def _generaJsonConDatosAdicionales(self):
		consulta = self._devuelveConsultaABbdd()
		json_out = system.util.jsonEncode(consulta)
		return json_out
	
	def _obtieneRutaPlantilla(self):
		return self._obtieneCarpetaDePlantilla() + "/" + self._tipo_etiqueta
	
	def _obtieneCarpetaDePlantilla(self):
		sku = self._obtieneSKU()
		cliente = self._obtieneCliente()
		
		carpeta_sku = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneCarpetaPlantilla', {"sku": sku})
		carpeta_cliente = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneCarpetaPlantillaCliente', {"cliente": cliente})
		if carpeta_sku != '':
			carpeta = carpeta_sku[0][0]
		elif carpeta_cliente != '':
			carpeta = carpeta_cliente[0][0]
		else:
			carpeta = 'default'
		return carpeta
	
	def _obtieneSKU(self):
		consulta = self._devuelveConsultaABbdd()
		return consulta["sku"]
		
	def _devuelveConsultaABbdd(self):
		parametros = self._obtieneParametrosConsulta()
		datos = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneJsonConDatosPorID', parametros)
		datos_diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(datos, 0)
		return datos_diccionario
		
	def _obtieneCliente(self):
		consulta = self._devuelveConsultaABbdd()
		return consulta["client_code"]
		
	def _obtieneParametrosConsulta(self):
		return {"s_id": self._showertray_id, "company_code": self._codigo_empresa}
		
		
		
class EtiquetasAdicionalesVia(ImpresionEtiquetas):
	
	def __init__(self):
		pass
		
	def imprimeEtiquetaUSA(self):
		pass
		
	"""gestor_impresion_etiquetas = fd.etiquetas.ImpresionEtiquetas(impresora, showertray_id, '01', tipo_etiqueta)
	datos_impresion = gestor_impresion_etiquetas.generaJsonConParametrosImpresion()
	json=system.util.jsonEncode(datos_impresion)
	system.net.httpPost(bartender_url,'text', json)"""