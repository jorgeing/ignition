import random

class EventoAsignacionRFIDDentroDelPlato:
	"""Gestiona la asignación de chips RFID al interior del plato durante el proceso de producción."""
	
	ANTENA_1_RFID = 'rfid_preasignado_1'
	ANTENA_2_RFID = 'rfid_preasignado_2'
	ANTENA_3_RFID = 'rfid_preasignado_3'
	ANTENA_FIN_RFID = 'rfid_id_interior'
	
	ANTENA_1_RSSI = 'rssi_1'
	ANTENA_2_RSSI = 'rssi_2'
	ANTENA_3_RSSI = 'rssi_3'
	ANTENA_FIN_RSSI = 'rssi_interior'
	
	ANTENA_1_TIEMPO = 't_stamp_preasignado_1'
	ANTENA_2_TIEMPO = 't_stamp_preasignado_2'
	ANTENA_3_TIEMPO = 't_stamp_preasignado_3'
	ANTENA_FIN_TIEMPO = 't_stamp'
	
	_info_tag = ''
	_rfid_id_interior = ''
	_antena = 0
	_columna_rfid_id = ''
	_columna_rssi = ''
	_columna_t_stamp = ''
	_rssi = -99
	
	def __init__(self, info_tag, antena):
		"""Inicializa con info del tag y número de antena."""
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._logger = fd.utilidades.logger.LoggerFuncionesClase('trigger_antena_test')
		self._info_tag = info_tag
		self._rfid_id_interior = self._info_tag['rfid_id_interior']
		self._rfid_id_interior_anterior = self._info_tag['rfid_id_interior_anterior']
		self._rssi = self._info_tag['rfid_interior_rssi']
		self._antena = antena
		self._asignaQueAntenaMandaLaPeticion(antena)
		
	def guardaRFIDparaPlato(self):
		"""Guarda/asigna el RFID al plato si es válido y diferente al anterior."""
		if self._rfid_id_interior != '' and self._rfid_id_interior != None and self._rfid_id_interior != self._rfid_id_interior_anterior:
			self._logger.logInfo("Intenta asignar - update: "+ self._rfid_id_interior+ ' - ' +str(self._info_tag['mold_id']))
			asignado = self._asignaRFID()
			if asignado == 0:
				self._logger.logInfo("no consigue update, hace insert: "+ self._rfid_id_interior+ ' - ' +str(self._info_tag['mold_id']))
				self._reservaRFIDparaPlato()
			
			self.verificaLosChipsGuardados()
			
	def verificaLosChipsGuardados(self):
		"""Verifica que los chips RFID almacenados sean coherentes."""
		valores_rfid = self._obtieneRFIDGuardados()
		self._compruebaSiSonIguales(valores_rfid)
			
	def _asignaQueAntenaMandaLaPeticion(self, antena):
		"""Determina qué columnas usar según la antena activa."""
		if antena == 1:
			self._columna_rfid_id = self.ANTENA_1_RFID
			self._columna_rssi = self.ANTENA_1_RSSI
			self._columna_t_stamp = self.ANTENA_1_TIEMPO
			
		elif antena == 2:
			self._columna_rfid_id = self.ANTENA_2_RFID
			self._columna_rssi = self.ANTENA_2_RSSI
			self._columna_t_stamp = self.ANTENA_2_TIEMPO
			
		elif antena == 3:
			self._columna_rfid_id = self.ANTENA_3_RFID
			self._columna_rssi = self.ANTENA_3_RSSI
			self._columna_t_stamp = self.ANTENA_3_TIEMPO
			
		elif antena == 4:
			self._columna_rfid_id = self.ANTENA_FIN_RFID
			self._columna_rssi = self.ANTENA_FIN_RSSI
			self._columna_t_stamp = self.ANTENA_FIN_TIEMPO
			
		elif antena == 9999:
			self._columna_rfid_id = self.ANTENA_1_RFID
			self._columna_rssi = self.ANTENA_1_RSSI
			self._columna_t_stamp = self.ANTENA_1_TIEMPO
		
	def _reservaRFIDparaPlato(self):
		"""Inserta un nuevo registro RFID para el plato."""
		parametros = self._generaParametrosReserva()
		print('_reservaRFIDparaPlato '+str(parametros))
		self._logger.logInfo('_reservaRFIDparaPlato '+str(parametros))
		self._db.ejecutaNamedQuery('FD/Platos/ReservaRFIDInternoAPlato', parametros)
		
	def _generaParametrosReserva(self):
		"""Genera el diccionario de parámetros para la reserva."""
		parametros= {
			"columna_rfid_id": str(self._columna_rfid_id),
			"columna_t_stamp": str(self._columna_t_stamp),
			"columna_rssi": str(self._columna_rssi),
			"showertray_id": str(self._info_tag['showertray_id']),
			"rfid_preasignado": str(self._rfid_id_interior),
			"mold_id": str(self._info_tag['mold_id']),
			"rssi": self._rssi
			}
		return parametros
	
	def _asignaRFID(self):
		"""Ejecuta la query de asignación de RFID al plato."""
		parametros = self._generaParametrosAsignacion()
		self._logger.logInfo('_asignaRFID '+str(parametros))
		print('_asignaRFID '+str(parametros))
		asignado = self._db.ejecutaNamedQuery('FD/Platos/AsignaRFIDInternoAPlato', parametros)
		return asignado
		
	def _generaParametrosAsignacion(self):
		"""Genera el diccionario de parámetros para la asignación."""
		parametros= {
			"columna_rfid_id": str(self._columna_rfid_id),
			"columna_t_stamp": str(self._columna_t_stamp),
			"rfid_id_interior": str(self._rfid_id_interior),
			"columna_rssi": str(self._columna_rssi),
			"rssi": self._rssi,
			"showertray_id": str(self._info_tag['showertray_id']),
			"mold_id": str(self._info_tag['mold_id'])
			}
		return parametros
		
	def _obtieneRFIDGuardados(self):
		"""Obtiene los RFIDs preasignados desde la base de datos."""
		return self._db.ejecutaNamedQuery('FD/Platos/ObtieneInformarcionRfidPreasignados', {"showertray_id": str(self._info_tag['showertray_id'])})
		
	def _compruebaSiSonIguales(self, valores_rfid):
		"""Comprueba si hay chips duplicados y los consolida."""
		rfid_1 = valores_rfid[0]['rfid_preasignado_1']
		rfid_2 = valores_rfid[0]['rfid_preasignado_2']
		rfid_3 = valores_rfid[0]['rfid_preasignado_3']
		#print(str(valores_rfid[0]['rfid_preasignado_2']) +'=='+ str(valores_rfid[0]['rfid_preasignado_3']))
		if ((rfid_1 == rfid_2 or rfid_1 == rfid_3) and rfid_1 is not None) or (rfid_2 == rfid_3 and rfid_2 is not None):
			self._asignaQueAntenaMandaLaPeticion(4)
			self._asignaRFID()





