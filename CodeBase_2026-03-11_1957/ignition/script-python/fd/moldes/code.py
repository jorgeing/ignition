from fd.utilidades.logger import *
from fd.utilidades.dataset import *

class Molde:
	"""Representa un molde de fundición con su estado, ciclos y metadatos asociados."""

	_loggerBase = LoggerBase("Moldes")
	
	MIN_TAG_CANTIDAD = 1
	
	_mold_id = ""
	_informacion = {}
	_ruta_modelos_cache = '[rfid_tags]Cache/ModelsDataset'
	
	def __init__(self, mold_id):
		"""Inicializa el molde con su identificador y carga su información desde la base de datos."""
		self._mold_id = mold_id
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._obtieneInfo()
		
		
	def refresca(self):
		"""Recarga la información del molde desde la base de datos."""
		self._obtieneInfo()
		
	def obtieneIdMolde(self):
		"""Devuelve el identificador único del molde."""
		return self._mold_id
		
	def moldePuedeEstarActivo(self, tags_leidos):
		"""Determina si el molde puede estar activo según los tags leídos y los ciclos actuales."""
		ciclos_actuales = self.ciclosActuales()
		max_ciclos = self.limiteDeCiclos()
		
		if tags_leidos >= self.MIN_TAG_CANTIDAD and ciclos_actuales < max_ciclos:
			return True
			
	def obtieneEstadoMolde(self):
		"""Devuelve el estado actual del molde."""
		return self._informacion["status"]
	
	def obtieneLoopsLimpiezaPlayas(self):
		"""Devuelve el número de loops de limpieza de playas del molde."""
		return self._informacion["loops_limpieza_playa"]
		
	def limiteDeCiclos(self):
		"""Devuelve el número máximo de ciclos permitidos entre reparaciones."""
		return self._informacion["max_loops_between_repairs"]
		
	def ciclosActuales(self):
		"""Devuelve el número de ciclos realizados desde la última reparación."""
		return self._informacion["loops_last_repair"]
		
	def obtieneObservaciones(self):
		"""Devuelve las observaciones registradas para el molde."""
		return self._informacion["observation"]
		
	def obtieneUltimosTagsDetectados(self):
		"""Devuelve la cantidad de tags detectados en la última lectura del molde."""
		return self._informacion["last_detected_tag_count"]
	
	def obtieneSKUModelo(self):
		"""Obtiene el SKU del modelo asociado al molde consultando la caché de modelos."""
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
		"""Consulta y devuelve el identificador del showertray que se encuentra dentro del molde."""
		showertray_id = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneShowertrayInterior', {"mold_id": self._mold_id})
		return showertray_id
	
	def _obtieneDatasetModelosCache(self):
		"""Lee el dataset de modelos desde la caché de tags y lo convierte a formato Python."""
		dataset_modelos = system.tag.readBlocking(self._ruta_modelos_cache)[0].value
		dataset_modelos = system.dataset.toPyDataSet(dataset_modelos)
		return dataset_modelos
			
	def _obtieneInfo(self):
		"""Carga la información del molde desde la base de datos y la almacena internamente."""
		informacion_dataset = self._db.ejecutaNamedQuery('FD/Moldes/EstadoMolde', {"mold_id":self._mold_id})
		if informacion_dataset.getRowCount()>0:
			self._informacion = ConversorFormatosDataset.filaDatasetADiccionario(informacion_dataset, 0)
		else:
			raise NoEncontradoException(self._mold_id)
		


