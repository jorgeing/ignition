class DecodificadorRequestDataRobusto:
	
	@staticmethod		
	def obtieneDatos(request):
		try:
			request_data = request["data"].tostring()
			request_data = system.util.jsonDecode(request_data)
		except:
			request_data = request["data"]
		return request_data

class RespuestaError:
	
	def __init__(self, request):
		self._request = request
		
	def contruyeRespuestaError(self, codigo_error_http, mensaje_error):
		self._request["servletResponse"].setStatus(codigo_error_http)
		respuesta_error={
			'response':mensaje_error
		}
		return (self._request, respuesta_error)