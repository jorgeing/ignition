class ConversoresDecimalHexadecimal:
	
	@staticmethod
	def convierteUuidDecimalEnHexadecimal(uuid_dec):
		uuid_dec = uuid_dec.zfill(38)
		id_inicio = ConversoresDecimalHexadecimal._obtienePrimerosDigitosDecimales(uuid_dec)
		id_final = ConversoresDecimalHexadecimal._obtieneUltimosDigitosDecimales(uuid_dec)
		
		id_inicio_hex = hex(id_inicio)[2:-1].zfill(16).upper()
		id_final_hex = hex(id_final)[2:-1].zfill(16).upper()
		
		return id_inicio_hex+id_final_hex
		
	@staticmethod
	def convierteUuidHexadecimalEnDecimal(uuid_hex):
		uuid_hex = uuid_hex.zfill(32)
		id_inicio_hex = ConversoresDecimalHexadecimal._obtienePrimerosDigitosHexadecimales(uuid_hex)
		id_final_hex = ConversoresDecimalHexadecimal._obtieneUltimosDigitosHexadecimales(uuid_hex)
		
		id_inicio_dec=int(id_inicio_hex,16)
		id_final_dec=int(id_final_hex,16)
		
		id_inicio_str=str(id_inicio_dec).zfill(19)
		id_final_str=str(id_final_dec).zfill(19)
		
		return id_inicio_str+id_final_str
	
	@staticmethod
	def _obtienePrimerosDigitosDecimales(uuid):
		return long(uuid[:19])
		
	@staticmethod
	def _obtieneUltimosDigitosDecimales(uuid):
		return long(uuid[19:])
		
	@staticmethod
	def _obtienePrimerosDigitosHexadecimales(uuid):
		return uuid[:16]
		
	@staticmethod
	def _obtieneUltimosDigitosHexadecimales(uuid):
		return uuid[16:]
		