class GestorMoldes:
	"""Gestiona los cambios de estado de un molde en el sistema de producción."""

	_loggerBase = LoggerBase("GestorMoldes")
	
	ID_ESTADO_ACTIVO = 1 
	ID_ESTADO_PENDIENTE_REPARACION = 2
	ID_ESTADO_REPARACION = 3
	ID_ESTADO_BAJA = 5
	
	_id_molde = None
	_parametros_actualizar={}
	_molde = None
	
	def __init__(self, molde):
		"""Inicializa el gestor con el identificador del molde y prepara los parámetros de actualización."""
		self._molde = molde
		self._id_molde = self._molde
		self._parametros_actualizar = self._generaParametrosParaActualizarEstadoMoldes()
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def activarMolde(self):
		"""Activa el molde estableciendo su estado como activo."""
		self._actualizaEstadoMolde(self.ID_ESTADO_ACTIVO)
		
	def activarMoldeSiEsPosible(self):
		"""Activa el molde únicamente si cumple las condiciones para estar activo."""
		if self._moldePuedeEstarActivo():
			self.activarMolde()
		
 
		self._actualizaEstadoMolde(self.ID_ESTADO_BAJA)
	
	def moldeAPendienteReparacion(self):
		"""Cambia el estado del molde a pendiente de reparación."""
		self._actualizaEstadoMolde(self.ID_ESTADO_PENDIENTE_REPARACION)
	
	def moldeEnReparacion(self):
		"""Cambia el estado del molde a en reparación."""
		self._actualizaEstadoMolde(self.ID_ESTADO_REPARACION)
	
	def darBajaMolde(self):
		"""Da de baja el molde estableciendo su estado como baja."""
		self._actualizaEstadoMolde(self.ID_ESTADO_BAJA)
	
	def _generaParametrosParaActualizarEstadoMoldes(self):
		"""Genera el diccionario de parámetros necesarios para actualizar el estado del molde en la base de datos."""
		place_id = fd.globales.ParametrosGlobales.obtieneIdFabrica()
		
		params_actualiza_estado_moldes = {
			'mold_id': str(self._id_molde),
			'place_id': int(place_id)
		}
		
		return params_actualiza_estado_moldes
		
	def _actualizaEstadoMolde(self, estado_molde):
		"""Ejecuta la query de actualización de estado del molde en la base de datos."""
		params_actualiza_estado_moldes = self._parametros_actualizar
		params_actualiza_estado_moldes['status']=estado_molde
		try:
			filas_afectadas = self._db.ejecutaNamedQuery('FD/Moldes/ActualizarEstadoMolde', params_actualiza_estado_moldes)
			if filas_afectadas == 0:
				raise Exception('No se ha podido actualizar estado del molde')
		except Exception as e:
			raise Exception('No se ha podido actualizar estado del molde: ' + str(e))
		
	
class GestorTagsMoldes:
	"""Gestiona la verificación y actualización de la cantidad de tags RFID detectados en un molde."""

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
		"""Inicializa el gestor con el número de tags leídos y el objeto molde asociado."""
		self._molde = molde
		self._id_molde = self._molde.obtieneIdMolde()
		self._tags_leidos = tags_leidos
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def compruebaYActualizaFalsosPendientesReparacion(self):
		"""Comprueba si el molde tiene más tags que antes para descartar falsos pendientes de reparación y actualiza la cantidad."""
		if self._tieneMasTagsQueAntes():
			self._molde.activarMoldeSiEsPosible()
		self.actualizaCantidadTagsDetectados()
			
	def actualizaCantidadTagsDetectados(self):
		"""Persiste en la base de datos la cantidad actual de tags detectados en el molde."""
		params_actualiza_tags = self._generaParametrosCantidadTagsDetectados()
		self._db.ejecutaNamedQuery('FD/Moldes/ActualizaCantidadTagsMolde', params_actualiza_tags)
		
	def _tieneMasTagsQueAntes(self):
		"""Comprueba si la lectura actual ha detectado más tags que la última registrada."""
		tags_ultimos_detectados = self._molde.obtieneUltimosTagsDetectados()
		self._tags_leidos > tags_ultimos_detectados
		
	def _generaParametrosCantidadTagsDetectados(self):
		"""Genera el diccionario de parámetros para actualizar la cantidad de tags en la base de datos."""
		observaciones = self._molde.obtieneObservaciones()
		observaciones_nuevas = self._eliminaParteDeLaObservacion(observaciones)
		
		params_actualiza_tags = {
		'mold_id': str(self._id_molde),
		'tag_count': int(self._tags_leidos),
		'observation': str(observaciones_nuevas)
		}
		return params_actualiza_tags

	def _eliminaParteDeLaObservacion(self, observacion):
		"""Elimina la parte de la observación relativa a chips insuficientes."""
		if observacion==None or len(observacion)==0:
			return ''
		observacion_dividida = observacion.split('-')
		observacion_actualizada = []
		
		for division in observacion_dividida:
			if 'CHIPS INSUFICIENTES' not in division:
				observacion_actualizada.append(division)
				
		return '-'.join(observacion_actualizada)
		
