class ComprobadorEstadoBartender:
	
	_host = ''
	_puerto = '0'
	
	def __init__(self, ip_o_nombre_host, puerto = 9081):
		self._host = ip_o_nombre_host
		self._puerto = str(puerto)
		
	def esOk(self):
		url = "http://"+self._host+":"+self._puerto+"/Integration/estado_servidor/Execute"
		try:
			resp = system.net.httpPost(url,'text')
			return True
		except:
			return False