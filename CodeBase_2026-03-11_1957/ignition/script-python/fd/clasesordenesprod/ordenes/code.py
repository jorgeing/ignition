from fd.utilidades.logger import *
from fd.utilidades.sql import *
from fd.utilidades.dataset import *

class OrdenProduccionBase:
	_id_orden_produccion = ""
	_id_orden_produccion_detallada = ""
	_info = {
		"sku":"",
		"codcli":9999
	}
	
	def __init__(self, id_orden):
		self._rellenaIdOrdenProduccion(id_orden)
		self._consultaInfo()
		
	def obtieneIdOrden(self):
		return self._id_orden_produccion
		
	def obtieneIdOrdenDetallada(self):
		return self._id_orden_produccion_detallada
		
	def obtieneInfoComoDataset(self):
		return fd.utilidades.dataset.ConversorFormatosDataset.diccionarioAFilaDataset(self._info)
		
	def obtieneInfo(self):
		return self._info
		
	def esOrdenNula(self):
		return not self._id_orden_produccion
			
	def _rellenaIdOrdenProduccion(self, id_orden):
		self._id_orden_produccion_detallada = id_orden
		self._id_orden_produccion = self._ordenProduccionDetalladaAOrdenProduccion(id_orden)
		
	def _ordenProduccionDetalladaAOrdenProduccion(self,id_orden):
		return id_orden.split("\\")[0]
		
	def _consultaInfo(self):
		raise NotImplementedError("Debes implementar este método")

class OrdenProduccionClavei(OrdenProduccionBase):

	def _consultaInfo(self):
		query_clavei = "SELECT * FROM FDOS_ProductionOrdersWithInfo where exactprodorder = ?"
		bd_clavei = fd.globales.ParametrosGlobales.obtieneNombreBaseDatosClavei()
		
		dataset_clavei = system.db.runPrepQuery(query_clavei, [self._id_orden_produccion], bd_clavei )
		
		if dataset_clavei.getRowCount()>0:
			self._info = ConversorFormatosDataset.filaDatasetADiccionario(dataset_clavei, 0)
		else:
			raise fd.excepciones.AccesoBaseDatosException("No se ha podido encontrar la orden de produccion con id: " + self._id_orden_produccion)
			
class OrdenProduccionScada(OrdenProduccionBase):
	
	def obtieneSku(self):
		return self._info["productref"]
		
	def _consultaInfo(self):
		db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase') 
		query_factorydb = db.ejecutaNamedQuery('FD/OrdenesProduccionScada/ObtieneSkuDeOrdenProduccion', {"production_order_id": self._id_orden_produccion})
		self._info = ConversorFormatosDataset.filaDatasetADiccionario(query_factorydb, 0)
		
class OrdenProduccionDetallada(OrdenProduccionBase):
	
	def obtieneSku(self):
		return self._info["sku"]
		
	def obtieneIdColor(self):
		if self.esOrdenNula():
			return -1
		else:
			return fd.sku.ManejadorSku(self._info["sku"]).obtieneIdColor()
			
	def obtieneIdCliente(self):
		return self._info["codcli"]
	
	def _consultaInfo(self):
		if self._id_orden_produccion_detallada:
			db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
			query_factorydb = db.ejecutaNamedQuery('FD/OrdenesProduccionScada/ObtieneInfoDeOrdenProduccion', {"production_order_id": self._id_orden_produccion_detallada})
			self._info = ConversorFormatosDataset.filaDatasetADiccionario(query_factorydb, 0)