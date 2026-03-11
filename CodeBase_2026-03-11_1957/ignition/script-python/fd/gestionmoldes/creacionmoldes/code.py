class CreadorMoldes:
	
	_bbdd=None
	
	
	def __init__(self, id_modelo, largo, ancho, ciclos_entre_limpiezas):
		self._id_modelo = id_modelo
		self._largo = largo
		self._ancho = ancho
		self._ciclos_entre_limpiezas = ciclos_entre_limpiezas
		self._id_fabrica = fd.globales.ParametrosGlobales.obtieneIdFabrica()
		
		self._bbdd = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		self._logger = self._logger = fd.utilidades.logger.LoggerFuncionesClase('CreadorMoldes')
		
	def creaYRegistraMoldeUsandoEtiquetas(self):
		try:
			self._bbdd.iniciaTransaccion(system.db.SERIALIZABLE, 1000)
			self._creaNumeroSerie()
			self._registraMoldeSinEpc()
			self._bbdd.commitTransaccion()
			self._logger.logInfo("Molde creado correctamente: "+self._dec_id)
			return self._dec_id, self._numero_molde
		except Exception as e:
			self._logger.logError(str(e))
			self._bbdd.rollbackTransaccion()
		
	def _creaNumeroSerie(self):
		self._numero_molde = self._obtieneUltimoNumeroMolde()
		
		generador_numero_serie_molde = 	fd.numerosserie.GeneradorNumeroSerieMolde.construyeDesdeIdModeloYDimension(
				self._id_modelo,
				self._largo, 
				self._ancho, 
				self._numero_molde)
		
		numero_serie_molde = generador_numero_serie_molde.obtieneNumeroSerie()
		
		self._dec_id=numero_serie_molde
		self._hex_id=fd.utilidades.transformaciones.ConversoresDecimalHexadecimal.convierteUuidDecimalEnHexadecimal(numero_serie_molde)
		
	def _registraMoldeSinEpc(self):
		mold_params={'id_molde_dec':self._dec_id,'id_molde_hex':self._hex_id, 
			'id_modelo':self._id_modelo, 
			'numero_molde':self._numero_molde,
			'largo':self._largo,
			'ancho':self._ancho, 
			'id_fabrica':self._id_fabrica,
			'ciclos_entre_limpiezas':self._ciclos_entre_limpiezas}
		print(mold_params)
		self._bbdd.ejecutaNamedQuery('FD/Moldes/RegistraMoldeSinTags',mold_params)
		
	def _obtieneUltimoNumeroMolde(self):
		number_params={'place_id':self._id_fabrica, 'model_id':self._id_modelo, 'length':self._largo, 'width':self._ancho}
		last_number = self._bbdd.ejecutaNamedQuery('FD/Moldes/ObtieneUltimoNumeroMolde',number_params)
		mold_number=int(last_number)+1
		print(last_number)
		return mold_number