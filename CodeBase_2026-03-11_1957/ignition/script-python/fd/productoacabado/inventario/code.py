class BaseAltaInventario:
	_logger = None
	_fecha_inventario = None
	_usuario = None
	_almacen = None
	_ubicacion = None
	_consulta = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
	
	def __init__(self, fecha_inventario, usuario, almacen, ubicacion):
		self._fecha_inventario = fecha_inventario
		self._usuario = usuario
		self._almacen = almacen
		self._ubicacion = ubicacion


class GeneradorAltaInventario(BaseAltaInventario):
	
	def registraAlta(self,numero_serie):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("GeneradorAltaInventario")
		self._logger.activaLogDebug()
		
		existe_numero_serie = self._compruebaSiExisteNumeroSerie(numero_serie)
		if existe_numero_serie:
			resultado_alta = 'existe'
			sku_plato_registrado = self._obtieneSKURegistrado(numero_serie)
		else:
			resultado_alta, sku_plato_registrado = self._insertaPlatoEnInventarioYObtieneSKU(numero_serie)
		return resultado_alta, sku_plato_registrado
	
	def _compruebaSiExisteNumeroSerie(self, numero_serie):
		parametros = {'numero_serie': numero_serie, 'fecha_inventario': self._fecha_inventario}
		datos_plato_registrado = self._consulta.ejecutaNamedQuery('FD/ProductoAcabado/CompruebaSiExisteNumeroSerie', parametros)
		if datos_plato_registrado.getRowCount() > 0:
			existe_numero_serie = True
		else:
			existe_numero_serie = False
		return existe_numero_serie
		
	def _obtieneSKURegistrado(self, numero_serie):
		info_plato = fd.platos.PlatoDucha(numero_serie).obtieneInfoScada()
		sku_plato = info_plato['sku']
		return sku_plato
	
	def _insertaPlatoEnInventarioYObtieneSKU(self, numero_serie):
		timestamp = system.date.now()
		sku_plato_registrado = None
		parametros = {'numero_serie':numero_serie, 'usuario':self._usuario, 't_stamp':timestamp, 'fecha_inventario':self._fecha_inventario, 'almacen':self._almacen, 'ubicacion': self._ubicacion}
		try:
			sku_plato_registrado = self._consulta.ejecutaNamedQuery('FD/ProductoAcabado/AltaInventario',parametros)
			if sku_plato_registrado:
				resultado_alta = 'correcto'
			else:
				self._logger.logError('Error al obtener sku del plato: ' + str(numero_serie))
				resultado_alta = 'error'
		except Exception as e:
			self._logger.logError('Error al registar plato: ' + str(e))
			resultado_alta = 'error'
		return resultado_alta, sku_plato_registrado
	

class ConsultadorAltasInventario(BaseAltaInventario):
	
	def cuentaAltasTotalesInventario(self):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("ConsultadorAltasInventario")
		self._logger.activaLogDebug()
	
		parametros = {'fecha_inventario':self._fecha_inventario, 'almacen':self._almacen}
		try:
			cuenta_altas = self._consulta.ejecutaNamedQuery('FD/ProductoAcabado/CuentaAltasInventarioPorFechaAlmacen',parametros)
		except Exception as e:
			self._logger.logError('Error al contar altas totales: ' + str(e))
			cuenta_altas = -1
		return cuenta_altas
		
	def cuentaAltasTotalesInventarioPorUsuario(self):
		parametros = {'usuario':self._usuario, 'fecha_inventario':self._fecha_inventario, 'almacen':self._almacen}
		try:
			cuenta_altas = self._consulta.ejecutaNamedQuery('FD/ProductoAcabado/CuentaAltasInventarioPorFechaAlmacenYUsuario',parametros)
		except Exception as e:
			self._logger.logError('Error al contar altas por usuario: ' + str(e))
			cuenta_altas = -1
		return cuenta_altas
		
	def cuentaAltasTotalesInventarioPorUbicacion(self):
		parametros = {'usuario':self._usuario, 'fecha_inventario':self._fecha_inventario, 'almacen':self._almacen, 'ubicacion': self._ubicacion}
		try:
			cuenta_altas = self._consulta.ejecutaNamedQuery('FD/ProductoAcabado/CuentaAltasInventarioPorFechaUbicacion',parametros)
		except Exception as e:
			self._logger.logError('Error al contar altas por ubicacion: ' + str(e))
			cuenta_altas = -1
		return cuenta_altas
		
		
		