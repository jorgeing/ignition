class ActualizaTablaScrapRFID:
	_logger = None
	_transaccion = ""
	_consultaScada = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
	_consultaClavei = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('ClaveiDB','CodeBase')
	_datos_scrap_nuevo = []
	_parametros_insertar = ""
	_id_platos_actualizar = ""
	
	def __init__(self):
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("ActualizaTablaScrapRFID")
		self._logger.activaLogDebug()
		
	def insertaNuevoScrap(self):
		try:
			self._iniciaTransaccionScada()
			self._logger.logDebug("Iniciando insercion nuevo scrap")
			
			self._obtieneInfoScrapNuevo()
			self._obtieneParametrosAInsertarYPlatosAActualizar()
			self._insertaScrapEnClavei()
			self._actualizaPlatosEnScada()
			
			self._commitTransaccionScada()
		except Exception as e:
			self._logger.logError("Error actualizando scrap: "+ str(e))
			self._rollbackTransaccionScada()
			raise Exception("Error actualizando scrap: "+ str(e))
		
	def _iniciaTransaccionScada(self):
		self._transaccion = self._consultaScada.iniciaTransaccion(isolation_level = system.db.SERIALIZABLE, timeout = 60000)
		
	def _commitTransaccionScada(self):
		self._consultaScada.commitTransaccion()
		
	def _rollbackTransaccionScada(self):
		self._consultaScada.rollbackTransaccion()
	
	def _obtieneInfoScrapNuevo(self):
		datos_scrap_nuevo = self._consultaScada.ejecutaNamedQuery('FD/Clavei/ObtieneInfoScrapNuevo', {})
		datos_scrap_nuevo_formateados = system.dataset.toPyDataSet(datos_scrap_nuevo)
		self._datos_scrap_nuevo =  datos_scrap_nuevo_formateados
	
	def _obtieneParametrosAInsertarYPlatosAActualizar(self):
		valores_insertados, id_platos_insertados = self._construyeListadoParametrosYListadoIdPlatos()
		valores_insertados_formateados = ','.join(valores_insertados)
		parametros_insertar = {'values': valores_insertados_formateados}
		id_platos_actualizar = '('+','.join(id_platos_insertados)+')'
		self._parametros_insertar =  parametros_insertar
		self._id_platos_actualizar = id_platos_actualizar
	
	def _construyeListadoParametrosYListadoIdPlatos(self):
		valores_insertados = []
		id_platos_insertados = []
		for fila in self._datos_scrap_nuevo:
			lista_valores = self._construyeListaValoresInsertar(fila)
			string_valores = ", ".join(lista_valores)
			string_valores = '( '+string_valores+' )'
			valores_insertados.append(string_valores)
			id_platos_insertados.append("'"+fila['showertray_uuid']+"'")
		return valores_insertados, id_platos_insertados
	
	def _construyeListaValoresInsertar(self, fila):
		lista_valores = [ "'"+str(fila['CodEmp'])+"'", 
								"'scrap-instance-showertray'",
								"'"+system.date.format(fila['timestamp'], "dd-MM-yyyy HH:mm:ss")+"'",
								"'"+str(fila['productref'])+"'",
								"'"+str(fila['showertray_uuid'])+"'", 
								"'"+str(fila['mold_uuid'])+"'",
								"'"+str(fila['client_code'])+"'",
								"'false'",
								'1',
								"'"+str(fila['scada_scrap_reason_id'])+"'",
								"'"+str(fila['clavei_scrap_reason_id'])+"'",
								"'"+str(fila['scrap_reason_desc'])+"'"]
		return lista_valores
	
	def _insertaScrapEnClavei(self):
		if self._parametros_insertar['values']:
			    self._consultaClavei.ejecutaNamedQuery('FD/Clavei/InsertaScrapNuevo', self._parametros_insertar)
	
	def _actualizaPlatosEnScada(self):
		if self._parametros_insertar['values']:
			parametros_actualizar = {'rango': self._id_platos_actualizar}
			self._consultaScada.ejecutaNamedQuery('FD/Clavei/ActualizaPlatosInsertadosScrap', parametros_actualizar)
		
		