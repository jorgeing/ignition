import uuid
from fd.utilidades.logger import *
from fd.utilidades.sql import *
from fd.utilidades.dataset import *

class AsignadorOrdenProduccion:
	
	_id_bloqueo = ""
	_ejecutador_named_queries = None
	
	def __init__(self, id_bloqueo):
		self._ejecutador_named_queries = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		self._id_bloqueo = id_bloqueo
		
	@staticmethod
	def obtieneAsignadorConUUID():
		id_bloqueo_aleatorio = str(uuid.uuid4())
		return AsignadorOrdenProduccion(id_bloqueo_aleatorio)
			
	def obtieneYBloqueaOrdenProduccion(self, sku_molde, id_color, limite_ordenes):
		parametros = {'sku_molde':sku_molde, 'id_color':id_color, 'id_bloqueo':self._id_bloqueo, 'limite_ordenes':limite_ordenes}
		return self._ejecutador_named_queries.ejecutaNamedQuery('FD/PlanificacionProduccion/SeleccionesDelPlan/ObtieneYBloqueaOrdenProduccionPorMoldeYColor',parametros)
		
	def transfiereOrdenProduccion(self,id_bloqueo_destino):
		query = "SELECT rfid.transfer_locked_prod_order(?, ?);"
		system.db.runPrepQuery(query, [self._id_bloqueo, id_bloqueo_destino])
	
	def desbloqueaOrdenProduccion(self):
		query = "SELECT rfid.release_production_order(?);"
		system.db.runScalarPrepQuery(query,[self._id_bloqueo])
	
	def eliminaBloqueo(self):
		query = "DELETE FROM rfid.locked_prod_orders WHERE lock_place_id=?"
		system.db.runPrepUpdate(query, [self._id_bloqueo])
	
	def obtieneOrdenProduccionBloqueada(self):
		query = "SELECT production_order_id_detailed FROM rfid.locked_prod_orders WHERE lock_place_id = ?"
		return system.db.runScalarPrepQuery(query, [self._id_bloqueo])
		
	def existeBloqueo(self):
		query = "SELECT lock_place_id FROM rfid.locked_prod_orders WHERE lock_place_id = ?"
		id_bloqueo = system.db.runScalarPrepQuery(query, [self._id_bloqueo])
		return bool(id_bloqueo)
		
	def obtieneIdBloqueo(self):
		return self._id_bloqueo
	
class AsignadorOrdenProduccionDesdeNumeroSerie:
	
	_asignador_ordenes = None
	_numero_serie = ''
	
	def __init__(self, numero_serie):
		self._numero_serie = numero_serie
		self._asignador_ordenes = AsignadorOrdenProduccion.obtieneAsignadorConUUID()
		
	def asignaOrdenProduccion():
		pass