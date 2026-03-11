class EstadosMaquina:
	
	_id_maquina = ''
	_db = None
	def __init__(self, id_maquina):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._id_maquina = id_maquina
		self._estados
	def devuelveEstadosMaquina(self):
		self._estados = self._db.ejecutaNamedQuery('FD/Supervision/ObtieneEstadosMaquina', {"maquina":self._id_maquina})
		#return estados
		
	def devuelveEstadoActual(self):
		pass