class EtiquetasVia:
	
	_via = 0
	_molde = ''
	_showertray_id = ''
	
	_db = None
	
	def __init__(self, via, molde, showertray_id):
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
		if self._compruebaSiEsMoldeUSA():
			fd.moduloetiquetas.modelosetiquetado.EtiquetaUSA(self._via, self._showertray_id).imprime()
	
	def etiquetasPlatosSchulte(self):
		if self._compruebaSiEsMoldeSchulte():
			print('Es Schulte!')
			fd.moduloetiquetas.modelosetiquetado.EtiquetaSchulte(self._via, self._showertray_id).imprime()
			
	def etiquetaRfid(self):
		respuesta = fd.moduloetiquetas.modelosetiquetado.EtiquetaRFID(self._via, self._showertray_id, self._molde).imprime()
		#return respuesta
		
	def etiquetaMoldes(self):
		if self._moldePendienteReparacion():
			fd.moduloetiquetas.modelosetiquetado.EtiquetaMoldes(self._via, self._molde).imprime()
		'''
		elif self._moldePendienteLimpiezaPlaya():
			fd.moduloetiquetas.modelosetiquetado.EtiquetaLimpiezaPlayasMoldes(self._via, self._molde).imprime()
		'''
			
	def etiquetaRfidCorteDekor(self):
		fd.moduloetiquetas.modelosetiquetado.EtiquetaRFIDCorteDekor(self._via, self._showertray_id).imprime()
		
	@staticmethod
	def etiquetaInteriorPlato(impresora):
		fd.moduloetiquetas.modelosetiquetado.EtiquetasInteriores(impresora).imprime()
		
	def _obtieneModeloMolde(self):
		modelo_molde = self._db.ejecutaNamedQuery('FD/Moldes/ObtieneNumeroMolde', {"mold_id":self._molde})
		return modelo_molde
	
	def _obtieneIdCliente(self):
		id_cliente = self._db.ejecutaNamedQuery('FD/Platos/ObtieneIdClienteDeIdPlato', {"showertray_id":self._showertray_id})
		return id_cliente
		
	def _compruebaSiEsMoldeUSA(self):
		modelo_molde = self._obtieneModeloMolde()
		if modelo_molde == 33 or modelo_molde == 34:
			return True
		else:
			return False
	
	def _compruebaSiEsMoldeSchulte(self):
		id_cliente = self._obtieneIdCliente()
		if id_cliente == 7158:
			return True
		else:
			return False
			
	def _moldePendienteReparacion(self):
		observaciones = fd.moldes.Molde(self._molde).obtieneObservaciones()
		if observaciones == None or observaciones.strip() == '':
			return False
		else:
			return True
	
	def _moldePendienteLimpiezaPlaya(self):
		loops_limpieza = fd.moldes.Molde(self._molde).obtieneLoopsLimpiezaPlayas()
		if loops_limpieza >= 4:
			return True
		else:
			return False


class EtiquetasEnvasa:
	
	_showertray_id = ''
	_impresora = 0
	
	
	def __init__(self, showertray_id, impresora):
		self._showertray_id = showertray_id
		self._impresora = impresora
		self._etiquetaLosgistica()
		self._etiquetaA4()
	
	def _etiquetaLosgistica(self):
		fd.moduloetiquetas.modelosetiquetado.EtiquetaLogistica(self._showertray_id, self._impresora).imprime()
		
	def _etiquetaA4(self):
		fd.moduloetiquetas.modelosetiquetado.EtiquetaA4(self._impresora, self._showertray_id).imprime()

class EtiquetasAreaMoldes:
	
	_id_molde = ''
	_epc_etiqueta_dec = ''
	
	
	def __init__(self, id_molde, epc_etiqueta_dec):
		self._id_molde = id_molde
		self._epc_etiqueta_dec = epc_etiqueta_dec
		self._etiquetaTagMolde()
	
	def _etiquetaTagMolde(self):
		fd.moduloetiquetas.modelosetiquetado.EtiquetaTagMoldes(self._id_molde, self._epc_etiqueta_dec).imprime()
	
class EtiquetasMoldes:
	
	_molde = ''
	
	def __init__(self, molde):
		self._molde = molde


class EtiquetasInventario:
	
	_ubicacion = ''
	_almacen = ''
	_codigo_barras = ''
	_impresora = 0
	
	def __init__(self, ubicacion, almacen, codigo_barras, impresora):
		self._ubicacion = ubicacion
		self._almacen = almacen
		self._codigo_barras = codigo_barras
		self._impresora = impresora
	
	def etiquetaUbicacionInventario(self):
		fd.moduloetiquetas.modelosetiquetado.EtiquetaUbicacionInventario(self._ubicacion, self._almacen, self._codigo_barras, self._impresora).imprime()
	
	
class EtiquetasPedidosClientes:
	_numero_pedido = 0
	_anyo_pedido = 1900
	_impresora = 0
	
	def __init__(self, numero_pedido, anyo_pedido, impresora):
		self._numero_pedido = numero_pedido
		self._anyo_pedido = anyo_pedido
		self._impresora = impresora
	
	def etiquetaPedidos(self):
		fd.moduloetiquetas.modelosetiquetado.EtiquetaPedidos(self._impresora, self._numero_pedido, self._anyo_pedido).imprime()
	
	
	
	
	