class RespuestaApiEntradaMolde:
	
	def __init__(self, request):
		self._request = request
		
	def contruyeRespuesta(self, es_valida, info_rfid, info_orden):
	
		
		respuesta = {'json':{
					'mold_id':info_rfid.obtieneIdMolde(),
					'production_order':info_orden.obtieneIdOrdenDetallada(),
					'sku':info_orden.obtieneSku(), 
					'color':info_orden.obtieneIdColor(),
					'is_valid':es_valida, 'inclination_time':4, 
					'model_id':info_rfid.obtieneIdModelo(), 
					'mold_length':info_rfid.obtieneLongitudMolde(), 
					'mold_width':info_rfid.obtieneAnchoMolde(), 
					'mold_number':info_rfid.obtieneNumeroMolde(), 
					'codcli':info_orden.obtieneIdCliente()}
					}
					
		return (self._request, respuesta)