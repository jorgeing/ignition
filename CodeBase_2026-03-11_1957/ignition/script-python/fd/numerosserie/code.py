class NumeroSerie:
	
	_numero_serie_entrada = ""
	_numero_serie_dec = ""
	_numero_serie_hex = ""
	
	def __init__(self,numero_serie):
		if numero_serie == None:
			numero_serie = ''
		self._numero_serie_entrada = numero_serie
		self._rellenaNumerosSerieHexYDec()
		
		
	def obtieneNumeroSerieDecimal(self):
		return self._numero_serie_dec
		
	def obtieneNumeroSerieHexadecimal(self):
		return self._numero_serie_hex
		
	def esPlato(self):
		return self.obtieneNumeroSerieDecimal()[0]=='1'
		
	def esMolde(self):
		return self.obtieneNumeroSerieDecimal()[0]=='2'
		
	def _rellenaNumerosSerieHexYDec(self):
		if self._numeroEntradaEsDecimal():
			self._numero_serie_dec = self._numero_serie_entrada
			self._numero_serie_hex = NumeroSerie._decToHexId(self._numero_serie_entrada)
		elif self._numeroEntradaEsHexadecimal():
			self._numero_serie_hex = self._numero_serie_entrada
			self._numero_serie_dec = NumeroSerie._hexToDecId(self._numero_serie_entrada)
		else:
			raise fd.excepciones.NumeroSerieException(self._numero_serie_entrada)
	
	def _numeroEntradaEsDecimal(self):
		return len(self._numero_serie_entrada) == 38 and self._numero_serie_entrada.isdigit()
		
	def _numeroEntradaEsHexadecimal(self):
	    return len(self._numero_serie_entrada) == 32 and self._numeroEntradaSoloContieneCaracteresHexadecimales()
	    
	def _numeroEntradaSoloContieneCaracteresHexadecimales(self):
		caracteres_hexadecimales = "0123456789abcdefABCDEF"
		for caracter in self._numero_serie_entrada:
			if caracter not in caracteres_hexadecimales:
				return False
		return True
	
	@staticmethod
	def _decToHexId(dec_id):
		hex_id=''
		if dec_id:
			num_most=int(dec_id[0:19])
			num_least=int(dec_id[19:])
			num_most_hex=hex(num_most)[2:-1].zfill(16).upper()
			num_least_hex=hex(num_least)[2:-1].zfill(16).upper()
			hex_id=num_most_hex+num_least_hex
		return hex_id
		
	@staticmethod
	def _hexToDecId(hex_id):
		if hex_id:
			hex_id = hex_id.zfill(32)
			num_most=int(hex_id[0:16],16)
			num_least=int(hex_id[16:],16)
			num_str_most=str(num_most).zfill(19)
			num_str_least=str(num_least).zfill(19)
			return num_str_most+num_str_least
		else:
			return ''

class GeneradorNumeroSerie:
	
	TIPO_NUMERO_SERIE_PLATO = 1
	TIPO_NUMERO_SERIE_MOLDE = 2
	TIPO_NUMERO_SERIE_PANEL = 3
	TIPO_NUMERO_SERIE_CAJA = 4
	
	
	_id_color = 0
	_id_cliente = 0
	_tipo_numero_serie =0
	_numero_molde= 0
	_id_modelo = 0
	_dimension = 0
	
	_numero_serie = ''
	
	
	def __init__(self, tipo_numero_serie, id_cliente, numero_molde, id_color, id_modelo, dimension):
		
		
		self._tipo_numero_serie = tipo_numero_serie
		self._id_cliente = id_cliente
		self._numero_molde = numero_molde
		self._id_color = id_color
		self._id_modelo = id_modelo
		self._dimension = dimension
		
		self._numero_serie = self._creaNumeroSerie()
		
	def obtieneNumeroSerie(self):
		return self._numero_serie
		
	def _creaNumeroSerie(self):
		
		fecha = self._obtieneSeccionFechaNumeroSerie()
		cliente = self._obtieneSeccionClienteNumeroSerie()
		lugar = self._obtieneSeccionLugarNumeroSerie()
		numero_molde = self._obtieneSeccionNumeroMoldeNumeroSerie()
		color =  self._obtieneSeccionColorNumeroSerie()
		dimensiones_molde = self._obtieneSeccionDimensionesNumeroSerie()
		modelo_molde = self._obtieneSeccionModeloNumeroSerie()
		
		numero_serie_cabeza = str(self._tipo_numero_serie)+fecha+cliente+lugar
		numero_serie_cola = numero_molde + color + modelo_molde + dimensiones_molde
		
		numero_serie = numero_serie_cabeza.zfill(19)+numero_serie_cola.zfill(19)
		
		return numero_serie
		
	def _obtieneSeccionFechaNumeroSerie(self):
		return system.date.format(system.date.now(),'yyyyMMddHHmmss')[2:]
		
	def _obtieneSeccionClienteNumeroSerie(self):
		return str(self._id_cliente).zfill(5)
		
	def _obtieneSeccionLugarNumeroSerie(self):
		place = fd.globales.ParametrosGlobales.obtieneIdFabrica()
		return str(place).zfill(1)
		
	def _obtieneSeccionNumeroMoldeNumeroSerie(self):
		return str(self._numero_molde).zfill(4)
	
	def _obtieneSeccionColorNumeroSerie(self):
		return str(self._id_color).zfill(6)
		
	def _obtieneSeccionModeloNumeroSerie(self):
		return str(self._id_modelo).zfill(3)
		
	def _obtieneSeccionDimensionesNumeroSerie(self):
		return str(self._dimension).zfill(6)



