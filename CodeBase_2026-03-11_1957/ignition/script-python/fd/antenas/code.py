class GestionAntenas:
	
	_mold_id = ''
	
	def __init__(self, mold_id):
		self._mold_id = mold_id
		
	def buscaPlatoDentroDelMolde(self):
		return fd.moldes.Molde(self._mold_id).obtieneShowertrayDentroDelMolde()
		
	#def 
	
class GestionAntenasAsignacionRfiInterior:
	_info_tag = []
	_info_tag_anterior = []
	
	def __init__(self, info_tag, info_tag_anterior):
		self._info_tag = info_tag
		self._info_tag_anterior = info_tag_anterior
		
	def asignaRfidInterior(self, antena):
		if self._moldeORfidHaCambiado() and self._datosNoSonVacios():
			gestor_asignacion = fd.rfidinteriorplato.EventoAsignacionRFIDDentroDelPlato(self._info_tag, antena)
			gestor_asignacion.guardaRFIDparaPlato()
		
	def _obtieneMoldeYRfidInterior(self):
		self._rfid_id_interior = self._info_tag["rfid_id_interior"]
		self._mold_id = self._info_tag["mold_id"]
		
	def _obtieneMoldeYRfidInteriorAnterior(self):
		self._rfid_id_interior_anterior = self._info_tag_anterior["rfid_id_interior"]
		self._mold_id_anterior = self._info_tag_anterior["mold_id"]
		
	def _moldeORfidHaCambiado(self):
		return self._rfid_id_interior != self._rfid_id_interior_anterior or self._mold_id != self._mold_id_anterior
		
	def _datosNoSonVacios(self):
		return self._rfid_id_interior != '' and self._mold_id != ''