class GestorBusquedaEPCMoldes:
	"""Gestiona la búsqueda de códigos EPC asociados a una selección de moldes."""

	_moldes_seleccionados = []
	
	def __init__(self, moldes_seleccionados):
		"""Inicializa el gestor con la lista de moldes seleccionados."""
		self._moldes_seleccionados = moldes_seleccionados
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		
	def devuelveEPCMolde(self):
		"""Devuelve los códigos EPC de los moldes seleccionados."""
		return self._obtieneEPCdeMoldes()
		
	def muestraMoldesSeleccionados(self):
		"""Devuelve la lista de moldes seleccionados."""
		return self._moldes_seleccionados
		
	def _obtieneEPCdeMoldes(self):
		"""Consulta la base de datos para obtener los EPC de los tags de los moldes seleccionados."""
		moldes_seleccionados = self._generaParametrosMoldesSeleccionados()
		params_moldes_seleccionados = {"moldes_seleccionados":str(moldes_seleccionados)}
		epc_moldes = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneEPCdeTagsMolde', params_moldes_seleccionados)
		return epc_moldes
		
	def _generaParametrosMoldesSeleccionados(self):
		"""Genera la cadena de texto con los identificadores de moldes seleccionados en formato SQL."""
		moldes_seleccionados = ','.join(["'" + molde + "'" for molde in self._moldes_seleccionados])
		return moldes_seleccionados
		
class EventoActualizaEstadoMolde:
	"""Registra eventos de cambio de estado de moldes en la base de datos."""

	def __init__(self):
		"""Inicializa el objeto de evento de actualización de estado de molde."""
		pass
		
	def actualizaEstadoMolde(self, id_molde, new_status, showertray):
		"""Inserta un evento de cambio de estado del molde en la base de datos."""
		parametros_estado_molde = self._generaParametrosEstadoMolde(id_molde, new_status, showertray)
		fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase').ejecutaNamedQuery('FD/Moldes/InsertaEventoMolde', parametros_estado_molde)
		
	
	def _generaParametrosEstadoMolde(self, id_molde, new_status, showertray):
		"""Genera el diccionario de parámetros para insertar el evento de estado del molde."""
		
		parametros_estado_molde = {
			'mold_id':id_molde,
			'status':new_status,
			'showertray_inside': showertray,
			'place_id': fd.globales.ParametrosGlobales._place_id,
			't_stamp': system.date.now()
		}
		return parametros_estado_molde
		
	

class SupervisorPintadoMolde:
	"""Supervisa y transfiere el valor de pintura desde el tag del PLC al tag de eventos."""

	_ruta_pintura_plc = '[rfid_tags]PLC_Inputs/paint_ml'
	_ruta_pintura_destino = '[rfid_tags]Events/painted_event_ml'
	
	def __init__(self):
		"""Inicializa el supervisor de pintado de molde."""
		pass
		
	def obtieneValorPinturaYEscribeEnTagDestino(self):
		"""Lee el valor de mililitros de pintura del PLC y lo escribe en el tag de destino de eventos."""
		pintura_ml = system.tag.readBlocking(self._ruta_pintura_plc)[0].value
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(self._ruta_pintura_destino, pintura_ml)

class SupervisorEstadoMoldes:
	"""Supervisa el estado de los tags de un molde y gestiona las actualizaciones correspondientes."""

	_id_molde = ''
	_ruta_cuenta_tag_molde = ''
	
	def __init__(self, id_molde, via_produccion):
		"""Inicializa el supervisor con el ID del molde y la vía de producción para determinar la ruta del tag."""
		self._id_molde = id_molde
		if via_produccion == 1 or via_produccion == -1:
			self._ruta_cuenta_tag_molde = '[rfid_tags]Computed/line1_paint_input_current_mold_max_tag_count'
		else:
			self._ruta_cuenta_tag_molde = '[rfid_tags]Antennas/Molds/line2_paint_input/tag_count'
	
	def gestionaEstadoTagsMoldes(self):
		"""Gestiona el estado de los tags del molde comprobando y actualizando la cantidad de tags detectados."""
		molde = Molde(self._id_molde)
		cuenta_tag_molde = system.tag.readBlocking(self._ruta_cuenta_tag_molde)[0].value
		gestor_tags_moldes = GestorTagsMoldes(cuenta_tag_molde, molde)
		gestor_tags_moldes.compruebaYActualizaFalsosPendientesReparacion()