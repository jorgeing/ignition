import datetime

class LanzadorOrdenes(object):
	
	PATH_SECUENCIA = '[rfid_tags]ProdOrders/GeneradorOrdenes/ultima_secuencia_digitos'
	PATH_ANYO_EN_CURSO = '[rfid_tags]ProdOrders/GeneradorOrdenes/anyo_en_curso'
	
	def __init__(self):
		self._fecha_actual = system.date.now()
		pass
	
	def generaOrdenesNuevas(self):
		pass
	
	def _generaIdOrden(self):
		prefijo = 'OP'
		anyo = self._compruebaReseteoYObtieneAnyoActual()
		secuencia_digitos = self._generaSecuencia7Digitos()
		id_orden = prefijo + anyo + '_' + secuencia_digitos
		return id_orden
	
	def _compruebaReseteoYObtieneAnyoActual(self):
		anyo_actual = system.date.getYear(self._fecha_actual)
		anyo_en_curso = self._obtieneAnyoEncurso()
		if anyo_actual > anyo_en_curso:
			self._actualizaAnyoEnCurso(anyo_actual)
			self._reseteaSecuencia(anyo_actual)
		anyo_actual_formateado = str(anyo_actual)
		return anyo_actual_formateado
	
	def _actualizaAnyoEnCurso(self, anyo_actual):
		system.tag.writeBlocking(self.PATH_SECUENCIA, 0)
	
	def _reseteaSecuencia(self, anyo_actual):
		system.tag.writeBlocking(self.PATH_ANYO_EN_CURSO, anyo_actual)
	
	def _obtieneAnyoEncurso(self):
		anyo_en_curso = system.tag.readBlocking([self.PATH_ANYO_EN_CURSO])[0].value
		return anyo_en_curso
	
	def _generaSecuencia7Digitos(self):
		ultima_secuencia = self._obtieneUltimaSecuenciaGenerada()
		nueva_secuencia = ultima_secuencia + 1
		self._actualizaUltimaSecuencia(nueva_secuencia)
		nueva_secuencia_formateada = str(nueva_secuencia).zfill(7)
		return nueva_secuencia_formateada
	
	def _obtieneUltimaSecuenciaGenerada(self):
		ultima_secuencia = system.tag.readBlocking([self.PATH_SECUENCIA])[0].value
		return ultima_secuencia
	
	def _actualizaUltimaSecuencia(self, nueva_secuencia):
		system.tag.writeBlocking(self.PATH_SECUENCIA, nueva_secuencia)


class LanzadorOrdenesManual(LanzadorOrdenes):
	
	RUTA_INSERT_ORDEN = 'FD/PlanificacionProduccion/PlanificacionManual/InsertaOrdenNueva'
	RUTA_SELECT_NOMCLI = 'FD/Utilidades/ObtieneNombreCliente'
	RUTA_SELECT_DESC_SKU = 'FD/Utilidades/ObtieneDescripcionSKU'
	
	CODEMP = '01'
	CODPED = 0
	CODSER = 'SC'
	PRODUCTION_LINE = '101'
	CODSERPED = 'A'
	LINPED = 0
	
	_db = None
	
	def __init__(self, sku, id_cliente, unidades, cpsd, mecanismo_creacion= 'MANUAL'):
		super(LanzadorOrdenesManual, self).__init__()
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._sku = sku
		self._id_cliente = id_cliente
		self._unidades = unidades
		self._cpsd = self._formateaCPSDADatetime(cpsd)
		self._mecanismo_creacion = mecanismo_creacion
	
	def _formateaCPSDADatetime(self, cpsd):
		cpsd_datetime = datetime.datetime.strptime(cpsd, "%Y-%m-%d")
		return cpsd_datetime
	
	def generaOrdenesNuevas(self):
		for unidad in range(self._unidades):
			self._insertaOrdenNueva()
	
	def _insertaOrdenNueva(self):
		parametros_nueva_orden = self._obtieneParametrosOrden()
		self._db.ejecutaNamedQuery(self.RUTA_INSERT_ORDEN, parametros_nueva_orden)
	
	def _obtieneParametrosOrden(self):
		parametros_nueva_orden = {
			'codemp': self.CODEMP,
			'pordorder': self._generaIdOrden(),
			'referencia': self._sku,
			'cantidadtotal': 1,
			'unidadesproducidas': 0,
			'pendientes': 1,
			'nomcli': self._obtieneNombreCliente(),
			'codcli': self._id_cliente,
			'codped': self.CODPED,
			'codeje': self._obtieneCodEje(),
			'codser': self.CODSER,
			'description': self._obtieneDescripcionSKU(),
			'archiveid': self._generaArchiveID(),
			'archiverecordid': 1,
			'productionline': self.PRODUCTION_LINE,
			'codserped': self.CODSERPED,
			'linped': self.LINPED,
			'cpsd': self._cpsd,
			'mecanismo_creacion': self._mecanismo_creacion
		}
		return parametros_nueva_orden
	
	def _obtieneNombreCliente(self):
		return self._db.ejecutaNamedQuery(self.RUTA_SELECT_NOMCLI, {'codcli': self._id_cliente})[0][0]
		
	def _obtieneCodEje(self):
		anyo_actual = system.date.getYear(self._fecha_actual)
		return anyo_actual
	
	def _obtieneDescripcionSKU(self):
		return self._db.ejecutaNamedQuery(self.RUTA_SELECT_DESC_SKU, {'sku': self._sku})[0][0]
	
	def _generaArchiveID(self):
		fecha_actual = system.date.format(self._fecha_actual, 'yyyyMMdd')
		return int(fecha_actual)

