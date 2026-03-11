class ImpresionListaEtiquetas:
	
	MOLD_ID = 0
	MANUAL_PRINT_REASON = 0
	
	
	def __init__(self, lista_sku, worker_id, printer_id, cliente):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._lista_sku = lista_sku
		self._worker_id = worker_id
		self._printer_id = printer_id
		self._cliente = cliente
		self._bucleRecorreLista()
		
	def _creaShowertrayId(self, color, modelo, dimension):
		return fd.numerosserie.GeneradorNumeroSerie(1, self._cliente, self.MOLD_ID, color, modelo, dimension).obtieneNumeroSerie()
		
	def _obtieneModeloDeSku(self, sku):
		return sku [:3]
		
	def _obtieneIdModeloDeSku(self, sku):
		info_modelo = self._db.ejecutaNamedQuery('FD/Platos/ModeloDeSku', {"sku_name":self._obtieneModeloDeSku(sku)})
		return info_modelo[0]["id"]
		
	def _obtieneDimensionDeSku(self, sku):
		return sku[3:9]
		
	def _obtieneColorDeSku(self, sku):
		return sku[9:13]
		
	def _bucleRecorreLista(self):
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
	
	MOLD_ID = 0
	MANUAL_PRINT_REASON = 0
	
	def __init__(self, lista_sku_qty, worker_id, printer_id, cliente):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto(
			'FactoryDB', 'CodeBase'
		)
		self._lista_sku_qty = lista_sku_qty
		self._worker_id = worker_id
		self._printer_id = printer_id
		self._cliente = cliente
		self._bucleRecorreLista()
		
	def _obtieneModeloDeSku(self, sku):
		return sku[:3]
		
	def _obtieneIdModeloDeSku(self, sku):
		info_modelo = self._db.ejecutaNamedQuery(
			'FD/Platos/ModeloDeSku',
			{"sku_name": self._obtieneModeloDeSku(sku)}
		)
		return info_modelo[0]["id"]
		
	def _obtieneDimensionDeSku(self, sku):
		return sku[3:9]
		
	def _obtieneColorDeSku(self, sku):
		return sku[9:13]
		
	def _imprimeEtiquetaSku(self, sku):
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
		for item in self._lista_sku_qty:
			sku = item["SKU"]
			qty = item["QTY"]
			
			for _ in range(qty):
				self._imprimeEtiquetaSku(sku)