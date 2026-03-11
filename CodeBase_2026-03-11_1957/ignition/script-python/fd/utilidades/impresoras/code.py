class InformacionImpresoras:
	
	_printer_id = 0
	
	def __init__(self, printer_id):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._printer_id = printer_id
	
	def obtieneNombreImpresora(self):
		nombre_impresora = ''
		try:
			nombre_impresora = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneInformacionImpresora', {"printer_id": self._printer_id})
		except Exception as e:
			raise Exception('No se ha podido obtener informacion de la impresora: ' + str(e))
		return nombre_impresora[0]["printer_name"]
		
	def obtieneServidorImpresion(self):
		servidor = ''
		try:
			servidor = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneInformacionImpresora', {"printer_id": self._printer_id})
		except Exception as e:
			raise Exception('No se ha podido obtener informacion de la impresora: ' + str(e))
		return servidor[0]["printer_server"]
		
	def obtieneNombreImpresoraA4(self):
		impresora_a4 = ''
		try:
			nombre_impresora = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneInformacionImpresora', {"printer_id": self._printer_id})
		except Exception as e:
			raise Exception('No se ha podido obtener informacion de la impresora: ' + str(e))
		return nombre_impresora[0]["printer_a4"]


class InformacionPorNombreImpresoras:
	
	_nombre_impresora = ''
	
	def __init__(self, nombre_impresora):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._nombre_impresora = nombre_impresora
		
	def obtieneServidorImpresion(self):
		servidor = ''
		try:
			servidor = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneInfoPorNombreImpresora', {"printer_name": self._nombre_impresora})
		except Exception as e:
			raise Exception('No se ha podido obtener informacion de la impresora: ' + str(e))
		return servidor[0]["printer_server"].encode('ascii')
		



class ConfiguracionImpresoras:
	PATH_UDT = '[rfid_tags]Printers/configuracion_impresoras_dolores'
	_udt_configuracion_impresoras = {}
	
	def __init__(self):
		self._udt_configuracion_impresoras = system.tag.readBlocking(self.PATH_UDT)[0].value
		#self._logger = fd.utilidades.logger.LoggerFuncionesClase('ConfiguracionImpresoras')
		
	def obtieneImpresoraRFID(self, via):
		if via == 1:
			return self._udt_configuracion_impresoras["via1_impresora_rfid"]
		elif via == 2:
			return self._udt_configuracion_impresoras["via2_impresora_rfid"]
		else:
			return 'zebra_etiquetas_largas_dolores_110'
	
	def obtieneImpresoraAreaMoldes(self):
		return self._udt_configuracion_impresoras["area_moldes_impresora_rfid"]
		
	def obtieneImpresoraA4(self, impresora_envasado):
		impresora_a4 = InformacionImpresoras(impresora_envasado).obtieneNombreImpresoraA4()
		
		if self._esImpresoraDeEnvasa(impresora_a4):
			impresora_a4 = self._corrigeImpresoraEnvasaSegunSelector(impresora_a4)
		
		return impresora_a4
			
	def _corrigeImpresoraEnvasaSegunSelector(self, impresora_a4):
		selector_impresoras = fd.utilidades.tags.GestorTags.leeValorDeUnTag('[rfid_tags]Printers/selector_impresoras_envasa_a4')
		if selector_impresoras == 0:
			return impresora_a4
		elif selector_impresoras == 1:
			return self._udt_configuracion_impresoras["envasa_impresora_a4_1"]
		elif selector_impresoras == 2:
			return self._udt_configuracion_impresoras["envasa_impresora_a4_2"]
		
			
	def _esImpresoraDeEnvasa(self, nombre_impresora):
		if nombre_impresora:
			return 'envasadora' in nombre_impresora
		else:
			return False