class CronometroTareas:
	
	_lista_eventos = []
	
	def __init__(self):
		self._lista_eventos=[]
		self.registraEvento("Inicio")
		
	def registraEvento(self, nombre_evento):
		evento={
			"nombre":nombre_evento,
			"timestamp":system.date.now()
		}
		self._lista_eventos.append(evento)
		
	def listaEventos(self):
		for i in range(len(self._lista_eventos)):
			evento_con_duracion = self._lista_eventos[i]
			evento_con_duracion["duracion"]= system.date.millisBetween(self._lista_eventos[i-1]["timestamp"], self._lista_eventos[i]["timestamp"])
			self._lista_eventos[i] = evento_con_duracion
			
		return self._lista_eventos