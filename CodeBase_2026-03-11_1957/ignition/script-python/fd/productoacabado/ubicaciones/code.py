class EventoDarDeAltaUbicacion:
	
	_ejecutador_named_query = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
	
	_ubicacion = ''
	_almacen = ''
	
	def __init__(self, ubicacion, almacen):
		self._ubicacion = ubicacion
		self._almacen = str(almacen)
	
	def altaNuevaUbicacion(self):
		parametros = self._generaParametrosNuevaUbicacion()
		resultado_alta = self._insertaNuevaUbicacion(parametros)
		return resultado_alta
	
	def _generaParametrosNuevaUbicacion(self):
		codigo_ubicacion = self._generaCodigoUbicacion()
		parametros = {
			'ubicacion': self._ubicacion,
			'almacen': self._almacen,
			'barras': codigo_ubicacion
		}
		return parametros
	
	def _generaCodigoUbicacion(self):
		codigo_ubicacion = self._ubicacion.lower() + 'alm0' + self._almacen
		return codigo_ubicacion
	
	def _insertaNuevaUbicacion(self, parametros):
		creado = self._compruebaSiExisteUbicacion()
		if creado.getRowCount() > 0:
			resultado_insert = 'Ubicación ya existe en almacén seleccionado'
		else:
			query_insertar_nueva_ubicacion = 'FD/ProductoAcabado/InsertaUbicacionNueva' 
			resultado_insert = self._ejecutador_named_query.ejecutaNamedQuery(query_insertar_nueva_ubicacion, parametros)
		return resultado_insert
	
	def _compruebaSiExisteUbicacion(self):
		query_creado = 'FD/ProductoAcabado/YaExisteUbicacion'
		parametros_creado = {
			'ubicacion':self._ubicacion, 
			'almacen':self._almacen
		}
		creado = self._ejecutador_named_query.ejecutaNamedQuery(query_creado, parametros_creado)
		return creado

class EventoObtenerDatosUbicacion:
	
	_ejecutador_named_query = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
	_codigo_ubicacion = ''
	
	def __init__(self, codigo_ubicacion):
		self._codigo_ubicacion = codigo_ubicacion
		
	def obtieneDatosUbicacionPorCodigo(self):
		datos_ubicacion = self._ejecutador_named_query.ejecutaNamedQuery('FD/ProductoAcabado/ObtieneDatosUbicacionPorCodigo', {'codigo_ubicacion': self._codigo_ubicacion})
		return datos_ubicacion
		
		
		
		
		