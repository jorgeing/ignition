class ExportadorExcel:
	
	_data = None
	_nombre_archivo = ""
	
	def __init__(self, nombre_base, dataset):
		self._nombre_archivo = self._construyeNombreArchivo(nombre_base)
		self._data = system.dataset.toExcel(True, [dataset])
		
	def descargaDesdePerspective(self):
		system.perspective.download(self._nombre_archivo, self._data)
		
	def obtieneArrayBytes(self):
		return self._data
		
	def guardaEnRuta(self, path_directorio_destino):
		filepath = path_directorio_destino +'/'+self._nombre_archivo
		system.file.writeFile(filepath, self._data)
		
	def _obtieneSufijoFecha(self):
		return system.date.format(system.date.now(),'yyyy-MM-dd')
		
	def _construyeNombreArchivo(self, nombre_base):
		sufijo_fecha = self._obtieneSufijoFecha()
		return nombre_base+'_'+sufijo_fecha+'.xlsx'