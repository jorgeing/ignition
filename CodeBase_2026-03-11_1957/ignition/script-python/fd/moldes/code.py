from fd.utilidades.logger import *
from fd.utilidades.dataset import *

class Molde:
	_loggerBase = LoggerBase("Moldes")
	
	MIN_TAG_CANTIDAD = 1
	
	_mold_id = ""
	_informacion = {}
	_ruta_modelos_cache = '[rfid_tags]Cache/ModelsDataset'
	
	def __init__(self, mold_id):
		self._mold_id = mold_id
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._obtieneInfo()
		
		
	def refresca(self):
		self._obtieneInfo()
		
	def obtieneIdMolde(self):
		return self._mold_id
		
	def moldePuedeEstarActivo(self, tags_leidos):
		ciclos_actuales = self.ciclosActuales()
		max_ciclos = self.limiteDeCiclos()
		
		if tags_leidos >= self.MIN_TAG_CANTIDAD and ciclos_actuales < max_ciclos:
			return True
			
	def obtieneEstadoMolde(self):
		return self._informacion["status"]
	
	def obtieneLoopsLimpiezaPlayas(self):
		return self._informacion["loops_limpieza_playa"]
		
	def limiteDeCiclos(self):
		return self._informacion["max_loops_between_repairs"]
		
	def ciclosActuales(self):
		return self._informacion["loops_last_repair"]
		
	def obtieneObservaciones(self):
		return self._informacion["observation"]
		
	def obtieneUltimosTagsDetectados(self):
		return self._informacion["last_detected_tag_count"]
	
	def obtieneSKUModelo(self):
		modelos_cache = self._obtieneDatasetModelosCache()
		id_modelo = int(self._mold_id[29:32])
		nombre_sku = ''
		nombre_largo_modelo = ''
		sku_molde = ''
		for fila in modelos_cache:
			if fila['id'] == id_modelo:
				nombre_sku = fila['sku_name']
				nombre_largo_modelo = fila['long_name']
		sku_molde = nombre_sku + self._mold_id[32:35] + self._mold_id[35:]
		return id_modelo, nombre_sku, nombre_largo_modelo, sku_molde
		
	def obtieneShowertrayDentroDelMolde(self):
		showertray_id = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneShowertrayInterior', {"mold_id": self._mold_id})
		return showertray_id
	
	def _obtieneDatasetModelosCache(self):
		dataset_modelos = system.tag.readBlocking(self._ruta_modelos_cache)[0].value
		dataset_modelos = system.dataset.toPyDataSet(dataset_modelos)
		return dataset_modelos
			
	def _obtieneInfo(self):
		informacion_dataset = self._db.ejecutaNamedQuery('FD/Moldes/EstadoMolde', {"mold_id":self._mold_id})
		if informacion_dataset.getRowCount()>0:
			self._informacion = ConversorFormatosDataset.filaDatasetADiccionario(informacion_dataset, 0)
		else:
			raise NoEncontradoException(self._mold_id)
		


class GestorMoldes:
	_loggerBase = LoggerBase("GestorMoldes")
	
	ID_ESTADO_ACTIVO = 1 
	ID_ESTADO_PENDIENTE_REPARACION = 2
	ID_ESTADO_REPARACION = 3
	ID_ESTADO_BAJA = 5
	
	_id_molde = None
	_parametros_actualizar={}
	_molde = None
	
	def __init__(self, molde):
		self._molde = molde
		self._id_molde = self._molde
		self._parametros_actualizar = self._generaParametrosParaActualizarEstadoMoldes()
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def activarMolde(self):
		self._actualizaEstadoMolde(self.ID_ESTADO_ACTIVO)
		
	def activarMoldeSiEsPosible(self):
		if self._moldePuedeEstarActivo():
			self.activarMolde()
		
 
		self._actualizaEstadoMolde(self.ID_ESTADO_BAJA)
	
	def moldeAPendienteReparacion(self):
		self._actualizaEstadoMolde(self.ID_ESTADO_PENDIENTE_REPARACION)
	
	def moldeEnReparacion(self):
		self._actualizaEstadoMolde(self.ID_ESTADO_REPARACION)
	
	def darBajaMolde(self):
		self._actualizaEstadoMolde(self.ID_ESTADO_BAJA)
	
	def _generaParametrosParaActualizarEstadoMoldes(self):
		place_id = fd.globales.ParametrosGlobales.obtieneIdFabrica()
		
		params_actualiza_estado_moldes = {
			'mold_id': str(self._id_molde),
			'place_id': int(place_id)
		}
		
		return params_actualiza_estado_moldes
		
	def _actualizaEstadoMolde(self, estado_molde):
		params_actualiza_estado_moldes = self._parametros_actualizar
		params_actualiza_estado_moldes['status']=estado_molde
		try:
			filas_afectadas = self._db.ejecutaNamedQuery('FD/Moldes/ActualizarEstadoMolde', params_actualiza_estado_moldes)
			if filas_afectadas == 0:
				raise Exception('No se ha podido actualizar estado del molde')
		except Exception as e:
			raise Exception('No se ha podido actualizar estado del molde: ' + str(e))
		
	
