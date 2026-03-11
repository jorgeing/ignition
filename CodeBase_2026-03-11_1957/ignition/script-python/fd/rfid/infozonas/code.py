class DatosZonaRFID:
	
	_nombre_zona = ""
	_path_zona = ""
	_datos_zona = None
	
	def __init__(self, nombre_zona, path_contenedor_udts = "[rfid_tags]Antennas/Molds"):
		self._nombre_zona = nombre_zona
		self._path_zona = path_contenedor_udts + "/" + nombre_zona
		self._datos_zona = fd.utilidades.tags.GestorTags.leeValorDeUnTag(self._path_zona)
		
	def obtieneIdMolde(self):
		return self._datos_zona["mold_id"]
		
	def obtieneIdModelo(self):
		return self._datos_zona["model_id"]
		
	def obtieneLongitudMolde(self):
		return self._datos_zona["mold_length"]
		
	def obtieneAnchoMolde(self):
		return self._datos_zona["mold_width"]
		
	def obtieneNumeroMolde(self):
		return self._datos_zona["mold_number"]
		
	def obtieneNumeroChips(self):
		return self._datos_zona["tag_count"]
		
	def obtieneIdViaProduccion(self):
		return self._datos_zona["id_via_produccion"]
		
	def obtieneSkuMolde(self):
		return self._datos_zona["mold_sku"]