class ImpresionListaEtiquetas:
	"""Gestiona la impresión de etiquetas a partir de una lista de SKUs."""
	
	MOLD_ID = 0
	MANUAL_PRINT_REASON = 0
	
	
	def __init__(self, lista_sku, worker_id, printer_id, cliente):
		"""Inicializa e inicia el bucle de impresión."""
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._lista_sku = lista_sku
		self._worker_id = worker_id
		self._printer_id = printer_id
		self._cliente = cliente
		self._bucleRecorreLista()
		
	def _creaShowertrayId(self, color, modelo, dimension):
		"""Genera un número de serie para el plato."""
		return fd.numerosserie.GeneradorNumeroSerie(1, self._cliente, self.MOLD_ID, color, modelo, dimension).obtieneNumeroSerie()
		
	def _obtieneModeloDeSku(self, sku):
		"""Extrae los 3 primeros caracteres del SKU como modelo."""
		return sku [:3]
		
	def _obtieneIdModeloDeSku(self, sku):
		"""Obtiene el ID del modelo consultando la BD."""
		info_modelo = self._db.ejecutaNamedQuery('FD/Platos/ModeloDeSku', {"sku_name":self._obtieneModeloDeSku(sku)})
		return info_modelo[0]["id"]
		
	def _obtieneDimensionDeSku(self, sku):
		"""Extrae los caracteres de dimensión del SKU."""
		return sku[3:9]
		
	def _obtieneColorDeSku(self, sku):
		"""Extrae los caracteres de color del SKU."""
		return sku[9:13]
		
	def _bucleRecorreLista(self):
		"""Recorre la lista de SKUs y crea e imprime etiquetas para cada uno."""
		for sku in self._lista_sku:
			color = self._obtieneColorDeSku(sku)
			modelo = self._obtieneIdModeloDeSku(sku)
			dimension = self._obtieneDimensionDeSku(sku)
			
			gestor_creacion_plato = fd.platos.EventoCreacionPlato()
			gestor_creacion_plato.creaPlatoDeSku(sku, self._cliente)
			showertray_id = gestor_creacion_plato.obtieneNumeroSerie()
			
			gestor_envasado = fd.platos.EventoEmpaquetadoPlato(self.MANUAL_PRINT_REASON, self._printer_id, self._worker_id, -1)
			gestor_envasado.empaquetarPlato(showertray_id, 0, 0, self._cliente)

class ImpresionListaEtiquetasConCantidad:
	"""Gestiona la impresión de etiquetas con cantidad especificada por SKU."""
	
	MOLD_ID = 0
	MANUAL_PRINT_REASON = 0
	
	def __init__(self, lista_sku_qty, worker_id, printer_id, cliente):
		"""Inicializa e inicia el bucle de impresión."""
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto(
			'FactoryDB', 'CodeBase'
		)
		self._lista_sku_qty = lista_sku_qty
		self._worker_id = worker_id
		self._printer_id = printer_id
		self._cliente = cliente
		self._bucleRecorreLista()
		
	def _obtieneModeloDeSku(self, sku):
		"""Extrae los 3 primeros caracteres del SKU como modelo."""
		return sku[:3]
		
	def _obtieneIdModeloDeSku(self, sku):
		"""Obtiene el ID del modelo consultando la BD."""
		info_modelo = self._db.ejecutaNamedQuery(
			'FD/Platos/ModeloDeSku',
			{"sku_name": self._obtieneModeloDeSku(sku)}
		)
		return info_modelo[0]["id"]
		
	def _obtieneDimensionDeSku(self, sku):
		"""Extrae los caracteres de dimensión del SKU."""
		return sku[3:9]
		
	def _obtieneColorDeSku(self, sku):
		"""Extrae los caracteres de color del SKU."""
		return sku[9:13]
		
	def _imprimeEtiquetaSku(self, sku):
		"""Crea un plato a partir del SKU e imprime su etiqueta."""
		gestor_creacion_plato = fd.platos.EventoCreacionPlato()
		gestor_creacion_plato.creaPlatoDeSku(sku, self._cliente)
		showertray_id = gestor_creacion_plato.obtieneNumeroSerie()
		
		gestor_envasado = fd.platos.EventoEmpaquetadoPlato(
			self.MANUAL_PRINT_REASON,
			self._printer_id,
			self._worker_id,
			-1
		)
		gestor_envasado.empaquetarPlato(
			showertray_id, 0, 0, self._cliente
		)
		
	def _bucleRecorreLista(self):
		"""Recorre la lista de pares SKU/cantidad e imprime cada uno."""
		for item in self._lista_sku_qty:
			sku = item["SKU"]
			qty = item["QTY"]
			
			for _ in range(qty):
				self._imprimeEtiquetaSku(sku)