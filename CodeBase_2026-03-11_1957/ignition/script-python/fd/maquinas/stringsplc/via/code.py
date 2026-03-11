class StringsComunicacionPlc:
	
	@staticmethod
	def procesaStringColorMoldeOrden(stringplc):
		logger = system.util.getLogger("procesaStringColorMoldeOrden")
		partes = stringplc.split(',')
		color = partes[0]
		uuid = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal.convierteUuidHexadecimalEnDecimal(partes[2].zfill(16)+partes[1].zfill(16))
		prod_order_plc=""
		try:
			prod_order_plc = partes[3]
		except:
			logger.warn("Error obteniendo orden de: " + str(stringplc))
			prod_order_plc = ""
		datos_creacion = {'mold_id':uuid, 'color_id':int(color), 'production_order_id': prod_order_plc}
		return datos_creacion