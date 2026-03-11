class manejoRequestCorte:
	
	def __init__(self, request):
		try:
			self._showertray_id = request['showertray_id']
			self._cut_length = request['cut_length']
			self._cut_width = request['cut_width']
			self._sales_order = request['sales_order_id']
			self._scanner_id = request['scanner_id']
			self._client_number = request['client_id']
			self._worker_id = request['worker_id']
			self._sku = request['sku']
			self._impresora = request['rfid_printer_name'] #modificar porque ya no es RFID
			self._production_order_id = request.get['production_order_id']
			self._frame_options = request.get['frame_options']
			
			self._place_id =  fd.globales.ParametrosGlobales.obtieneIdFabrica()
			
		except Exception as e:
			raise Exception('Error obteniendo datos: ' + str(e))
			
		if not self._compruebaIntegridadDatos():
			raise Exception("Datos incompletos o invalidos en el request")
			
	def obtieneDiccionario(self):
		return {
			"showertray_id": self._showertray_id,
			"cut_length": self._cut_length,
			"cut_width": self._cut_width,
			"sales_order": self._sales_order,
			"scanner_id": self._scanner_id,
			"client_number": self._client_number,
			"worker_id": self._worker_id,
			"sku": self._sku,
			"impresora": self._impresora,
			"production_order_id": self._production_order_id,
			"frame_options": self._frame_options,
			"place_id": self._place_id
			}


class manejoRequestEscaneo:
	
	def __init__(self, request):
		try:
			self._showertray_id = request['params']['showertray_id']
			self._worker_id = request['params']['worker_id']
			self._dekor = self._compruebaDekor(request)
		except Exception as e:
			raise Exception('Request invalido: ' + str(e))
			
		if not self._compruebaIntegridadDatos():
			raise Exception("Datos incompletos o invalidos en el request")
		
	def obtieneDiccionario(self):
		return {
			"showertray_id": self._showertray_id,
			"worker_id": self._worker_id,
			"dekor": self._dekor
			}
		
	def _compruebaDekor(self, request):
		params = request.get('params', {})
		return params.get('dekor') == True
			
	def _compruebaIntegridadDatos(self):
		return (
			self._showertray_id is not None and self._showertray_id != '' and
			self._worker_id is not None and self._worker_id != ''
			)




