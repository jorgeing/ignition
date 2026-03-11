class EtiquetasVia:
	"""Gestiona la impresión de todas las etiquetas asociadas a una vía de producción."""
	
	_via = 0
	_molde = ''
	_showertray_id = ''
	
	_db = None
	
	def __init__(self, via, molde, showertray_id):
		"""Inicializa y dispara la impresión de todos los tipos de etiquetas."""
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._via = via
		self._molde = molde
		self._showertray_id = showertray_id
		self.etiquetasPlatosUsa()
		self.etiquetaRfid()
		self.etiquetaRfidCorteDekor()
		self.etiquetaMoldes()
		self.etiquetasPlatosSchulte()
		
	def etiquetasPlatosUsa(self):
		"""Imprime la etiqueta especial para platos del mercado USA si aplica."""
		if self._compruebaSiEsMoldeUSA():
			fd.moduloetiquetas.modelosetiquetado.EtiquetaUSA(self._via, self._showertray_id).imprime()
	
	def etiquetasPlatosSchulte(self):
		"""Imprime la etiqueta especial para platos Schulte si aplica."""
		if self._compruebaSiEsMoldeSchulte():
			print('Es Schulte!')
			fd.moduloetiquetas.modelosetiquetado.EtiquetaSchulte(self._via, self._showertray_id).imprime()
			
	def etiquetaRfid(self):
		"""Imprime la etiqueta RFID del plato."""
		respuesta = fd.moduloetiquetas.modelosetiquetado.EtiquetaRFID(self._via, self._showertray_id, self._molde).imprime()
		#return respuesta
		
	def etiquetaMoldes(self):
		"""Imprime la etiqueta del molde si está pendiente de reparación."""
		if self._moldePendienteReparacion():
			fd.moduloetiquetas.modelosetiquetado.EtiquetaMoldes(self._via, self._molde).imprime()
		'''
		elif self._moldePendienteLimpiezaPlaya():
			fd.moduloetiquetas.modelosetiquetado.EtiquetaLimpiezaPlayasMoldes(self._via, self._molde).imprime()
		'''
			
	def etiquetaRfidCorteDekor(self):
		"""Imprime la etiqueta RFID para piezas de corte o dekor."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetaRFIDCorteDekor(self._via, self._showertray_id).imprime()
		
	@staticmethod
	def etiquetaInteriorPlato(impresora):
		"""Imprime la etiqueta interior del plato."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetasInteriores(impresora).imprime()
		
	def _obtieneModeloMolde(self):
		"""Consulta el número/modelo del molde en BD."""
		modelo_molde = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneNumeroMolde', {"mold_id":self._molde})
		return modelo_molde
	
	def _obtieneIdCliente(self):
		"""Obtiene el identificador del cliente para el plato."""
		id_cliente = self._db.ejecutaNamedQuery('FD/Platos/ObtieneIdClienteDeIdPlato', {"showertray_id":self._showertray_id})
		return id_cliente
		
	def _compruebaSiEsMoldeUSA(self):
		"""Verifica si el molde corresponde al mercado USA."""
		modelo_molde = self._obtieneModeloMolde()
		if modelo_molde == 33 or modelo_molde == 34:
			return True
		else:
			return False
	
	def _compruebaSiEsMoldeSchulte(self):
		"""Verifica si el cliente es Schulte."""
		id_cliente = self._obtieneIdCliente()
		if id_cliente == 7158:
			return True
		else:
			return False
			
	def _moldePendienteReparacion(self):
		"""Verifica si el molde tiene observaciones (pendiente de reparación)."""
		observaciones = fd.moldes.Molde(self._molde).obtieneObservaciones()
		if observaciones == None or observaciones.strip() == '':
			return False
		else:
			return True
	
	def _moldePendienteLimpiezaPlaya(self):
		"""Verifica si el molde supera los loops de limpieza de playas."""
		loops_limpieza = fd.moldes.Molde(self._molde).obtieneLoopsLimpiezaPlayas()
		if loops_limpieza >= 4:
			return True
		else:
			return False


class EtiquetasEnvasa:
	"""Gestiona la impresión de etiquetas en la zona de envasado."""
	
	_showertray_id = ''
	_impresora = 0
	
	
	def __init__(self, showertray_id, impresora):
		"""Inicializa e imprime etiqueta logística y A4."""
		self._showertray_id = showertray_id
		self._impresora = impresora
		self._etiquetaLosgistica()
		self._etiquetaA4()
	
	def _etiquetaLosgistica(self):
		"""Imprime la etiqueta logística del plato."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetaLogistica(self._showertray_id, self._impresora).imprime()
		
	def _etiquetaA4(self):
		"""Imprime la etiqueta A4 del plato."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetaA4(self._impresora, self._showertray_id).imprime()

class EtiquetasAreaMoldes:
	"""Gestiona la impresión de etiquetas en el área de moldes."""
	
	_id_molde = ''
	_epc_etiqueta_dec = ''
	
	
	def __init__(self, id_molde, epc_etiqueta_dec):
		"""Inicializa e imprime la etiqueta del tag del molde."""
		self._id_molde = id_molde
		self._epc_etiqueta_dec = epc_etiqueta_dec
		self._etiquetaTagMolde()
	
	def _etiquetaTagMolde(self):
		"""Imprime la etiqueta del tag RFID del molde."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetaTagMoldes(self._id_molde, self._epc_etiqueta_dec).imprime()
	
class EtiquetasMoldes:
	"""Clase base para etiquetas relacionadas con moldes."""
	
	_molde = ''
	
	def __init__(self, molde):
		"""Inicializa con el identificador del molde."""
		self._molde = molde


class EtiquetasInventario:
	"""Gestiona las etiquetas de ubicación para el inventario."""
	
	_ubicacion = ''
	_almacen = ''
	_codigo_barras = ''
	_impresora = 0
	
	def __init__(self, ubicacion, almacen, codigo_barras, impresora):
		"""Inicializa con datos de ubicación e impresora."""
		self._ubicacion = ubicacion
		self._almacen = almacen
		self._codigo_barras = codigo_barras
		self._impresora = impresora
	
	def etiquetaUbicacionInventario(self):
		"""Imprime la etiqueta de ubicación de inventario."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetaUbicacionInventario(self._ubicacion, self._almacen, self._codigo_barras, self._impresora).imprime()
	
	
class EtiquetasPedidosClientes:
	"""Gestiona la impresión de etiquetas de pedidos de clientes."""
	_numero_pedido = 0
	_anyo_pedido = 1900
	_impresora = 0
	
	def __init__(self, numero_pedido, anyo_pedido, impresora):
		"""Inicializa con número de pedido, año e impresora."""
		self._numero_pedido = numero_pedido
		self._anyo_pedido = anyo_pedido
		self._impresora = impresora
	
	def etiquetaPedidos(self):
		"""Imprime las etiquetas del pedido de cliente."""
		fd.moduloetiquetas.modelosetiquetado.EtiquetaPedidos(self._impresora, self._numero_pedido, self._anyo_pedido).imprime()
	
	
	
	
	