class ConstructorSQL:
	
	TIPO_COLUMNA_FECHA = 1
	TIPO_COLUMNA_NUMERO = 2
	TIPO_COLUMNA_TEXTO = 3
	
	@staticmethod
	def generaStringValoresParaInsertMasivo(dataset_ordenes_produccion, mapeo_columnas_tipo):
		filas_insertar = []
		for row in dataset_ordenes_produccion:
			fila_mapeada = ConstructorSQL._construyeFilaInsertMasivo(row, mapeo_columnas_tipo)
			filas_insertar.append(fila_mapeada)
		return ','.join(filas_insertar)
		
	@staticmethod
	def creaMapeo( nombreColumna, tipo):
		return {"nombreColumna": nombreColumna, "tipo":tipo}
		
	@staticmethod
	def _construyeFilaInsertMasivo( fila_dataset_entrada, mapeo_columnas_tipo):
		fila_insert = map(lambda x: ConstructorSQL._mapeaCampoTipo(fila_dataset_entrada, x), mapeo_columnas_tipo) 
		value_string=", ".join(fila_insert)
		value_string='( '+value_string+' )'
		return value_string
			
	@staticmethod
	def _mapeaCampoTipo(fila_dataset,  mapeo):
		tipo = mapeo["tipo"]
		nombreColumna = mapeo["nombreColumna"]
		if tipo == ConstructorSQL.TIPO_COLUMNA_FECHA:
			return "'"+system.date.format(fila_dataset[nombreColumna], "yyyy-MM-dd HH:mm:ss")+"'" if fila_dataset[nombreColumna] is not None else 'NULL'
		elif tipo == ConstructorSQL.TIPO_COLUMNA_NUMERO:
			return str(fila_dataset[nombreColumna]) if fila_dataset[nombreColumna] is not None else 'NULL'
		elif tipo == ConstructorSQL.TIPO_COLUMNA_TEXTO:
			return "'"+str(fila_dataset[nombreColumna]).replace("'","''")+"'" if fila_dataset[nombreColumna] is not None else 'NULL'
			
			
class EjecutadorNamedQueriesConContexto:
	
	ScriptScope = fd.utilidades.scope.ScriptScope
	_logger = None
	_scope = 0
	_base_datos = "" 
	_proyecto_named_queries = ""
	_numero_reintentos = 0
	
	_transaccion = None
	
	def __init__(self, base_datos, proyecto_named_queries, numero_reintentos = 3):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('EjecutadorNamedQueriesConContexto')
		#self._logger.activaLogDebug()
		self._numero_reintentos = numero_reintentos
		self._scope = self.ScriptScope.getScope()
		self._logger.logDebug(str(self._scope))
		
		self._proyecto_named_queries = proyecto_named_queries
		self._base_datos = base_datos
		
	def iniciaTransaccion(self, isolation_level, timeout):
		if self._scope in [self.ScriptScope.SCOPE_GATEWAY,self.ScriptScope.SCOPE_PERSPECTIVE] :
			self._transaccion = system.db.beginNamedQueryTransaction(project=self._proyecto_named_queries, database=self._base_datos, isolationLevel = isolation_level, timeout = timeout)
		else:
			self._transaccion = system.db.beginNamedQueryTransaction(database=self._base_datos, isolationLevel = isolation_level, timeout = timeout)
	
	def rollbackTransaccion(self):
		system.db.rollbackTransaction(self._transaccion)
		system.db.closeTransaction(self._transaccion)
	
	def commitTransaccion(self):
		system.db.commitTransaction(self._transaccion)
		system.db.closeTransaction(self._transaccion)
		
	def ejecutaNamedQuery(self, path_named_query, params):
		exito = False
		resultado = None
		texto_excepcion = ""
		for i in range(self._numero_reintentos):
			try:
				resultado = self._ejecutaNamedQuerySegunContexto(path_named_query, params)
				exito = True
				break
			except :
				texto_excepcion = str(sys.exc_info())
				self._logger.logWarning("Error ejecutando : " + str(path_named_query) + "con parametros: " + str(params) + "intento numero : " + str(i+1) + "/" + str(self._numero_reintentos) + " - Excepcion: "+str(texto_excepcion))
		
		if not exito:
			raise Exception("No se ha podido ejecutar la consulta por: "+ texto_excepcion)
		
		return resultado
		
	def _ejecutaNamedQuerySegunContexto(self, path_named_query, params):
		if self._scope in [self.ScriptScope.SCOPE_GATEWAY, self.ScriptScope.SCOPE_PERSPECTIVE]:
			return system.db.runNamedQuery(self._proyecto_named_queries, path_named_query, params, tx=self._transaccion)
		else:
			return system.db.runNamedQuery(path_named_query, params, tx=self._transaccion)