class inventarioRFID:
	
	PREFIJO_ID_PLATO = '1'
	PREFIJO_ID_MOLDE = '2'
	
	TABLA_INVENTARIO_PLATOS = 'rfid.inventario_rfid'
	TABLA_INVENTARIO_MOLDES = 'mold_management.inventario_moldes'
	
	_tabla_entrada = []
	_t_stamp = 0
	_lugar = ''
	_sublugar = ''
	_tabla_string = []
	_prefijo_id = ''
	_idx_tag_id = 0
	_idx_rssi = 0
	_tabla_inventario = []
	_id_tags_procesados = []
	
	def __init__(self, tabla, timestamp, lugar = '', sublugar = ''):
		logger = system.util.getLogger('subir_inventario_molde')
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._tabla_entrada = tabla
		self._lugar = lugar
		self._sublugar = sublugar
		logger.info('_tabla_entrada'+str(self._tabla_entrada))
		self._eliminaFilasVaciasDeTablaEntrada()
		self._t_stamp = self._formateaTimeStamp(timestamp)
		self._tabla_string = self._convierteFilasEnStringSeparadaPorComas()
		logger.info('_tabla_string'+str(self._tabla_string))
		self._asignaPosicionCabecera()
		
		
	def subirInventarioPlatos(self):
		self._id_tags_procesados = []
		tabla = self.TABLA_INVENTARIO_PLATOS
		self._prefijo_id = self.PREFIJO_ID_PLATO
		try:
			self._eliminaInventarioAnterior(tabla)
			self._recorreTablaPlato()
			self._insertaNuevoInventario(tabla)
		except Exception as e:
			raise fd.excepciones.InventarioException(str(self._tabla_string))
		
	def subirInventarioMoldes(self):
		self._id_tags_procesados = []
		self._prefijo_id = self.PREFIJO_ID_MOLDE
		try:
			self._eliminaInventarioAnteriorMoldes()
			self._recorreTablaMolde()
			self._insertaNuevoInventarioMoldes()
		except Exception as e:
			raise fd.excepciones.InventarioException(str(e) + ' - '+str(self._tabla_string))
		
	def _convierteFilasEnStringSeparadaPorComas(self):
		logger = system.util.getLogger('fila a string inventario')
		tabla_nueva = []
		logger.info('_tabla_entrada'+str(self._tabla_entrada))
		for fila in self._tabla_entrada:
			fila_nueva = fila.replace(";",",").split(",")
			logger.info('fila_nueva'+str(fila_nueva))
			tabla_nueva.append(fila_nueva)
		logger.info('tabla_nueva'+str(tabla_nueva))
		return tabla_nueva
		
	def _formateaTimeStamp(self, timestamp):
		return system.date.format(timestamp,"yyyy-MM-dd HH:mm:ss")
		
	def _asignaPosicionCabecera(self):
		try:
			self._idx_tag_id = self._tabla_string[0].index("TAG ID")
		except:
			self.__idx_tag_id = self._tabla_string[0].index("TAG")
			
		self._idx_rssi = self._tabla_string[0].index("RSSI")
		
		
	def _recorreTablaPlato(self):
		for fila in self._tabla_string[1:]:
			self._agregaFilaATablaInventarioSiEsValidaPlato(fila)
		self._uneValoresEnUnSoloString()
		
	def _recorreTablaMolde(self):
		
		for fila in self._tabla_string[1:]:
			self._agregaFilaATablaInventarioSiEsValidaMolde(fila)
		self._uneValoresEnUnSoloString()
		
		
	def _agregaFilaATablaInventarioSiEsValidaPlato(self, fila):
		id_tag = self._transformaTagIdDeHexToDec(str(fila[self._idx_tag_id]))
		rssi = int(fila[self._idx_rssi])
		
		if self._compruebaSiNoEsNuloYTieneLasDimensionesCorrectas(id_tag):
			nueva_fila = self._formateaNuevaFila(id_tag, rssi)
			self._tabla_inventario.append(nueva_fila)
				
	def _agregaFilaATablaInventarioSiEsValidaMolde(self, fila):
		indx_id_tag = str(fila[self._idx_tag_id])
		id_tag = self._db.ejecutaNamedQuery('FD/Inventario/ConsultaMolde', {"epc": indx_id_tag})
		
		rssi = int(fila[self._idx_rssi])
		if self._compruebaSiNoEsNuloYTieneLasDimensionesCorrectas(id_tag) and not (id_tag in self._id_tags_procesados):
			nueva_fila = self._formateaNuevaFila(id_tag, rssi)
			self._tabla_inventario.append(nueva_fila)
			self._id_tags_procesados.append(id_tag)
			
			
	def _filaNoEstaVacia(self, fila):
		return isinstance(fila, list) and ''.join(fila).strip() != ''
		
	def _eliminaFilasVaciasDeTablaEntrada(self):
		tabla_provisional=[]
		for fila in self._tabla_entrada:
			if self._filaNoEstaVacia(fila):
				tabla_provisional.append(fila)
		self._tabla_entrada =  tabla_provisional
		
	def _compruebaSiNoEsNuloYTieneLasDimensionesCorrectas(self, id_tag):
		return id_tag!=None and len(id_tag)==38 and id_tag[0] == self._prefijo_id
		
	def _transformaTagIdDeHexToDec(self, numero_serie):
		gestor_numero_serie = fd.numerosserie.NumeroSerie(numero_serie)
		numero_decimal = gestor_numero_serie.obtieneNumeroSerieDecimal()
		return numero_decimal
				
	def _formateaNuevaFila(self, id_tag, rssi):
		nueva_fila = "('%s','%s', '%s', %d, '%s')" % (id_tag, self._t_stamp, self._lugar, int(rssi), self._sublugar)
		return nueva_fila
		
	def _uneValoresEnUnSoloString(self):
		self._tabla_inventario = ",".join(self._tabla_inventario)
		
	def _eliminaInventarioAnterior(self, tabla):
		try: 
			self._db.ejecutaNamedQuery('FD/Inventario/EliminarInventario',{'tabla': tabla, 'lugar': self._lugar, 'sublugar': self._sublugar})
		except Exception as e:
			raise fd.excepciones.InventarioException('Error eliminando inventario antiguo' + str(e))
			
	def _eliminaInventarioAnteriorMoldes(self):
		try: 
			self._db.ejecutaNamedQuery('FD/Inventario/EliminarInventarioMoldes',{'tabla': self.TABLA_INVENTARIO_MOLDES})
		except Exception as e:
			raise fd.excepciones.InventarioException('Error eliminando inventario antiguo' + str(e))
		
	def _insertaNuevoInventario(self, tabla):
		params={"valores":self._tabla_inventario, "tabla": tabla}
		try:
			self._db.ejecutaNamedQuery('FD/Inventario/InstertarInventario',params)
		except Exception as e:
			raise fd.excepciones.InventarioException('Error insertando nuevo inventario' +str(e))
			
	def _insertaNuevoInventarioMoldes(self):
		params={"valores":self._tabla_inventario, "tabla": self.TABLA_INVENTARIO_MOLDES}
		try:
			self._db.ejecutaNamedQuery('FD/Inventario/InstertarInventarioMoldes',params)
		except Exception as e:
			raise fd.excepciones.InventarioException('Error insertando nuevo inventario' +str(e))