class LanzadorOrdenesPedidos(LanzadorOrdenes):
	
	RUTA_INSERT_ORDEN = 'FD/PlanificacionProduccion/PlanificacionManual/InsertaOrdenNueva'
	RUTA_SELECT_DESC_SKU = 'FD/Utilidades/ObtieneDescripcionSKU'
	
	CODEMP = '01'
	CODSER = 'SC'
	PRODUCTION_LINE = '101'
	CODSERPED = 'A'
	LINPED = 0
	
	_db = None
	
	def __init__(self, pedidos, molde_marco_corte = None, mecanismo_creacion = 'PEDIDO'):
		super(LanzadorOrdenesPedidos, self).__init__()
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._pedidos = pedidos
		self._molde_marco_corte = molde_marco_corte
		self._mecanismo_creacion = mecanismo_creacion
	
	def generaOrdenesNuevas(self):
		for pedido in self._pedidos:
			for unidad in range(int(pedido['cantidad_pendiente'])):
				self._insertaOrdenNueva(pedido)
	
	def _insertaOrdenNueva(self, pedido):
		parametros_nueva_orden = self._obtieneParametrosOrden(pedido)
		self._db.ejecutaNamedQuery(self.RUTA_INSERT_ORDEN, parametros_nueva_orden)
	
	def _obtieneParametrosOrden(self, pedido):
		parametros_nueva_orden = {
			'codemp': self.CODEMP,
			'pordorder': self._generaIdOrden(),
			'referencia': self._compruebaSemiProductoYObtieneSKU(pedido),
			'cantidadtotal': 1,
			'unidadesproducidas': 0,
			'pendientes': 1,
			'nomcli': pedido['NomCli'],
			'codcli': pedido['CodCli'],
			'codped': pedido['codped'],
			'codeje': self._obtieneCodEje(),
			'codser': self.CODSER,
			'description': self._obtieneDescripcionSKU(pedido),
			'archiveid': self._generaArchiveID(),
			'archiverecordid': 1,
			'productionline': self.PRODUCTION_LINE,
			'codserped': self.CODSERPED,
			'linped': self.LINPED,
			'cpsd': pedido['CPSD'],
			'mecanismo_creacion': self._mecanismo_creacion
		}
		return parametros_nueva_orden
	
	def _compruebaSemiProductoYObtieneSKU(self, pedido):
		sku_pedido = pedido['CodArt']
		sku_orden = None
		if fd.sku.ManejadorSku(sku_pedido).esSkuCorte():
			sku_orden = fd.sku.ConversorSKUCorte(sku_pedido, self._molde_marco_corte).convierteASkuSemiProducto()
		elif fd.sku.ManejadorSku(sku_pedido).esSkuDekor():
			sku_orden = fd.sku.ConversorSKUDekor(sku_pedido).convierteASkuSemiProducto()
		else:
			sku_orden = sku_pedido
		return sku_orden
	
	def _obtieneCodEje(self):
		anyo_actual = system.date.getYear(self._fecha_actual)
		return anyo_actual
	
	def _obtieneDescripcionSKU(self, pedido):
		return self._db.ejecutaNamedQuery(self.RUTA_SELECT_DESC_SKU, {'sku': pedido['CodArt']})[0][0]
	
	def _generaArchiveID(self):
		fecha_actual = system.date.format(self._fecha_actual, 'yyyyMMdd')
		return int(fecha_actual)
	
	