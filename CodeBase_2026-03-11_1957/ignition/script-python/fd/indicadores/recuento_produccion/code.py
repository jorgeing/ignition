class ReportadorProduccionGenerico(object):
	
	DatosTurno = fd.utilidades.turnoproduccion.DatosTurno
	
	_inicio_recuento = None
	_fin_recuento = None
	
	def __init__(self, timestamp_inicio_recuento, timestamp_fin_recuento):
		self._inicio_recuento = timestamp_inicio_recuento
		self._fin_recuento = timestamp_fin_recuento
		
	def obtieneRecuentoEnPeriodo():
		raise NotImplementedError()
		
	@staticmethod
	def obtieneDatasetRecuentoDiarioPorHoras(dia_produccion):
		raise NotImplementedError()
	
	
class ReportadorProduccionDesmoldeo(ReportadorProduccionGenerico):
	
	_id_linea = 0
	_db = None
	def __init__(self, timestamp_inicio_recuento, timestamp_fin_recuento, id_linea):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		super(ReportadorProduccionDesmoldeo, self).__init__(timestamp_inicio_recuento, timestamp_fin_recuento)
		self._id_linea = id_linea
	
	def obtieneRecuentoEnPeriodo(self):
		parametros = self._generaParametrosConsultaPlatosDesmoldeados(self._inicio_recuento, self._fin_recuento, self._id_linea)
		print(str(parametros))
		return self._db.ejecutaNamedQuery('FD/Platos/RecuentoPlatosDesmoldeados',parametros)
		
	@staticmethod
	def obtieneDatasetRecuentoDiarioPorHoras(dia_produccion):
		parametros = {'dia_produccion':dia_produccion}
		return self._db.ejecutaNamedQuery('FD/Platos/RecuentoPlatosDesmoldeadosDia', parametros)
		
		
	def _generaParametrosConsultaPlatosDesmoldeados(self, inicio_recuento, fin_recuento, id_linea):
		return {
			'id_linea':id_linea,
			'inicio':inicio_recuento,
			'fin':fin_recuento
		}