class ValidacionValorTag:
	"""Valida si un valor de tag RFID es válido para ser asignado."""
	
	CONDICION_INICIO = 'E2801191'
	#'E2801191'
	
	_epc_leido = ''
	_showertray_id = ''
	
	def __init__(self, epc_leido):
		"""Inicializa con el EPC leído y limpia ceros iniciales."""
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._epc_leido = self._eliminaCerosIniciales(epc_leido)
		
	def esRFIDValido2(self, showertray_id):
		"""Verifica si el RFID existe en BD y no ha sido ya asignado."""
		self._showertray_id = showertray_id
		respuesta = False
		if self.existeEnLaBBDD() and self._noHaSidoYaAsignado():
			respuesta = True
		else: 
			respuesta = False
		return respuesta
		
	def existeEnLaBBDD(self):
		"""Comprueba si el EPC existe en la tabla de RFIDs autogenerados."""
		existe = self._db.ejecutaNamedQuery('FD/Platos/RfidInteriorAutogenerado', {"id_hexadecimal": self._epc_leido})
		if existe:
			return True
		else:
			return False
		
	def _eliminaCerosIniciales(self, epc_leido):
		"""Elimina los ceros del inicio del EPC."""
		return epc_leido.lstrip('0')
		
	def _convierteHexadecimalDecimal(self):
		"""Convierte el EPC hexadecimal a decimal."""
		id_decimal = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal.convierteUuidHexadecimalEnDecimal(self._epc_leido)
		return id_decimal.lstrip('0')
		
	def _noHaSidoYaAsignado(self):
		"""Verifica que el chip no haya sido ya asignado a otro plato."""
		existe = self._db.ejecutaNamedQuery('FD/Platos/CompruebaSiYaExisteChip', {"rfid_id_interior": self._epc_leido, "showertray_id": self._showertray_id})
		if len(existe) == 0:
			return True
		else:
			return False
		
		
		
	#BORRAR TRAS PRUEBAS
	def esRFIDValido(self):
		"""Valida el RFID (método antiguo, pendiente de borrar)."""
		respuesta = False
		if self._formatoEpcCorrecto() and self._esConsistente() and self._validacionCRC() and self._esChipUnico():
			respuesta = True
		else: 
			respuesta = False
		return respuesta
		
	def _formatoEpcCorrecto(self):
		"""Verifica que el EPC tenga 24 caracteres."""
		if len(self._epc_leido) == 24:
			return True
		
	def _esConsistente(self):
		"""Verifica que el EPC empiece con el prefijo esperado."""
		if self._epc_leido[0:8] == self.CONDICION_INICIO:
			return True
			
	def _validacionCRC(self):
		"""Realiza validación CRC (actualmente siempre True)."""
		return True
		
	def _esChipUnico(self):
		"""Verifica que el chip no exista ya en la BD."""
		existe = self._db.ejecutaNamedQuery('FD/Platos/CompruebaSiYaExisteChip', {"rfid_id_interior": self._epc_leido, "showertray_id": self._showertray_id})
		print(str(existe))
		if len(existe) == 0:
			return True
			

