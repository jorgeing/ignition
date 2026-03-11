from fd.utilidades.logger import *
from fd.utilidades.sql import *
from fd.utilidades.dataset import *

class GestorOrdenesProduccion:
		
	_gestorEliminarOrdenesProduccion = None
	_gestorCrearOrdenesProduccion = None
	_gestorActualizarOrdenesProduccion = None
	_gestorObtenerOrdenesProduccion = None
	_db = None
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._gestorEliminarOrdenesProduccion = GestorEliminarOrdenesProduccion()
		
	def eliminaOrden(self, prod_ord):
		self._gestorEliminarOrdenesProduccion.eliminaOrdenProduccion(prod_ord)
		
	def obtenerOrdenProduccion(self, prod_ord):
		raise NotImplementedError()
		
	@staticmethod
	def obtieneOrdenProduccion(showertray_id):
		ordenes_produccion = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase').ejecutaNamedQuery('FD/OrdenesProduccionScada/ObtieneOrdenProduccionDeShowertray', {"showertray_id": showertray_id})
		if ordenes_produccion.getRowCount != 0:
			return ordenes_produccion

class GestorEliminarOrdenesProduccion:
	_loggerBase = LoggerBase("GestorEliminarOrdenesProduccion")
	_db = None
	
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def eliminaOrdenProduccion(self, prod_ord):
		try:
			params_necesarios = self._obtieneDatosDeTabla(prod_ord)
			params_para_eliminar_orden = self._generaParametrosParaEliminarOrden(params_necesarios, prod_ord)
			self._insertaEnTablaEliminarOrdenes(params_para_eliminar_orden)
		except Exception as e:
			raise e
	
	def _obtieneDatosDeTabla(self, prod_ord):
		query_params_datos = 'select Codemp, codser, exactprodorder from FDOS_NEWORDERS_INFO where FinalProductOrder = ?'
		params_datos = system.db.runPrepQuery(query_params_datos, [prod_ord], 'ClaveiDB')
		
		return params_datos[0]
	
	def _generaParametrosParaEliminarOrden(self, params_necesarios,prod_ord):
		prod_ord_semielaborado = str(params_necesarios["exactprodorder"])
		prod_ord_separado = prod_ord_semielaborado.split("_")
		codeje = prod_ord_separado[1]
		num_ord = prod_ord_separado[2]
		
		params_para_eliminar_orden = {
			'CodEmp':str(params_necesarios["Codemp"]),
			'CodSer':str(params_necesarios["codser"]),
			'CodEje':int(codeje),
			'NumOrd':int(num_ord),
			'Estado':0
		}
		return params_para_eliminar_orden
	
	def _insertaEnTablaEliminarOrdenes(self, params_para_eliminar_orden):
		try:
			self._db.ejecutaNamedQuery('FD/ConsultasClavei/EliminaOrdenesDeProduccion', params_para_eliminar_orden)
		except Exception as e:
			raise Exception('No se ha podido eliminar orden de producción: ' + str(e))


class GestorPlanProduccion:
	_loggerBase = LoggerBase("GestorPlanProduccion")
	_db = None
	def __init__(self):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def refrescarPlan(self):
		try:
			ordenes_produccion = self._obtieneOrdenesProduccionDeClavei()
			self._actualizaPlanEnScada(ordenes_produccion)
		
		except Exception as e:
			raise Exception('Error al refrescar plan: '+str(e))
	
	def _actualizaPlanEnScada(self, ordenes_produccion):
		logger = self._loggerBase.obtieneLoggerEstandarizado('_actualizaPlanEnScada')
		logger.activaLogDebug()
		
		try:
			string_valores_a_insertar = self._generaStringValoresParaInsertarEnScada(ordenes_produccion)
			logger.logDebug(string_valores_a_insertar)
			self._limpiaPlanEnScada()
			logger.logDebug('Plan truncado')
			self._insertaPlanEnScada(string_valores_a_insertar)
			logger.logDebug('Plan insertado de nuevo')
		except Exception as e:
			raise Exception('Error al limpiar y/o insertar plan en SCADA: ' +str(e))
		
		
	def _insertaPlanEnScada(self, string_valores_a_insertar):
		params = {'values': string_valores_a_insertar}
		self._db.ejecutaNamedQuery('FD/ConsultasClavei/InsertaEnOrdenesAbiertasAllLines',params)
		
	def _limpiaPlanEnScada(self):
		query_truncate = 'truncate table rfid.open_production_orders_all_lines '
		system.db.runPrepUpdate(query_truncate, [], 'FactoryDB')
		
	def _obtieneOrdenesProduccionDeClavei(self):
		cod_emp = fd.globales.ParametrosGlobales.obtieneCodEmp()
		ordenes_produccion = db.ejecutaNamedQuery('FD/ConsultasClavei/ObtieneOrdenesProduccionAllLines', {"codemp":cod_emp})
		
		if ordenes_produccion.getRowCount != 0:
			return ordenes_produccion
		else:
			raise Exception("_obtieneOrdenesProduccionDeClavei - No se ha encontrado ordenes de produccion en Clavei")
		

	def _generaStringValoresParaInsertarEnScada(self, ordenes_produccion):
		py_ordenes_produccion = system.dataset.toPyDataSet(ordenes_produccion)
		constructor_sql = ConstructorSQL
		
		mapeo_columnas_tipo = [
			constructor_sql.creaMapeo('CodEmp', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('PordOrder', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('Referencia', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('CantidadTotal', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('UnidadesProducidas', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('Pendientes', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('InicioEstimado', constructor_sql.TIPO_COLUMNA_FECHA),
			constructor_sql.creaMapeo('FinEstimado', constructor_sql.TIPO_COLUMNA_FECHA),
			constructor_sql.creaMapeo('NomCli', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('CodCli', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('CodPed', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('CodEje', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('CodSer', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('description', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('ProdOrderDetailed', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('ArchiveID', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('ArchiveRecordID', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('FirstLaunchTime', constructor_sql.TIPO_COLUMNA_FECHA),
			constructor_sql.creaMapeo('EstimatedFinishDateFullOrder', constructor_sql.TIPO_COLUMNA_FECHA),
			constructor_sql.creaMapeo('ProductionLine', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('CodEjePed', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('CodSerPed', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('LinPed', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('Obs', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('FinalProductOrder', constructor_sql.TIPO_COLUMNA_TEXTO)
		]
		
		filas_insertar = constructor_sql.generaStringValoresParaInsertMasivo(py_ordenes_produccion, mapeo_columnas_tipo)
		return filas_insertar
		


class GestorLiberacionOrdenesProduccion:
	
	_showertray_id = ''
	_usuario = ''
	_db = None
	def __init__(self, showertray_id, usuario):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._showertray_id = showertray_id
		self._usuario = usuario
		
	def liberaOrdenProduccion(self):
		parametros = self._obtieneParametros()
		orden_liberada = self._db.ejecutaNamedQuery('FD/OrdenesProduccionScada/LiberaOrdenProduccion', parametros)
		return orden_liberada
		
	def _obtieneParametros(self):
		ordenes_produccion = fd.clasesordenesprod.gestion.GestorOrdenesProduccion.obtieneOrdenProduccion(self._showertray_id)
		parametros = {
			"showertray_id": self._showertray_id, 
			"username": self._usuario, 
			"production_order_id": ordenes_produccion[0]["production_order_id"], 
			"production_order_id_detailed": ordenes_produccion[0]["production_order_id_detailed"]
		}
		return parametros