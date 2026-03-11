class ProcesadorTagsDeAntena:
	
	_nombre_antena = ''
	_path_json_antena=''
	_json_antena = ''
	_path_objeto_destino=''
	_objeto_destino_inicial = {}
	_objeto_destino = {}
	
	_procesador_antena = None
	
	def __init__(self, nombre_antena, path_json_lectura_antena, path_objeto_destino, tag_utiliza_string_plano = False):
		self._nombre_antena = nombre_antena
		self._path_json_antena = path_json_lectura_antena
		self._path_objeto_destino = path_objeto_destino
		
		self._json_antena = fd.utilidades.tags.GestorTags.leeValorDeUnTag(path_json_lectura_antena)
		self._objeto_destino_inicial = fd.utilidades.tags.GestorTags.leeValorDeUnTag(path_objeto_destino)
		
		self._procesador_antena = fd.rfid.procesaantena.ProcesadorAntena(self._nombre_antena, self._json_antena, self._objeto_destino_inicial, tag_utiliza_string_plano)
	
	def procesaYEscribeEnDestino(self):
		self._objeto_destino = self._procesador_antena.procesaDatosAntena()
		self._escribeObjetoDestino()
	
	def _escribeObjetoDestino(self):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._path_objeto_destino, self._objeto_destino)
		