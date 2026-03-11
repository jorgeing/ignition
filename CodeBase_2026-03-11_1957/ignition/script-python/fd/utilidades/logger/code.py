
class LoggerBase:	
	_nombreBaseLogger = ""
	
	def __init__(self, nombreBaseLogger):
		self._nombreBaseLogger	= nombreBaseLogger
		
	def obtieneLoggerEstandarizado(self, nombreFuncion):
		return LoggerEstandarizado(self._nombreBaseLogger, nombreFuncion)
		
class LoggerEstandarizado:
	
	LOG_DEBUG=0
	IGNORA_DEBUG=1
	
	_logger = None
	_nombreFuncion = ""
	_loggeaDebug = IGNORA_DEBUG
	
	def __init__(self, nombreBase, nombreFuncion):
		self._logger= system.util.getLogger(nombreBase)
		self._nombreFuncion = nombreFuncion
		
	def activaLogDebug(self):
		self._loggeaDebug = self.LOG_DEBUG
	
	def desactivaLogDebug(self):
		self._loggeaDebug = self.IGNORA_DEBUG
			
	def logDebug(self, msg):
		if self._loggeaDebug == self.LOG_DEBUG:
			self._logger.info("[debug/"+self._nombreFuncion+"]: " + str(msg))
			
	def logInfo(self, msg):
		self._logger.info("["+self._nombreFuncion+"]: "+ str(msg))
	
	def logWarning(self, msg):
		self._logger.warn("["+self._nombreFuncion+"]: "+ str(msg))
		
	def logError(self, msg):
		self._logger.error("["+self._nombreFuncion+"]: "+ str(msg))
		
class LoggerFuncionesClase:
	
	LOG_DEBUG=0
	IGNORA_DEBUG=1
	
	_logger = None
	_loggeaDebug = IGNORA_DEBUG
	
	def __init__(self, nombreBase):
		self._logger= system.util.getLogger(nombreBase)
		
	def activaLogDebug(self):
		self._loggeaDebug = self.LOG_DEBUG
	
	def desactivaLogDebug(self):
		self._loggeaDebug = self.IGNORA_DEBUG
			
	def logDebug(self, msg):
		if self._loggeaDebug == self.LOG_DEBUG:
			self._logger.info("[debug/"+self._obtieneNombreFuncion()+"]: " + str(msg))
			
	def logInfo(self, msg):
		self._logger.info("["+self._obtieneNombreFuncion()+"]: "+ str(msg))
	
	def logWarning(self, msg):
		self._logger.warn("["+self._obtieneNombreFuncion()+"]: "+ str(msg))
		
	def logError(self, msg):
		self._logger.error("["+self._obtieneNombreFuncion()+"]: "+ str(msg))
		
	def _obtieneNombreFuncion(self):
		nombre_funcion = sys._getframe(1).f_code.co_name
		return nombre_funcion