import time

class CreadorEtiquetasMoldeNuevo:
	CICLOS_LIMPIEZA = 30
	RUTA_ASIGNA_ETIQUETAS = 'FD/Moldes/AsignaEtiquetasAMolde'
	
	_bbdd = None
	
	def __init__(self, id_modelo, largo, ancho, numero_etiquetas = 4):
		self._id_modelo = id_modelo
		self._largo = largo
		self._ancho = ancho
		self._numero_etiquetas = numero_etiquetas
		self._creador_molde = fd.gestionmoldes.creacionmoldes.CreadorMoldes(id_modelo, largo, ancho, self.CICLOS_LIMPIEZA)
		self._bbdd = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		self._logger = self._logger = fd.utilidades.logger.LoggerFuncionesClase('CreadorEtiquetasMoldeNuevo')
	
	def creaMoldeYAsignaEtiquetas(self):
		try:
			self._bbdd.iniciaTransaccion(system.db.SERIALIZABLE, 1000)
			self._creaMoldeNuevo()
			self._gestionaEtiquetasMoldeNuevo()
			self._bbdd.commitTransaccion()
			self._logger.logInfo("Etiquetas de molde creadas y asiganadas correctamente: "+self._id_etiqueta_hex)
			print("Etiquetas de molde creadas y asiganadas correctamente: "+ self._id_etiqueta_hex)
			return self._id_molde_nuevo, self._numero_molde_nuevo
		except Exception as e:
			self._logger.logError(str(e))
			print(str(e))
			self._bbdd.rollbackTransaccion()
	
	def _creaMoldeNuevo(self):
		self._id_molde_nuevo, self._numero_molde_nuevo = self._creador_molde.creaYRegistraMoldeUsandoEtiquetas()
	
	def _gestionaEtiquetasMoldeNuevo(self):
		for i in range(self._numero_etiquetas):
			time.sleep(0.005)
			self._creaEtiquetasMoldeNuevo()
			self._asignaEtiquetasAMoldeNuevo()
			self._imprimeEtiquetasMoldeNuevo()
	
	def _creaEtiquetasMoldeNuevo(self):
		generador_numero_serie_etiquetas_molde = fd.numerosserie.GeneradorNumeroSerieEtiquetaMolde.construyeDesdeMolde(
				self._id_modelo,
				self._largo, 
				self._ancho, 
				self._numero_molde_nuevo)
		
		numero_serie_etiqueta_molde = generador_numero_serie_etiquetas_molde.obtieneNumeroSerie()
		
		self._id_etiqueta_dec = numero_serie_etiqueta_molde
		print(self._id_etiqueta_dec)
		self._id_etiqueta_hex = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal.convierteUuidDecimalEnHexadecimal(numero_serie_etiqueta_molde)
	
	def _asignaEtiquetasAMoldeNuevo(self):
		params={'id_molde':self._id_molde_nuevo,
				'id_etiqueta_hex':self._id_etiqueta_hex}
		print(str(params))
		self._bbdd.ejecutaNamedQuery(self.RUTA_ASIGNA_ETIQUETAS, params)
	
	def _imprimeEtiquetasMoldeNuevo(self):
		fd.moduloetiquetas.servicioetiquetado.EtiquetasAreaMoldes(self._id_molde_nuevo, self._id_etiqueta_dec)

class CreadorEtiquetasMoldeExistente:
	
	RUTA_ASIGNA_ETIQUETAS = 'FD/Moldes/AsignaEtiquetasAMolde'
	RUTA_OBTIENE_ID_MOLDE = 'FD/Moldes/ObtieneIdMolde'
	
	_bbdd = None
	
	def __init__(self, numero_molde, id_modelo, largo, ancho, cantidad_etiquetas):
		self._numero_molde = numero_molde
		self._id_modelo = id_modelo
		self._largo = largo
		self._ancho = ancho
		self._cantidad_etiquetas = cantidad_etiquetas
		self._bbdd = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		self._logger = self._logger = fd.utilidades.logger.LoggerFuncionesClase('CreadorEtiquetasMoldeExistente')
	
	def creaYAsignaEtiquetaAMolde(self):
		try:
			self._bbdd.iniciaTransaccion(system.db.SERIALIZABLE, 1000)
			self._gestionaEtiquetasMoldeExistente()
			self._bbdd.commitTransaccion()
			self._logger.logInfo("Etiquetas de molde creadas y asiganadas correctamente: "+self._id_etiqueta_hex)
			print("Etiquetas de molde creadas y asiganadas correctamente: "+ self._id_etiqueta_hex)
		except Exception as e:
			self._logger.logError(str(e))
			print(str(e))
			self._bbdd.rollbackTransaccion()
	
	def _gestionaEtiquetasMoldeExistente(self):
		self._obtieneIdMoldeExistente()
		for i in range(self._cantidad_etiquetas):
			time.sleep(0.005)
			self._creaEtiquetasMoldeExistente()
			self._asignaEtiquetasAMoldeExistente()
			self._imprimeEtiquetasMoldeExistente()
	
	def _obtieneIdMoldeExistente(self):
		params={'id_modelo':self._id_modelo,
				'numero_molde':self._numero_molde,
				'largo':self._largo,
				'ancho':self._ancho}
		self._id_molde = self._bbdd.ejecutaNamedQuery(self.RUTA_OBTIENE_ID_MOLDE, params)
	
	def _creaEtiquetasMoldeExistente(self):
		generador_numero_serie_etiquetas_molde = fd.numerosserie.GeneradorNumeroSerieEtiquetaMolde.construyeDesdeMolde(
				self._id_modelo,
				self._largo, 
				self._ancho, 
				self._numero_molde)
		
		numero_serie_etiqueta_molde = generador_numero_serie_etiquetas_molde.obtieneNumeroSerie()
		
		self._id_etiqueta_dec = numero_serie_etiqueta_molde
		print(self._id_etiqueta_dec)
		self._id_etiqueta_hex = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal.convierteUuidDecimalEnHexadecimal(numero_serie_etiqueta_molde)
	
	def _asignaEtiquetasAMoldeExistente(self):
		params={'id_molde':self._id_molde,
				'id_etiqueta_hex':self._id_etiqueta_hex}
		print(str(params))
		self._bbdd.ejecutaNamedQuery(self.RUTA_ASIGNA_ETIQUETAS, params)
	
	def _imprimeEtiquetasMoldeExistente(self):
		fd.moduloetiquetas.servicioetiquetado.EtiquetasAreaMoldes(self._id_molde, self._id_etiqueta_dec)