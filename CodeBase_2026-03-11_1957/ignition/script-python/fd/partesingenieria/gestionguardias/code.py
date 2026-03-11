from datetime import date, timedelta

class PlanificadorGuardias:
	
	def __init__(self):
		self._lista_ingenieros = self._obtieneIngenierosEnActivo()
	
	def planificaSemanasGuardiaMensual(self):
		inicio, fin = self._calculaPeriodoGuardias()
	
	def _calculaPeriodoGuardias(self):
		fecha_actual = system.date.now()
		mes_actual = system.date.getMonth(fecha_actual)
		anyo_actual = system.date.getYear(fecha_actual)
		
		if mes_actual == 12:
			anyo_siguiente = anyo_actual + 1
			mes_siguiente = 1
		else:
			anyo_siguiente = anyo_actual
			mes_siguiente = mes_actual + 1
		
		inicio = system.date.getDate(anyo_actual, mes_actual, 20)
		fin = system.date.getDate(anyo_siguiente, mes_siguiente, 20)
		
		return inicio, fin