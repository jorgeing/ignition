from com.inductiveautomation.ignition.common.model import ApplicationScope

class ScriptScope:
	SCOPE_CLIENTE = 'c'
	SCOPE_DESIGNER = 'd'
	SCOPE_GATEWAY = 'g'
	SCOPE_PERSPECTIVE = 'p'
	SCOPE_DESCONOCIDO = 'u'
	
	@staticmethod
	def getScope():
		scope = ApplicationScope.getGlobalScope()
		if ApplicationScope.isClient(scope):
			return ScriptScope.SCOPE_CLIENTE
	
		if ApplicationScope.isDesigner(scope):
			return ScriptScope.SCOPE_DESIGNER
	
		if ApplicationScope.isGateway(scope):
			if "perspective" in dir(system):
				return ScriptScope.SCOPE_PERSPECTIVE
			return ScriptScope.SCOPE_GATEWAY
		return ScriptScope.SCOPE_DESCONOCIDO
