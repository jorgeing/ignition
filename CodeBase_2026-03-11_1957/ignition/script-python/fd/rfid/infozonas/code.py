class DatosZonaRFID:
	"""Representa los datos de una zona RFID, incluyendo información del molde y su configuración."""

	_nombre_zona = ""
	_path_zona = ""
	_datos_zona = None
	
	def __init__(self, nombre_zona, path_contenedor_udts = "[rfid_tags]Antennas/Molds"):
		"""Inicializa la zona RFID cargando sus datos desde el tag correspondiente."""
		self._nombre_zona = nombre_zona
		self._path_zona = path_contenedor_udts + "/" + nombre_zona
		self._datos_zona = fd.utilidades.tags.GestorTags.leeValorDeUnTag(self._path_zona)
		
	def obtieneIdMolde(self):
		"""Devuelve el identificador del molde en la zona."""
		return self._datos_zona["mold_id"]
		
	def obtieneIdModelo(self):
		"""Devuelve el identificador del modelo del molde en la zona."""
		return self._datos_zona["model_id"]
		
	def obtieneLongitudMolde(self):
		"""Devuelve la longitud del molde en la zona."""
		return self._datos_zona["mold_length"]
		
	def obtieneAnchoMolde(self):
		"""Devuelve el ancho del molde en la zona."""
		return self._datos_zona["mold_width"]
		
	def obtieneNumeroMolde(self):
		"""Devuelve el número identificativo del molde en la zona."""
		return self._datos_zona["mold_number"]
		
	def obtieneNumeroChips(self):
		"""Devuelve el número de chips RFID detectados en la zona."""
		return self._datos_zona["tag_count"]
		
	def obtieneIdViaProduccion(self):
		"""Devuelve el identificador de la vía de producción asociada a la zona."""
		return self._datos_zona["id_via_produccion"]
		
	def obtieneSkuMolde(self):
		"""Devuelve el SKU del molde en la zona."""
		return self._datos_zona["mold_sku"]