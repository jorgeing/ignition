class IntegracionOperario:
	
	@staticmethod
	def existeOperario(worker_id):
		try:
			db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
			result = db.ejecutaNamedQuery('FD/Utilidades/IntegracionOperario/ExisteOperario', {"worker_id":worker_id})
			return result.getRowCount()>0
			
		except:
			logger = system.util.getLogger('existeWorkerIntegrationInfo')
			logger.warn('No se ha podido leer la base de datos RFID para obtener información del worker_id: ' + str(worker_id))
			return False
		
	@staticmethod
	def obtieneInformacionOperario(worker_id):
		info ={'warehouse':'1', 'erp_integration':True}
		try:
			db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
			result = db.ejecutaNamedQuery('FD/Utilidades/IntegracionOperario/ObtieneAlmacenIntegracionOperario', {"worker_id":worker_id})
			if (result):
				info = result[0]
		except:
			logger = system.util.getLogger('getWorkerIntegrationInfo')
			logger.warn('No se ha podido leer la base de datos RFID para obtener información del worker_id: ' + str(worker_id))
		return info