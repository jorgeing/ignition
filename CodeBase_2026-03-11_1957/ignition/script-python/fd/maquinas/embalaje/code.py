class AdaptadorEmbaladoraBase:
	
	_ancho = 0
	_largo = 0
	_produccion = 0
	_tipo_carton = -1
	
	def __init__(self, ancho, largo, produccion, tipo_carton):
		pass
	
	def obtieneAnchoCaja():
		raise NotImplementedError()
		
	def obtieneLargoCaja():
		raise NotImplementedError()
		
	def obtieneProduccionDiaria():
		raise NotImplementedError()
		
	def obtieneTipoCarton():
		raise NotImplementedError()
	

class AdaptadorEmbalitec(AdaptadorEmbaladoraBase):
	
	def __init__(self, path_udt_embalitec):
		pass

class AdaptadorTamegar(AdaptadorEmbaladoraBase):
	
	def __init__(self, path_udt_tamegar):
		pass

class Embaladora(AdaptadorEmbaladoraBase):
	#Recibe ancho, largo, nº cajas producidas, tipo cartón...
	
	
	
	def __init__(self, adaptador_maquina):
	
		self._ancho = adaptador_maquina.obtieneAnchoCaja()
		self._largo = adaptador_maquina.obtieneLargoCaja()
		self._produccion = adaptador_maquina.obtieneProduccionDiaria()
		self._tipo_carton = adaptador_maquina.obtieneTipoCarton()
		
	def registraCajaEnDB(self):
		pass
		
	
	