from fd.utilidades.impresoras import *

class eventoImpresionEtiquetasPorSku:
	
	MAX_CANTIDAD_ETIQUETAS = 60
	
	_sku = ''
	_id_cliente = ''
	_numero_serie = ''
	_escaner = 0
	_trabajador = 0
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
		
	def imprimirEtiquetasLogisticaPorSkuYCantidad(self, cantidad):
		self._cantidad = cantidad
		self._compruebaCantidadPeticionEtiquetas()
		
		url_bartender = self._contruyeUrlImpresion()
		
		parametros_json = self._generaJsonEtiquetasConSkuYCantida()
		system.net.httpPost(url_bartender,'text' ,parametros_json)
	
	def _contruyeUrlImpresion(self):
		servidor_impresion = self._informacion_impresora.obtieneServidorImpresion()
		url_bartender = 'http://'+ servidor_impresion +':9081/Integration/logistic_labels_v4_quantity/Execute'
		return url_bartender
	
	def _generaJsonEtiquetasConSkuYCantida(self):
		impresora = self._informacion_impresora.obtieneNombreImpresora()
		jsonc = {'impresora': impresora, 'sku': self._sku, 'cod_emp': fd.globales.ParametrosGlobales.obtieneCodEmp(), 'cantidad': int(self._cantidad)}
		print(jsonc)
		json = system.util.jsonEncode(jsonc)
		return json
		
	def _compruebaCantidadPeticionEtiquetas(self):
		if self._cantidad > self.MAX_CANTIDAD_ETIQUETAS:
			raise Exception('Numero de etiquetas no válido')