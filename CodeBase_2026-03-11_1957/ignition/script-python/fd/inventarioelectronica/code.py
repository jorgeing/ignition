
class GestorInventarioElectronica:
	ALMACENES = ['automatizacion', 'mecanicos']
	RUTA_ACTUALIZA_STOCK = 'FD/InventarioElectronica/ActualizaStock'
	RUTA_INSERTA_MOVIMIENTO = 'FD/InventarioElectronica/InsertaMovimiento'
	RUTA_INSERTA_ARTICULO = 'FD/InventarioElectronica/InsertaArticulo'
	RUTA_ELIMINA_ARTICULO = 'FD/InventarioElectronica/EliminaArticulo'
	RUTA_ACTUALIZA_ARTICULO = 'FD/InventarioElectronica/ActualizaArticulo'
	
	def __init__(self):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('GestorInventarioElectronica')
		self._ejecutadorNamedQueries = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
	
	def registraMovimiento(self, referencia, cantidad, tipo_movimiento, usuario, almacen_origen, almacen_destino):
		if tipo_movimiento == 'reposicion':
			self._registraReposicion(referencia, cantidad, tipo_movimiento, usuario, almacen_origen)
		elif tipo_movimiento == 'consumo':
			self._registraConsumo(referencia, cantidad, tipo_movimiento, usuario, almacen_origen)
		else:
			self._registraTransferencia(referencia, cantidad, tipo_movimiento, usuario, almacen_origen, almacen_destino)
	
	def registraArticulo(self, referencia, descripcion, categoria, caja):
		for almacen in self.ALMACENES:
			parametros = {
				'referencia': referencia,
				'descripcion': descripcion,
				'categoria': categoria,
				'caja': caja,
				'almacen': almacen
			}
			self._ejecutadorNamedQueries.ejecutaNamedQuery(self.RUTA_INSERTA_ARTICULO, parametros)
	
	def eliminaArticulo(self, referencia):
		parametros = {
			'referencia': referencia
		}
		self._ejecutadorNamedQueries.ejecutaNamedQuery(self.RUTA_ELIMINA_ARTICULO, parametros)
	
	def actualizaArticulo(self, referencia, descripcion, categoria, caja):
		parametros = {
			'referencia': referencia,
			'descripcion': descripcion,
			'categoria': categoria,
			'caja': caja
		}
		self._ejecutadorNamedQueries.ejecutaNamedQuery(self.RUTA_ACTUALIZA_ARTICULO, parametros)
	
	def _formateaSignoCantidad(self, cantidad, tipo_movimiento):
		return -int(cantidad)
	
	def _actualizaCantidadStock(self, referencia, cantidad, almacen):
		parametros = {
			'referencia': referencia,
			'cantidad': cantidad,
			'almacen': almacen
		}
		self._ejecutadorNamedQueries.ejecutaNamedQuery(self.RUTA_ACTUALIZA_STOCK, parametros)
	
	def _insertaMovimientoEnHistorico(self, referencia, cantidad, tipo_movimiento, usuario, almacen):
		parametros = {
			'referencia': referencia,
			'cantidad': cantidad,
			'tipo_movimiento': tipo_movimiento,
			'usuario': usuario,
			'almacen': almacen
		}
		self._logger.logInfo('Parametros inserción movimiento: ' + str(parametros))
		self._ejecutadorNamedQueries.ejecutaNamedQuery(self.RUTA_INSERTA_MOVIMIENTO, parametros)
	
	def _registraReposicion(self, referencia, cantidad, tipo_movimiento, usuario, almacen):
		self._actualizaCantidadStock(referencia, cantidad, almacen)
		self._insertaMovimientoEnHistorico(referencia, cantidad, tipo_movimiento, usuario, almacen)
	
	def _registraConsumo(self, referencia, cantidad, tipo_movimiento, usuario, almacen):
		cantidad = self._formateaSignoCantidad(cantidad, tipo_movimiento)
		self._actualizaCantidadStock(referencia, cantidad, almacen)
		self._insertaMovimientoEnHistorico(referencia, cantidad, tipo_movimiento, usuario, almacen)
	
	def _registraTransferencia(self, referencia, cantidad, tipo_movimiento, usuario, almacen_origen, almacen_destino):
		self._registraConsumo(referencia, cantidad, tipo_movimiento, usuario, almacen_origen)
		self._registraReposicion(referencia, cantidad, tipo_movimiento, usuario, almacen_destino)
	