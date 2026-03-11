class EstadisticasViaPintura:
	
	_id_linea=0
	_cola_platos=[]
	
	def __init__(self,id_linea):
		self._id_linea = id_linea
	
	def calculaPorcentajeOcupacionViaPintura(self):
		cola_filtrada = self.obtieneColaPlatosEnVia()
		total= self.calculaLongitudPlatosEnCola(cola_filtrada)
		long_via = self.obtieneLongitudVia()
		return (total/long_via)*100
		
	def obtieneColaPlatosEnVia(self):
		cola = system.dataset.toPyDataSet(fd.utilidades.tags.GestorTags.leeValorDeUnTag('[production_statistics]WIP/AwaitPourTable'))
		cola_filtrada = []
		for plato in cola:
			if plato["paint_dry_line_id"]==self._id_linea:
				cola_filtrada.append(plato)
		return cola_filtrada
		
	def obtieneNumeroPlatosEnVia(self):
		cola = system.dataset.toPyDataSet(fd.utilidades.tags.GestorTags.leeValorDeUnTag('[production_statistics]WIP/AwaitPourTable'))
		cola_filtrada = []
		for plato in cola:
			if plato["paint_dry_line_id"]==self._id_linea:
				cola_filtrada.append(plato)
		return len(cola_filtrada)
		
	def calculaLongitudPlatosEnCola(self, cola):
		distancia_promedio = self.obtieneDistanciaPromedioEntrePlatos()
		total = 0
		for plato in cola:
			ancho_m=fd.sku.ManejadorSku(plato["sku"]).obtieneAncho()/100.0
			total = total + (ancho_m + distancia_promedio)
		return total
		
	def obtieneLongitudVia(self):
		
		if self._id_linea == 1:
			return 33.5
		else:
			return 37
			
	def obtieneDistanciaPromedioEntrePlatos(self):
		return 0.3