class AsignadorRFIDInterior:
	"""Asignador estático de RFID interior al plato."""
	
	@staticmethod
	def asignaSiValido(path, showertray_id):
		"""Lee el tag y devuelve el EPC si es válido y tiene buen RSSI."""
		try:
			tag = fd.utilidades.tags.GestorTags.leeValorDeUnTag(path)
			print('tag: '+str(tag))
			try:
				epc = tag["labels"][0]["id"]
			except:
				epc = ''
			print('epc: '+str(epc))
			rssi_ok = AsignadorRFIDInterior.compruebaRSSI(tag)
			validador = fd.rfidinteriorplato.ValidacionValorTag(epc, showertray_id)
			es_valido = validador.esRFIDValido2()
			if es_valido and rssi_ok:
				print('es_valido: '+str(es_valido))
				return epc 
			else:
				return ''
		except:
			return ''
				
	@staticmethod
	def siValidoGuardaRssi(path, showertray_id):
		"""Lee el tag y devuelve el RSSI si es válido."""
		try:
			tag = fd.utilidades.tags.GestorTags.leeValorDeUnTag(path)
			try:
				epc = tag["labels"][0]["id"]
				rssi = tag["labels"][0]["min_rssi"]
				print('epc: '+str(epc)+' rssi: '+str(rssi))
			except:
				epc = ''
				rssi = -99
			rssi_ok = AsignadorRFIDInterior.compruebaRSSI(tag)
			validador = fd.rfidinteriorplato.ValidacionValorTag(epc, showertray_id)
			es_valido = validador.esRFIDValido2()
			print('rssi_ok: '+str(rssi_ok)+' es_valido: '+str(es_valido))
			if es_valido and rssi_ok:
				print('es_valido: '+str(es_valido))
				print(str(rssi))
				return rssi 
			else:
				return -99
		except:
			return -99
	
	@staticmethod
	def compruebaRSSI(tag):
		"""Verifica que el RSSI del tag supere el umbral mínimo."""
		rssi = tag["labels"][0]["min_rssi"]
		if rssi > -60:
			return True


class InformacionParaLaAntena:
	"""Genera la respuesta JSON para la antena RFID."""
	
	TYPE_STRING = 'label'
	_epc_leido = ''
	
	def __init__(self, epc_leido):
		"""Inicializa con el EPC leído."""
		self._epc_leido = epc_leido
		
	def generaJson(self):
		"""Genera el JSON de respuesta con el EPC."""
		return {'code':200,'message':'OK', 'IDHex':self._epc_leido, 'IDDec':self._epc_leido, 'type':self.TYPE_STRING}
		
		
