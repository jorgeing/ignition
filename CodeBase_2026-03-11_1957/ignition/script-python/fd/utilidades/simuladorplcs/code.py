class GeneradorTextoCsvSimuladorPLCOmron:

	def __init__(self, lineas_texto_generado_omron):
		self._lineas_texto_generado_omron = lineas_texto_generado_omron
		self._texto_transformado = ""

	def obtieneTextoTransformado(self):
		return self._texto_transformado

	def _transformaTextoOmronASimuladorPLC(self):
		lineas_sin_encabezado = self._obtenerLineasSinEncabezado(self._lineas_texto_generado_omron)

		for linea in lineas_sin_encabezado:
			self._transformaLineaYConcatenaATextoTransformado(linea)

	def _obtenerLineasSinEncabezado(self, lineas):
		return lineas[1:]

	def _transformaLineaYConcatenaATextoTransformado(self, linea):
		columnas = self._separaLineasEnColumnas(linea)
		if self._lineaSeparadaEnColumnasEsValida(columnas):
			linea_formateada = self._transformaYFormateaColumnas(columnas)
			self._texto_transformado = self._texto_transformado + linea_formateada

	def _separaLineasEnColumnas(self, linea):
		return linea.split('\t')

	def _transformaYFormateaColumnas(self, columnas):
		nombre = self._obtieneNombreDeColumnas(columnas)
		tipo_dato_omron = self._obtieneTipoDatoDeColumnas(columnas)
		tipo_dato_mapeado_simulador = self._mapearTipoDatoOmronASimulador(tipo_dato_omron)
		valor = self._obtenerValorPorDefectoSegunTipo(tipo_dato_mapeado_simulador)
		return self._formateaLineaSimuladorPLC(nombre, valor, tipo_dato_mapeado_simulador)

	def _formateaLineaSimuladorPLC(self, nombre, valor, tipo_dato_mapeado_simulador):
		return '"0","{}","{}","{}\n'.format(nombre, valor, tipo_dato_mapeado_simulador)

	def _obtieneNombreDeColumnas(self, columnas):
		return columnas[1].strip()

	def _obtieneTipoDatoDeColumnas(self, columnas):
		return columnas[2].strip()

	def _lineaSeparadaEnColumnasEsValida(self, columnas):
		return len(columnas) >= 4

	def _mapearTipoDatoOmronASimulador(self, datatype):
		datatype = datatype.upper()
		if datatype.startswith("STRING"):
			return "string"
		elif datatype.startswith("BOOL"):
			return "boolean"
		elif datatype == "LREAL" or datatype == "REAL":
			return "double"
		elif datatype == "INT":
			return "int32"
		elif datatype == "DINT":
			return "int32"
		elif datatype == "UINT":
			return "uint32"
		elif datatype == "TIME":
			return "int64"
		elif datatype == "DWORD":
			return "uint32"
		elif datatype == "WORD":
			return "uint16"
		elif datatype == "BYTE":
			return "uint16"
		elif datatype == "LWORD":
			return "uint64"
		else:
			return "string"

	def _obtenerValorPorDefectoSegunTipo(self, mapped_datatype):
		if mapped_datatype == "string":
			return ''
		elif mapped_datatype == "boolean":
			return "False"
		elif mapped_datatype in ["double", "float"]:
			return "0.0"
		elif mapped_datatype in ["int16", "uint16", "int32", "uint32", "int64"]:
			return "0"
		elif mapped_datatype == "datetime":
			return '0'
		else:
			return ''
