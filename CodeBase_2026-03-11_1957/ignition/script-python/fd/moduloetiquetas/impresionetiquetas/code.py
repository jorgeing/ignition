class ImpresorEtiquetas:
	"""Gestiona la impresión de etiquetas mediante peticiones HTTP."""
	
	_impresora = ''
	_ruta = ''
	_servidor = ''
	
	def __init__(self, impresora, ruta, servidor):
		"""Inicializa con nombre de impresora, ruta de plantilla y servidor."""
		self._impresora = impresora
		self._ruta = ruta
		self._servidor = servidor
		
	def imprime(self, datos_etiqueta):
		"""Envía la petición HTTP POST para imprimir la etiqueta."""
		url = self._generaUrlConServidor()
		datos_impresion = self._construyeJsonPeticion(datos_etiqueta)
		http_post = system.net.httpPost(url,'application/json', datos_impresion)
		return datos_impresion
		
	def _construyeJsonPeticion(self, datos_etiqueta):
		"""Construye el JSON con impresora, ruta y datos adicionales."""
		diccionario = {
			'impresora':self._impresora, 
			'ruta_plantilla': self._ruta,
			'additional_data':datos_etiqueta
		}
		json=system.util.jsonEncode(diccionario)
		logger = system.util.getLogger("impresion etiquetas")
		logger.info(str(json))
		return json
		
	def _generaUrlConServidor(self):
		"""Genera la URL completa del servidor de impresión."""
		logger = system.util.getLogger("impresion etiquetas")
		logger.info(str(self._servidor))
		return 'http://'+self._servidor+':9081/Integration/logistic_labels_json/Execute'
		