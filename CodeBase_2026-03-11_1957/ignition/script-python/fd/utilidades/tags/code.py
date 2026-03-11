from fd.excepciones import *
from fd.utilidades.logger import *

class GestorTags:
	_loggerBase = LoggerBase("GestorTags")
	
	@staticmethod
	def escribeTagsConReintento(paths, valores, reintentos=5):
		intento = 0
		reintentar = True
		while intento<reintentos and reintentar==True:
			intento = intento + 1
			result = system.tag.writeBlocking(paths, valores)
			reintentar = False
			for r in result:
				if r.isBadOrError():
					reintentar=True
		if intento==reintentos and reintentar==True:
			raise IOError("Error escribiendo tag: " + str(paths))
			
	@staticmethod
	def leeValorDeUnTag(path):
		qualifiedVal = system.tag.readBlocking(path)[0]
		calidad_lectura = qualifiedVal.getQuality()
		if calidad_lectura.isNotGood():
			raise ErrorLecturaTagException(calidad_lectura.getDiagnosticMessage())
		
		return qualifiedVal.value
		


class TagBuffer:
	
	def __init__(self, path, longitud_lista=4):
		self._path = path
		self._longitud_lista = longitud_lista
		self._buffer = self._cargaBufferDelTag(path)
		
	
	def agregaTag(self, tag_id):
		if tag_id in self._buffer:
			return False
		else:
			self._eliminaPrimeroDeLaLista()
			self._buffer.append(tag_id)
			self._guardaComoJson()
			return True
		
	def existeEnLista(self, tag_id):
		return tag_id in self._buffer
		
	def devuelveLista(self):
		return list(self._buffer)
		
	def _cargaBufferDelTag(self, path):
		try:
			buffer_tag = GestorTags.leeValorDeUnTag(path)
			buffer_data = system.util.jsonDecode(buffer_tag)
			if buffer_data:
				return buffer_data
			else:
				return []
		except:
			return []
		
	def _guardaComoJson(self):
		json = system.util.jsonEncode(self._buffer)
		GestorTags.escribeTagsConReintento(self._path, json)
		
	def _eliminaPrimeroDeLaLista(self):
		if len(self._buffer) >= self._longitud_lista:
			self._buffer.pop(0)