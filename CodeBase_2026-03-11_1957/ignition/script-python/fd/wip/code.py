class GestionMotivosScrap:
	
	_razon = ''
	_showertray_id = ''
	_url = ''
	_parametros = {}
	
	def __init__(self, razon, showertray_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._razon = razon
		self._showertray_id = showertray_id
		
	def asignaMotivo(self):
		self._compruebaRazonScrap()
		motivo_asignado = system.net.httpPost(self._url, "application/json", self._parametros)
		return motivo_asignado
		
	def _compruebaRazonScrap(self):
		if self._razon == 100:
			self._url = self._generaUrlDesmoldeo()
			self._parametros = self._generaParametrosPeticionDesmoldeo()
			
		elif self._razon == 200:
			self._url = self._generaUrlEnvasado()
			self._parametros = self._generaParametrosPeticionEnvasado()
			
		else:
			self._url = self._generaUrlScrap()
			self._parametros = self._generaParametrosPeticionScrap()
			
	def _obtieneDatosDeShowertray(self):
		dataset = self._db.ejecutaNamedQuery('FD/Utilidades/ObtieneInfoShowertray', {'showertray_id': self._showertray_id})
		if dataset.getRowCount()>0:
			diccionario = fd.utilidades.dataset.ConversorFormatosDataset.filaDatasetADiccionario(dataset, 0)
			return diccionario
		else:
			return None
			
	def _generaUrlDesmoldeo(self):
 
		return url_desmoldeo
		
	def _generaParametrosPeticionDesmoldeo(self):
		parametros = {
			"showertray_id":self._showertray_id,
			"mold_id":''
		}
		
	def _generaUrlEnvasado(self):
		url_envasado = 'http://172.16.0.28:8088/system/webdev/rfid_project/packaging/registerPackedShowertray_v4'
		return url_envasado
		
	def _generaParametrosPeticionEnvasado(self):
		datos = self._obtieneDatosDeShowertray()
		parametros={
			"showertray_id":self._showertray_id,
			"device_id":-2,
			"client_id":datos["client_number"],
			"printer_id":999,
			"worker_id":0,
			"sku":datos["sku"],
			"color_id":datos["color_id"]
		}
		
	def _generaUrlScrap(self):
		url_scrap = 'http://172.16.0.28:8088/system/webdev/rfid_project/events/scrap_showertray'
		return url_scrap
		
	def _generaParametrosPeticionScrap(self):
		parametros={
			"showertray_id":self._showertray_id,
			"worker_id": self.session.props.auth.user.userName,
			"scrap_reason": self.getSibling("Dropdown").props.value,
			"production_order_id":self.view.params.value.value.production_order_id,
			"production_order_id_detailed":self.view.params.value.value.production_order_id_detailed,
		}
		
	def _codificaJson(self, parametros):
		return system.util.jsonEncode(parametros)
		