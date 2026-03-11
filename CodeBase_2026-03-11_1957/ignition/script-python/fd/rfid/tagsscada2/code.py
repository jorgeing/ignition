"""Refactorizado con IA, validar antes"""

class ProcesadorTagsDeAntena2:
	"""Orquesta la lectura de tags de una antena RFID usando ProcesadorAntena2 y escribe el resultado en el tag de destino."""

	_nombre_antena = ''
	_path_json_antena=''
	_json_antena = ''
	_path_objeto_destino=''
	_objeto_destino_inicial = {}
	_objeto_destino = {}
	
	_procesador_antena = None
	
	def __init__(self, nombre_antena, path_json_lectura_antena, path_objeto_destino, tag_utiliza_string_plano = False):
		"""Inicializa el procesador cargando los datos actuales del tag y creando el procesador de antena versión 2."""
		self._nombre_antena = nombre_antena
		self._path_json_antena = path_json_lectura_antena
		self._path_objeto_destino = path_objeto_destino
		
		self._json_antena = fd.utilidades.tags.GestorTags.leeValorDeUnTag(path_json_lectura_antena)
		self._objeto_destino_inicial = fd.utilidades.tags.GestorTags.leeValorDeUnTag(path_objeto_destino)
		
		self._procesador_antena = fd.rfid.procesaantena2.ProcesadorAntena2(self._nombre_antena, self._json_antena, self._objeto_destino_inicial, tag_utiliza_string_plano)
	
	def procesaYEscribeEnDestino(self):
		"""Procesa los datos de la antena usando ProcesadorAntena2 y escribe el resultado en el tag de destino."""
		self._objeto_destino = self._procesador_antena.procesar()
		self._escribeObjetoDestino()
	
	def _escribeObjetoDestino(self):
		"""Escribe el objeto resultado procesado en el tag de destino del sistema SCADA."""
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._path_objeto_destino, self._objeto_destino)
		