class GeneradorUID: #TEMPORAL PRUEBA
	"""Generador temporal de UIDs para pruebas."""
	
	@staticmethod
	def generaUID():
		"""Genera un UID único basado en fecha y número aleatorio."""
		fecha_actual = system.date.now()
		lote = system.date.format(fecha_actual, 'ddMMyy')
		numero_aleatorio = random.randint(10**26, 10**27 - 1)
		intermedio = str(8)+str(lote)+str(numero_aleatorio)
		comprobacion = 8 + int(lote) + numero_aleatorio
		crc = int(comprobacion)%10000
		uiid = intermedio + str(crc)
		return uiid
		
	@staticmethod
	def compruebaCRC(uiid):
		"""Verifica el CRC de un UID generado."""
		numero_serie = uiid[:34]
		suma_numero_serie = int(numero_serie[0]) + int(numero_serie[1:7]) + int(numero_serie[7:])
		crc = uiid[34:]
		if int(suma_numero_serie)%10000 == int(crc):
			return True
		return int(numero_serie)%10000
		


#Final para generar codificación
class GeneradorCodificacionRfid:
	"""Genera codificaciones RFID únicas e inserta en BD."""
	
	_IDENTIFICADOR_INICIAL = 8
	
	_cantidad_uuid = 0
	_lote = ''
	_indice_mayor = 0
	_secuencia_numerica = []
	_lista_suma_numeros_intermedios = []
	
	_uuid_final_dec = []
	_uuid_final_hex = []
	
	
	def __init__(self, cantidad):
		"""Inicializa generando el lote y la secuencia numérica."""
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._cantidad_uuid = cantidad
		self._lote = self._obtieneLote()
		self._indice_mayor = self._compruebaSiLoteYaEstaCreado()
		self._secuencia_numerica = self._generaSecuenciaNumerica()
		self._secuencia_numerica = self._rellenaConZeros()
		
		
	def generaUuidUnico(self):
		"""Genera UUIDs únicos en decimal y hexadecimal y los inserta en BD."""
		uuid_semielaborado = self._generaNumeroIntermedio()
		lista_crc = self._generaCRC()
		
		self._uuid_final_dec = [uuid + str(crc) for uuid, crc in zip(uuid_semielaborado, lista_crc)]
		self._uuid_final_hex = self._transformaUuidListaEnHExadecimal()
		
		lista_final = self._juntaListasParaInsertar()
		dataset_lista_final = self._convierteEnDataset(lista_final)
		try:
			inserta_en_base_datos = self._insertaEnBaseDatos(dataset_lista_final)
			
		except:
			raise fd.excepciones.CreacionCodificacionEInstert('Error creando codificacion ' + str(e))
		
		return self._uuid_final_dec
		
		
	@staticmethod
	def sumaUnoAleatoriamente(lista_uuids):
		"""Suma uno aleatoriamente a un dígito del UUID y verifica el CRC."""
		for uuid in lista_uuids:
			numero_serie = list(uuid[:14])
			crc_original = list(uuid[14:])
			
			indice_aleatorio = random.randint(0,13)
			
			nuevo_digito = (int(numero_serie[indice_aleatorio]) + 1) % 10
			numero_serie[indice_aleatorio] = str(nuevo_digito)
			
			nuevo_numero_serie = ''.join(numero_serie)
			suma_numero_serie =  int(nuevo_numero_serie[0]) + int(nuevo_numero_serie[1:7]) + int(nuevo_numero_serie[7:])
			nuevo_crc = suma_numero_serie%10000
			
			if nuevo_crc != crc_original:
				return False
		return True
		
		
	def _obtieneLote(self):
		"""Obtiene el identificador de lote a partir de la fecha actual."""
		fecha_actual = system.date.now()
		return system.date.format(fecha_actual, 'yyMMdd')
		
		
	def _compruebaSiLoteYaEstaCreado(self):
		"""Obtiene el índice mayor del lote en BD para continuar la secuencia."""
		indice_mayor = self._db.ejecutaNamedQuery('FD/Rfid/CompruebaSiExisteLote', {"lote": self._lote})
		if len(indice_mayor) > 0:
			return indice_mayor[0][0]
		else:
			return 0
			
			
	def _generaSecuenciaNumerica(self):
		"""Genera una secuencia de índices consecutivos."""
		return [int(self._indice_mayor) + 1 + i for i in range(self._cantidad_uuid)]
		
		
	def _rellenaConZeros(self):
		"""Rellena los números con ceros hasta 7 dígitos."""
		return [str(numero).zfill(7) for numero in self._secuencia_numerica]
		
		
	def _generaNumeroIntermedio(self):
		"""Genera el número intermedio base del UUID."""
		self._lista_suma_numeros_intermedios = [int(self._IDENTIFICADOR_INICIAL)+int(self._lote)+ int(numero) for numero in self._secuencia_numerica]
		return [str(self._IDENTIFICADOR_INICIAL)+str(self._lote)+ numero for numero in self._secuencia_numerica]
		
		
	def _generaCRC(self):
		"""Calcula el CRC para cada elemento de la secuencia."""
		return [int(secuencia)%10000 for secuencia in self._lista_suma_numeros_intermedios]
		
		
	def _transformaUuidListaEnHExadecimal(self):
		"""Convierte la lista de UUIDs decimales a hexadecimal."""
		resultados = []
		conversor_hexadecimal = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal
		
		for uuid in self._uuid_final_dec:
			id_hexadecimal = conversor_hexadecimal.convierteUuidDecimalEnHexadecimal(uuid)
			id_hexadecimal_sin_ceros = id_hexadecimal.lstrip('0')
			resultados.append(id_hexadecimal_sin_ceros)
		return resultados
		
		
	def _obtieneListaLote(self):
		"""Genera una lista con el lote repetido para cada UUID."""
		lista_lote = []
		for fila in range(self._cantidad_uuid):
			lista_lote.append(self._lote)
		return lista_lote
		
	def _obtieneListaSerie(self):
		"""Genera una lista con los índices de serie para cada UUID."""
		lista_serie = []
		if self._indice_mayor > 0:
			serie = self._indice_mayor + 1
		else:
			serie = 1
		
		for fila in range(self._cantidad_uuid):
			lista_serie.append(serie)
			serie = serie + 1
		return lista_serie
		
	def _obtieneListaTimeStamp(self):
		"""Genera una lista con el timestamp actual para cada UUID."""
		lista_tstamp = []
		hoy = system.date.now()
		for fila in range(self._cantidad_uuid):
			lista_tstamp.append(hoy)
		return lista_tstamp
		
	def _juntaListasParaInsertar(self):
		"""Combina todas las listas en una lista final para insertar."""
		lista_final = []
		fila_total = []
		lista_lote = self._obtieneListaLote()
		lista_serie = self._obtieneListaSerie()
		lista_tstamp = self._obtieneListaTimeStamp()
		
		for fila in range(self._cantidad_uuid):
			fila_total.extend([self._uuid_final_dec[fila], self._uuid_final_hex[fila], lista_lote[fila], lista_serie[fila], lista_tstamp[fila]])
			lista_final.append(fila_total)
			fila_total = []
			
		return lista_final
		
		
	def _convierteEnDataset(self, lista_final):
		"""Convierte la lista final en un dataset de Ignition."""
		cabecera = ["id_dec", "id_hex", "lote", "indice_serie", "t_stamp"]
		dataset = system.dataset.toDataSet(cabecera, lista_final)
		return dataset
		
		
	def _insertaEnBaseDatos(self, dataset_lista_final):
		"""Inserta el dataset en la base de datos."""
		string_valores_a_insertar = self._mapeoColumnas(dataset_lista_final)
		
		params = {'values': string_valores_a_insertar}
		self._db.ejecutaNamedQuery('FD/Rfid/InsertaUuidsEnTabla',params)
		
		
	def _mapeoColumnas(self, dataset):
		"""Genera el string SQL de valores para inserción masiva."""
		pydataset = system.dataset.toPyDataSet(dataset)
		constructor_sql = fd.utilidades.sql.ConstructorSQL
		
		mapeo_columnas_tipo = [
			constructor_sql.creaMapeo('id_dec', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('id_hex', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('lote', constructor_sql.TIPO_COLUMNA_TEXTO),
			constructor_sql.creaMapeo('indice_serie', constructor_sql.TIPO_COLUMNA_NUMERO),
			constructor_sql.creaMapeo('t_stamp', constructor_sql.TIPO_COLUMNA_FECHA)
		]
		
		filas_insertar = constructor_sql.generaStringValoresParaInsertMasivo(pydataset, mapeo_columnas_tipo)
		return filas_insertar
		
		