class GeneradorNumeroSeriePlato(GeneradorNumeroSerie):
	
	@staticmethod
	def construyeDesdeMolde(id_molde, id_cliente, id_color):
		
		numero_molde = GeneradorNumeroSeriePlato._obtieneNumeroMolde(id_molde)
		id_modelo = GeneradorNumeroSeriePlato._obtieneModelo(id_molde)
		dimension = GeneradorNumeroSeriePlato._obtieneDimension(id_molde)
		
		return GeneradorNumeroSeriePlato(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_PLATO, id_cliente, numero_molde, id_color, id_modelo, dimension
			)
			
	@staticmethod
	def contruyeDesdeSku(sku, id_cliente, largo, ancho):
		
		numero_molde = 0
		id_color = 0000
		dimensiones = 000000
		id_modelo = 0
		
		if fd.sku.ManejadorSku(sku).esSkuDekor():
			id_color = 9003
			dimensiones = GeneradorNumeroSeriePlato._obtieneDimensionDekor(largo, ancho)
			id_modelo = 1
		else:
			id_color = GeneradorNumeroSeriePlato._obtieneColorSku(sku)
			dimensiones = GeneradorNumeroSeriePlato._obtieneDimensionesSku(sku)
			id_modelo = GeneradorNumeroSeriePlato._obtieneModeloSku(sku)
		
		return GeneradorNumeroSeriePlato(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_PLATO, id_cliente, numero_molde, id_color, id_modelo, dimensiones
			)
	
	@staticmethod
	def _obtieneNumeroMolde(id_molde):
		final_molde = id_molde[19:]
		return final_molde[0:4]
	
	@staticmethod
	def _obtieneModelo(id_molde):
		final_molde = id_molde[19:]
		return final_molde[-9:-6]
	
	@staticmethod
	def _obtieneDimension(id_molde):
		final_molde = id_molde[19:]
		return final_molde[-6:]
		
	@staticmethod
	def _obtieneColorSku(sku):
		return sku[9:13]
		
	@staticmethod
	def _obtieneDimensionesSku(sku):
		return sku[3:9]
		
	@staticmethod
	def _obtieneModeloSku(sku):
		
		modelo = sku[:3]
		id_modelo = GeneradorNumeroSeriePlato._obtieneModeloNumericoSku(modelo)
		return id_modelo
		
	@staticmethod
	def _obtieneModeloNumericoSku(modelo):
		db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		id_modelo = db.ejecutaNamedQuery('FD/Platos/ModeloDeSku', {"sku_name": modelo})
		return id_modelo[0]["id"]
		
	@staticmethod
	def _obtieneDimensionDekor(largo, ancho):
		largo_nomralizado = str(largo).zfill(3)
		ancho_normalizado = str(ancho).zfill(3)
		return largo_nomralizado+ancho_normalizado
		
class GeneradorNumeroSerieMolde(GeneradorNumeroSerie):
	
	@staticmethod
	def construyeDesdeIdModeloYDimension(id_modelo, largo, ancho, numero_molde):
		dimensiones = str(largo).zfill(3)+str(ancho).zfill(3)
		return GeneradorNumeroSerieMolde(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_MOLDE, 0, numero_molde, 0, id_modelo, dimensiones
			)
	
	@staticmethod
	def construyeDesdeSKU(sku, id_cliente, id_color):
		pass
		
	def _obtieneSeccionFechaNumeroSerie(self):
		return str('').zfill(12)

class GeneradorNumeroSerieResiblock(GeneradorNumeroSerie):
	
	def _obtieneSeccionFechaNumeroSerie(self):
		return '00000000'

class GeneradorNumeroSerieEtiquetaMolde(GeneradorNumeroSerie):
	
	@staticmethod
	def construyeDesdeMolde(id_modelo, largo, ancho, numero_molde):
		dimensiones = str(largo).zfill(3)+str(ancho).zfill(3)
		id_cliente = GeneradorNumeroSerieEtiquetaMolde._obtieneSeccionClienteNumeroSerie()
		return GeneradorNumeroSerieEtiquetaMolde(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_MOLDE, id_cliente, numero_molde, 0, id_modelo, dimensiones
			)
	
	@staticmethod
	def construyeDesdeSKU(sku, id_cliente, id_color):
		pass
	
	@staticmethod
	def _obtieneSeccionClienteNumeroSerie():
		fecha_actual = system.date.now()
		milis = system.date.getMillis(fecha_actual)
		milis_formateado = str(milis).zfill(5)
		return milis_formateado