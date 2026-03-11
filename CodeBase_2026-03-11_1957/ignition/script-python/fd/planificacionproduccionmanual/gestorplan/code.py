from collections import OrderedDict

class GestorPlanificacion:
	
	def __init__(self):
		self._logger = system.util.getLogger('AgrupacionPlanificacion')
		self.COLUMN_INICIO= "inicioestimado"
		self.COLUMN_TOTAL = "cantidadtotal"
		self.COLUMN_PRODUCIDAS = "unidadesproducidas"
		self.COLUMN_PENDIENTES = "pendientes"
		self.COLUMN_REFERENCIA = "referencia"
		self.COLUMN_MOLDE = "description"
		self.COLUMN_COLOR = "color_id"
		self.COLUMN_PORCENTAJE = "completado"
		self.COLUMN_NOMBRE_COLOR = "nombre_color"
		
	def agruparPorTurno(self, dataset):
		if self._estaVacio(dataset):
			return dataset
		
		grupos = self._agruparFilas(dataset, 'turno')
		return self._construirDatasetAgregado(grupos, self.COLUMN_INICIO)
	
	def agruparPorDia(self, dataset):
		if self._estaVacio(dataset):
			return dataset
		
		grupos = self._agruparFilas(dataset, 'dia')
		return self._construirDatasetAgregado(grupos, self.COLUMN_INICIO)
	
	def agruparPorSkuEnTurno(self, dataset, turno, color = None):
		if self._estaVacio(dataset):
			return dataset
		
		dataset_filtrado = self._filtrarPorTurnoYColor(dataset, turno, color)
		if self._estaVacio(dataset_filtrado):
			return dataset_filtrado
		
		grupos = self._agruparFilas(dataset_filtrado, 'sku')
		return self._construirDatasetAgregado(grupos, self.COLUMN_REFERENCIA)
	
	def agruparPorMoldeEnTurno(self, dataset, turno, color = None):
		if self._estaVacio(dataset):
			return dataset
		
		dataset_filtrado = self._filtrarPorTurnoYColor(dataset, turno, color)
		if self._estaVacio(dataset_filtrado):
			return dataset_filtrado
		
		grupos = self._agruparFilas(dataset_filtrado, 'molde')
		return self._construirDatasetAgregado(grupos, self.COLUMN_REFERENCIA)
	
	def agruparPorColorEnTurno(self, dataset, turno, color=None):
		if self._estaVacio(dataset):
			return dataset
		
		dataset_filtrado = self._filtrarPorTurnoYColor(dataset, turno, color)
		if self._estaVacio(dataset_filtrado):
			return dataset_filtrado
		
		grupos = self._agruparFilas(dataset_filtrado, 'color')
		return self._construirDatasetAgregado(grupos, self.COLUMN_COLOR, self.COLUMN_NOMBRE_COLOR)
	
	def _estaVacio(self, dataset):
		return dataset is None or dataset.rowCount == 0
	
	def _agruparFilas(self, dataset, tipo_agrupacion):
		grupos = OrderedDict()
		pyData = system.dataset.toPyDataSet(dataset)
		
		for fila in pyData:
			clave = self._obtieneClaveSegunAgrupacion(fila, tipo_agrupacion)
		
			if clave not in grupos:
				grupos[clave] = self._crearAcumuladorVacio()
			
				if tipo_agrupacion == 'color':
						grupos[clave][self.COLUMN_NOMBRE_COLOR] = fila[self.COLUMN_NOMBRE_COLOR]
			
			self._acumularFilaEnGrupo(grupos[clave], fila)
		
		return grupos
	
	
	def _obtieneClaveSegunAgrupacion(self, fila, tipo_agrupacion):
		clave = None
		if tipo_agrupacion == 'turno':
			clave = fila[self.COLUMN_INICIO]
		elif tipo_agrupacion == 'dia':
			clave = fila[self.COLUMN_INICIO]
			clave = system.date.format(clave, 'yyyy-MM-dd')
		elif tipo_agrupacion == 'sku':
			clave = fila[self.COLUMN_REFERENCIA]
		elif tipo_agrupacion == 'molde':
			clave = fila[self.COLUMN_MOLDE]
		elif tipo_agrupacion ==  'color':
			clave = fila[self.COLUMN_COLOR]
		return clave
	
	
	def _crearAcumuladorVacio(self):
		return {
			self.COLUMN_TOTAL:      0.0,
			self.COLUMN_PRODUCIDAS: 0.0,
			self.COLUMN_PENDIENTES: 0.0
		}
	
	
	def _acumularFilaEnGrupo(self, grupo, fila):
		grupo[self.COLUMN_TOTAL]      += float(fila[self.COLUMN_TOTAL])
		grupo[self.COLUMN_PRODUCIDAS] += float(fila[self.COLUMN_PRODUCIDAS])
		grupo[self.COLUMN_PENDIENTES] += float(fila[self.COLUMN_PENDIENTES])
	
	
	def _construirDatasetAgregado(self, grupos, nombre_columna_clave, nombre_columna_secundaria=None):
		columnas = [nombre_columna_clave]
		
		if nombre_columna_secundaria:
			columnas.append(nombre_columna_secundaria)
		
		columnas.extend([
			self.COLUMN_TOTAL,
			self.COLUMN_PRODUCIDAS,
			self.COLUMN_PENDIENTES,
			self.COLUMN_PORCENTAJE
		])
		
		filas = []
		
		for clave, totales in grupos.items():
			total      = totales[self.COLUMN_TOTAL]
			producidas = totales[self.COLUMN_PRODUCIDAS]
			pendientes = totales[self.COLUMN_PENDIENTES]
			
			porcentaje = self._calcularPorcentajeCompletado(producidas, total)
			
			fila = [clave]
			if nombre_columna_secundaria:
				fila.append(totales[nombre_columna_secundaria])
			
			fila.extend([
				total,
				producidas,
				pendientes,
				porcentaje
			])
			
			filas.append(fila)
		
		return system.dataset.toDataSet(columnas, filas)
	
	def _calcularPorcentajeCompletado(self, unidadesProducidas, cantidadTotal):
		if cantidadTotal == 0:
			return 0.0
		return (float(unidadesProducidas) / float(cantidadTotal)) * 100.0
	
	def _filtrarPorTurnoYColor(self, dataset, turno, color):
		pyData = system.dataset.toPyDataSet(dataset)
		
		columnas = list(dataset.getColumnNames())
		filas_filtradas = []
		for fila in pyData:
			if system.date.toMillis(fila[self.COLUMN_INICIO]) != system.date.toMillis(turno):
				continue

			if color:
				if fila[self.COLUMN_COLOR] != str(color):
					continue

			fila_nueva = [fila[nombre_columna] for nombre_columna in columnas]
			filas_filtradas.append(fila_nueva)
		
		return system.dataset.toDataSet(columnas, filas_filtradas)
		