class GestorTagsMoldes:
	_loggerBase = LoggerBase("GestorMoldes")
	
	ID_ESTADO_ACTIVO = 1 
	ID_ESTADO_PENDIENTE_REPARACION = 2
	ID_ESTADO_REPARACION = 3
	ID_ESTADO_BAJA = 5
	
	MIN_TAG_CANTIDAD = 1
	
	_id_molde=""
	_tags_leidos = 0
	_molde = None
	
	def __init__(self, tags_leidos, molde):
		self._molde = molde
		self._id_molde = self._molde.obtieneIdMolde()
		self._tags_leidos = tags_leidos
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def compruebaYActualizaFalsosPendientesReparacion(self):
		if self._tieneMasTagsQueAntes():
			self._molde.activarMoldeSiEsPosible()
		self.actualizaCantidadTagsDetectados()
			
	def actualizaCantidadTagsDetectados(self):
		params_actualiza_tags = self._generaParametrosCantidadTagsDetectados()
		self._db.ejecutaNamedQuery('FD/Moldes/ActualizaCantidadTagsMolde', params_actualiza_tags)
		
	def _tieneMasTagsQueAntes(self):
		tags_ultimos_detectados = self._molde.obtieneUltimosTagsDetectados()
		self._tags_leidos > tags_ultimos_detectados
		
	def _generaParametrosCantidadTagsDetectados(self):
		observaciones = self._molde.obtieneObservaciones()
		observaciones_nuevas = self._eliminaParteDeLaObservacion(observaciones)
		
		params_actualiza_tags = {
		'mold_id': str(self._id_molde),
		'tag_count': int(self._tags_leidos),
		'observation': str(observaciones_nuevas)
		}
		return params_actualiza_tags

	def _eliminaParteDeLaObservacion(self, observacion):
		if observacion==None or len(observacion)==0:
			return ''
		observacion_dividida = observacion.split('-')
		observacion_actualizada = []
		
		for division in observacion_dividida:
			if 'CHIPS INSUFICIENTES' not in division:
				observacion_actualizada.append(division)
				
		return '-'.join(observacion_actualizada)
		
class GestorBusquedaEPCMoldes:
	
	_moldes_seleccionados = []
	
	def __init__(self, moldes_seleccionados):
		self._moldes_seleccionados = moldes_seleccionados
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def devuelveEPCMolde(self):
		return self._obtieneEPCdeMoldes()
		
	def muestraMoldesSeleccionados(self):
		return self._moldes_seleccionados
		
	def _obtieneEPCdeMoldes(self):
		moldes_seleccionados = self._generaParametrosMoldesSeleccionados()
		params_moldes_seleccionados = {"moldes_seleccionados":str(moldes_seleccionados)}
		epc_moldes = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneEPCdeTagsMolde', params_moldes_seleccionados)
		return epc_moldes
		
	def _generaParametrosMoldesSeleccionados(self):
		moldes_seleccionados = ','.join(["'" + molde + "'" for molde in self._moldes_seleccionados])
		return moldes_seleccionados
		
class EventoActualizaEstadoMolde:

	def __init__(self):
		pass
		
	def actualizaEstadoMolde(self, id_molde, new_status, showertray):
		parametros_estado_molde = self._generaParametrosEstadoMolde(id_molde, new_status, showertray)
		fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase').ejecutaNamedQuery('FD/Moldes/InsertaEventoMolde', parametros_estado_molde)
		
	
	def _generaParametrosEstadoMolde(self, id_molde, new_status, showertray):
		
		parametros_estado_molde = {
			'mold_id':id_molde,
			'status':new_status,
			'showertray_inside': showertray,
			'place_id': fd.globales.ParametrosGlobales._place_id,
			't_stamp': system.date.now()
		}
		return parametros_estado_molde
		
	

class SupervisorPintadoMolde:
	
	_ruta_pintura_plc = '[rfid_tags]PLC_Inputs/paint_ml'
	_ruta_pintura_destino = '[rfid_tags]Events/painted_event_ml'
	
	def __init__(self):
		pass
		
	def obtieneValorPinturaYEscribeEnTagDestino(self):
		pintura_ml = system.tag.readBlocking(self._ruta_pintura_plc)[0].value
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._ruta_pintura_destino, pintura_ml)

class SupervisorEstadoMoldes:
	
	_id_molde = ''
	_ruta_cuenta_tag_molde = ''
	
	def __init__(self, id_molde, via_produccion):
		self._id_molde = id_molde
		if via_produccion == 1 or via_produccion == -1:
			self._ruta_cuenta_tag_molde = '[rfid_tags]Computed/line1_paint_input_current_mold_max_tag_count'
		else:
			self._ruta_cuenta_tag_molde = '[rfid_tags]Antennas/Molds/line2_paint_input/tag_count'
	
	def gestionaEstadoTagsMoldes(self):
		molde = Molde(self._id_molde)
		cuenta_tag_molde = system.tag.readBlocking(self._ruta_cuenta_tag_molde)[0].value
		gestor_tags_moldes = GestorTagsMoldes(cuenta_tag_molde, molde)
		gestor_tags_moldes.compruebaYActualizaFalsosPendientesReparacion()