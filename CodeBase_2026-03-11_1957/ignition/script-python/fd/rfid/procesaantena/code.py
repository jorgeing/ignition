class ProcesadorAntena():
	"""Procesa las lecturas RFID de una antena, clasificando los tags en moldes y etiquetas."""

	_nombre_antena = ''
	_json_antena = ''
	_objeto_destino_inicial = {}
	_objeto_destino = {}
	
	_estado_antena = False
	_lista_moldes=[]
	_lista_etiquetas=[]
	_lista_rfid_interior=[]
	
	_lista_moldes_inicial = []
	_lista_etiquetas_inicial = []
	_lista_rfid_interior_inicial = []
	
	_buscador_moldes = None
	_conversor_hex_dec = None
	_logger = None
	
	def __init__(self, nombre_antena, json_lectura_antena, objeto_destino_inicial, utiliza_string_plano = False):
		"""Inicializa el procesador de antena cargando los datos de lectura y el historial previo."""
		self._buscador_moldes = fd.gestionmoldes.consultamoldes.BuscadorMoldes()
		self._conversor_hex_dec = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal()
		self._logger = fd.utilidades.logger.LoggerFuncionesClase("ProcesadorAntena")
		
		self._nombre_antena = nombre_antena
		
		if utiliza_string_plano:
			self._extraeStringAntena(json_lectura_antena)
		else:
			self._extraeJsonAntena(json_lectura_antena)
			
		self._objeto_destino_inicial = objeto_destino_inicial
		
		self._intentaObtenerListasIniciales()
			
	
	def procesaDatosAntena(self):
		"""Procesa los datos de la antena y devuelve el objeto resultado con moldes, etiquetas y RFID interior."""
		self._identificaYGeneraListaMoldes()
		self._identificaYGeneraListaEtiquetas()
		self._identificaYGeneraListaRfidInterior()
		self._construyeObjetoDestino()
		return self._objeto_destino

	def _extraeJsonAntena(self, json_lectura_antena):
		"""Extrae la lista de EPCs y el estado de la antena desde un objeto JSON o diccionario."""
		json_lectura_antena = dict(json_lectura_antena)
		try:
			if json_lectura_antena.has_key("lista_epc"):
				self._json_antena=json_lectura_antena["lista_epc"]
				self._estado_antena = int(json_lectura_antena["estado_antena"])
		except Exception as e:
			self._logger.logWarning("Error extrayendo Json: " + str(e))
			self._json_antena = json_lectura_antena
			self._estado_antena = 3 #De momento si no llega en el json, siempre es correcto (3)
			
	def _extraeStringAntena(self, json_lectura_antena):
		"""Extrae la lista de EPCs y el estado de la antena desde una cadena delimitada por ';'."""
		timestamp = system.date.now()
		separados = json_lectura_antena.split(";")
		self._estado_antena = int(separados[0])
		id_lectura = 0
		lista_epc_dict = []
		for elemento in separados[1:]:
			if len(elemento)>0:
				dict_elemento={
					"id":"lectura_"+str(id_lectura),
					"rssi": 40,
					"epc":elemento,
					"timestamp":timestamp
				}
				id_lectura = id_lectura+1
				lista_epc_dict.append(dict_elemento)
		self._json_antena = lista_epc_dict

	def _identificaYGeneraListaMoldes(self):
		"""Identifica los tags de moldes en la lectura y genera la lista procesada de moldes."""
		self._lista_moldes = self._identificaTagsYGeneraListado(self._obtieneIdMolde, self._lista_moldes_inicial )
		
	def _identificaYGeneraListaEtiquetas(self):
		"""Identifica los tags de etiquetas en la lectura y genera la lista procesada de etiquetas."""
		self._lista_etiquetas = self._identificaTagsYGeneraListado(self._obtieneIdEtiqueta, self._lista_etiquetas_inicial )
		
	def _identificaYGeneraListaRfidInterior(self):
		"""Identifica y genera la lista de tags RFID interior. Pendiente de implementar."""
		#A Implementar
		pass
		
	def _identificaTagsYGeneraListado(self, funcion_identificacion, lista_tags_procesados_inicial):
		"""Identifica tags usando la función proporcionada y genera el listado procesado con estadísticas."""
		tags_identificados =[]
		for tag in self._json_antena:
			id_tag = funcion_identificacion(tag)
			if id_tag:
				tag_extendido = self._extiendeTagConId(tag, id_tag)
				tags_identificados.append(tag_extendido)	
		listado_procesado = self._procesaDatosTags(tags_identificados, lista_tags_procesados_inicial)
		return listado_procesado
		
	def _extiendeTagConId(self, tag,id_tag):
		"""Crea una copia extendida del tag añadiendo el campo 'id' con el identificador obtenido."""
		tag_extendido = dict(tag)
		tag_extendido["id"]=id_tag
		return tag_extendido
		
	def _obtieneIdMolde(self,tag):
		"""Obtiene el identificador del molde correspondiente al EPC del tag, si existe."""
		return self._buscador_moldes.obtieneIdMoldePorEpc(tag['epc'])
		
	def _obtieneIdEtiqueta(self, tag):
		"""Obtiene el identificador decimal de la etiqueta si el EPC corresponde a una etiqueta válida."""
		id_etiqueta = None
		epc_dec = self._conversor_hex_dec.convierteUuidHexadecimalEnDecimal(tag['epc'])
		if self._idDecimalEsEtiqueta(epc_dec):
			id_etiqueta = epc_dec
		return id_etiqueta
		
	def _idDecimalEsEtiqueta(self, id_etiqueta):
		"""Verifica si un identificador decimal cumple el criterio de ser una etiqueta válida."""
		return id_etiqueta[0]=='1' and len(id_etiqueta)==38
		
	def _procesaDatosTags(self, lista_tags_procesar, lista_tags_procesados_inicial):
		"""Agrupa y procesa los tags detectados acumulando estadísticas de lecturas, RSSI y timestamps."""
		tags_procesados = []
		for tag in lista_tags_procesar:
			tag = self._preprocesarTag(tag)
			encontrado = False
			for i in range(len(tags_procesados)):
				if tag["id"]==tags_procesados[i]["id"]:
					encontrado=True
					tag_procesado_inicial = self._encuentraTagEnListaTagsProcesadosInicial(tag, lista_tags_procesados_inicial)
					tag_procesado_actualizado={
						"id":tag["id"],
						"tag_count":tags_procesados[i]["tag_count"]+1,
						"min_rssi":tag["rssi"] if tag["rssi"]<tags_procesados[i]["min_rssi"] else tags_procesados[i]["min_rssi"],
						"max_rssi":tag["rssi"] if tag["rssi"]>tags_procesados[i]["max_rssi"] else tags_procesados[i]["max_rssi"],
						"last_read":tag["timestamp"],
						"first_read":tag["timestamp"] if tag_procesado_inicial == None else tag_procesado_inicial["first_read"],
					}
					tags_procesados[i]= tag_procesado_actualizado
					break
			if not encontrado:
				tags_procesados.append({
					'id':tag["id"],
					'tag_count':1,
					'max_rssi':tag["rssi"],
					'min_rssi':tag["rssi"],
					'last_read':tag["timestamp"],
					'first_read':tag["timestamp"]
				})
		tags_procesados_ordenados = sorted(tags_procesados, key=lambda x: x['max_rssi'], reverse=True)
		return tags_procesados_ordenados
		
	def _encuentraTagEnListaTagsProcesadosInicial(self, tag, lista_tags_procesados_inicial):
		"""Busca y devuelve el registro previo del tag en la lista inicial de tags procesados."""
		for tag_procesado in lista_tags_procesados_inicial:
			if tag["id"] == tag_procesado["id"]:
				return tag_procesado	
		return None
	
	def _preprocesarTag(self,tag):
		"""Normaliza el valor RSSI del tag al rango con signo y actualiza su timestamp."""
		tag["rssi"]=tag["rssi"]-256 if tag["rssi"]>127 else tag["rssi"]
		tag["timestamp"]=system.date.format(system.date.now(),'yyyy-MM-dd HH:mm:ss')
		return tag
	
	def _intentaObtenerListasIniciales(self):
		"""Intenta cargar las listas iniciales de moldes, etiquetas y RFID interior desde el objeto destino."""
		try:
			self._lista_moldes_inicial = self._objeto_destino_inicial["molds"]
			self._lista_etiquetas_inicial = self._objeto_destino_inicial["labels"]
			self._lista_rfid_interior_inicial = self._objeto_destino_inicial["rfid_interior"]
		except:
			self._logger.logWarning("El objeto de destino no tiene los listados, inicializando...")
			self._lista_moldes_inicial = []
			self._lista_etiquetas_inicial = []
			self._lista_rfid_interior_inicial = []
	
	def _construyeObjetoDestino(self):
		"""Construye el objeto resultado final con todas las listas procesadas y metadatos de la antena."""
		self._objeto_destino={
			'now':system.date.now(),
			'name': self._nombre_antena,
			'estado_antena_ok': self._estado_antena==3,
			'molds':self._lista_moldes,
			'labels':self._lista_etiquetas,
			'rfid_interior':self._lista_rfid_interior
		}
		