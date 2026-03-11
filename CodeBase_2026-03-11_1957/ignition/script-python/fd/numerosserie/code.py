class NumeroSerie:
	"""Clase que representa un número de serie RFID, permitiendo conversión entre formato decimal y hexadecimal."""
	
	_numero_serie_entrada = ""
	_numero_serie_dec = ""
	_numero_serie_hex = ""
	
	def __init__(self,numero_serie):
		"""Inicializa el número de serie a partir de un valor en formato decimal o hexadecimal.

		Args:
			numero_serie (str): Número de serie en formato decimal (38 dígitos) o hexadecimal (32 caracteres).

		Raises:
			fd.excepciones.NumeroSerieException: Si el número de serie no tiene un formato válido.
		"""
		if numero_serie == None:
			numero_serie = ''
		self._numero_serie_entrada = numero_serie
		self._rellenaNumerosSerieHexYDec()
		
		
	def obtieneNumeroSerieDecimal(self):
		"""Retorna el número de serie en formato decimal.

		Returns:
			str: Número de serie en formato decimal de 38 dígitos.
		"""
		return self._numero_serie_dec
		
	def obtieneNumeroSerieHexadecimal(self):
		"""Retorna el número de serie en formato hexadecimal.

		Returns:
			str: Número de serie en formato hexadecimal de 32 caracteres.
		"""
		return self._numero_serie_hex
		
	def esPlato(self):
		"""Indica si el número de serie corresponde a un plato.

		Returns:
			bool: True si el número de serie pertenece a un plato, False en caso contrario.
		"""
		return self.obtieneNumeroSerieDecimal()[0]=='1'
		
	def esMolde(self):
		"""Indica si el número de serie corresponde a un molde.

		Returns:
			bool: True si el número de serie pertenece a un molde, False en caso contrario.
		"""
		return self.obtieneNumeroSerieDecimal()[0]=='2'
		
	def _rellenaNumerosSerieHexYDec(self):
		"""Rellena los atributos de número de serie decimal y hexadecimal a partir del valor de entrada.

		Raises:
			fd.excepciones.NumeroSerieException: Si el número de serie de entrada no tiene un formato válido.
		"""
		if self._numeroEntradaEsDecimal():
			self._numero_serie_dec = self._numero_serie_entrada
			self._numero_serie_hex = NumeroSerie._decToHexId(self._numero_serie_entrada)
		elif self._numeroEntradaEsHexadecimal():
			self._numero_serie_hex = self._numero_serie_entrada
			self._numero_serie_dec = NumeroSerie._hexToDecId(self._numero_serie_entrada)
		else:
			raise fd.excepciones.NumeroSerieException(self._numero_serie_entrada)
	
	def _numeroEntradaEsDecimal(self):
		"""Verifica si el número de serie de entrada tiene formato decimal válido.

		Returns:
			bool: True si el número de entrada tiene 38 dígitos decimales, False en caso contrario.
		"""
		return len(self._numero_serie_entrada) == 38 and self._numero_serie_entrada.isdigit()
		
	def _numeroEntradaEsHexadecimal(self):
	    """Verifica si el número de serie de entrada tiene formato hexadecimal válido.

	    Returns:
	        bool: True si el número de entrada tiene 32 caracteres hexadecimales, False en caso contrario.
	    """
	    return len(self._numero_serie_entrada) == 32 and self._numeroEntradaSoloContieneCaracteresHexadecimales()
	    
	def _numeroEntradaSoloContieneCaracteresHexadecimales(self):
		"""Verifica si todos los caracteres del número de serie de entrada son hexadecimales.

		Returns:
			bool: True si todos los caracteres son válidos en base hexadecimal, False en caso contrario.
		"""
		caracteres_hexadecimales = "0123456789abcdefABCDEF"
		for caracter in self._numero_serie_entrada:
			if caracter not in caracteres_hexadecimales:
				return False
		return True
	
	@staticmethod
	def _decToHexId(dec_id):
		"""Convierte un identificador en formato decimal a formato hexadecimal.

		Args:
			dec_id (str): Número de serie en formato decimal de 38 dígitos.

		Returns:
			str: Número de serie en formato hexadecimal de 32 caracteres, o cadena vacía si dec_id es falso.
		"""
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
		"""Convierte un identificador en formato hexadecimal a formato decimal.

		Args:
			hex_id (str): Número de serie en formato hexadecimal de 32 caracteres.

		Returns:
			str: Número de serie en formato decimal de 38 dígitos, o cadena vacía si hex_id es falso.
		"""
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
	"""Clase base para la generación de números de serie RFID según el tipo de elemento."""
	
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
		"""Inicializa el generador de número de serie con los parámetros del elemento a identificar.

		Args:
			tipo_numero_serie (int): Tipo de elemento (plato, molde, panel, caja).
			id_cliente (int): Identificador del cliente.
			numero_molde (int): Número del molde.
			id_color (int): Identificador del color.
			id_modelo (int): Identificador del modelo.
			dimension (str): Dimensiones del elemento.
		"""
		
		
		self._tipo_numero_serie = tipo_numero_serie
		self._id_cliente = id_cliente
		self._numero_molde = numero_molde
		self._id_color = id_color
		self._id_modelo = id_modelo
		self._dimension = dimension
		
		self._numero_serie = self._creaNumeroSerie()
		
	def obtieneNumeroSerie(self):
		"""Retorna el número de serie generado.

		Returns:
			str: Número de serie en formato decimal de 38 dígitos.
		"""
		return self._numero_serie
		
	def _creaNumeroSerie(self):
		"""Construye el número de serie concatenando las distintas secciones.

		Returns:
			str: Número de serie completo en formato decimal de 38 dígitos.
		"""
		
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
		"""Retorna la sección de fecha del número de serie en formato YYMMDDHHmmss.

		Returns:
			str: Cadena de 12 caracteres con la fecha y hora actuales.
		"""
		return system.date.format(system.date.now(),'yyyyMMddHHmmss')[2:]
		
	def _obtieneSeccionClienteNumeroSerie(self):
		"""Retorna la sección del cliente en el número de serie, con relleno de ceros.

		Returns:
			str: Identificador del cliente formateado a 5 dígitos.
		"""
		return str(self._id_cliente).zfill(5)
		
	def _obtieneSeccionLugarNumeroSerie(self):
		"""Retorna la sección del lugar (fábrica) en el número de serie.

		Returns:
			str: Identificador de la fábrica formateado a 1 dígito.
		"""
		place = fd.globales.ParametrosGlobales.obtieneIdFabrica()
		return str(place).zfill(1)
		
	def _obtieneSeccionNumeroMoldeNumeroSerie(self):
		"""Retorna la sección del número de molde en el número de serie, con relleno de ceros.

		Returns:
			str: Número de molde formateado a 4 dígitos.
		"""
		return str(self._numero_molde).zfill(4)
	
	def _obtieneSeccionColorNumeroSerie(self):
		"""Retorna la sección del color en el número de serie, con relleno de ceros.

		Returns:
			str: Identificador del color formateado a 6 dígitos.
		"""
		return str(self._id_color).zfill(6)
		
	def _obtieneSeccionModeloNumeroSerie(self):
		"""Retorna la sección del modelo en el número de serie, con relleno de ceros.

		Returns:
			str: Identificador del modelo formateado a 3 dígitos.
		"""
		return str(self._id_modelo).zfill(3)
		
	def _obtieneSeccionDimensionesNumeroSerie(self):
		"""Retorna la sección de dimensiones en el número de serie, con relleno de ceros.

		Returns:
			str: Dimensiones del elemento formateadas a 6 dígitos.
		"""
		return str(self._dimension).zfill(6)



class GeneradorNumeroSeriePlato(GeneradorNumeroSerie):
	"""Generador especializado de números de serie para platos, hereda de GeneradorNumeroSerie."""
	
	@staticmethod
	def construyeDesdeMolde(id_molde, id_cliente, id_color):
		"""Construye un generador de número de serie de plato a partir de los datos de un molde.

		Args:
			id_molde (str): Identificador del molde en formato decimal de 38 dígitos.
			id_cliente (int): Identificador del cliente.
			id_color (int): Identificador del color.

		Returns:
			GeneradorNumeroSeriePlato: Instancia configurada con los datos del molde.
		"""
		
		numero_molde = GeneradorNumeroSeriePlato._obtieneNumeroMolde(id_molde)
		id_modelo = GeneradorNumeroSeriePlato._obtieneModelo(id_molde)
		dimension = GeneradorNumeroSeriePlato._obtieneDimension(id_molde)
		
		return GeneradorNumeroSeriePlato(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_PLATO, id_cliente, numero_molde, id_color, id_modelo, dimension
			)
			
	@staticmethod
	def contruyeDesdeSku(sku, id_cliente, largo, ancho):
		"""Construye un generador de número de serie de plato a partir de un SKU de producto.

		Args:
			sku (str): Código SKU del producto.
			id_cliente (int): Identificador del cliente.
			largo (int): Largo del plato en milímetros.
			ancho (int): Ancho del plato en milímetros.

		Returns:
			GeneradorNumeroSeriePlato: Instancia configurada con los datos del SKU.
		"""
		
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
		"""Extrae el número de molde a partir del identificador del molde.

		Args:
			id_molde (str): Identificador del molde en formato decimal de 38 dígitos.

		Returns:
			str: Número de molde extraído (4 caracteres).
		"""
		final_molde = id_molde[19:]
		return final_molde[0:4]
	
	@staticmethod
	def _obtieneModelo(id_molde):
		"""Extrae el identificador del modelo a partir del identificador del molde.

		Args:
			id_molde (str): Identificador del molde en formato decimal de 38 dígitos.

		Returns:
			str: Identificador del modelo extraído (3 caracteres).
		"""
		final_molde = id_molde[19:]
		return final_molde[-9:-6]
	
	@staticmethod
	def _obtieneDimension(id_molde):
		"""Extrae las dimensiones a partir del identificador del molde.

		Args:
			id_molde (str): Identificador del molde en formato decimal de 38 dígitos.

		Returns:
			str: Dimensiones extraídas del molde (6 caracteres).
		"""
		final_molde = id_molde[19:]
		return final_molde[-6:]
		
	@staticmethod
	def _obtieneColorSku(sku):
		"""Extrae el código de color a partir del SKU del producto.

		Args:
			sku (str): Código SKU del producto.

		Returns:
			str: Código de color extraído del SKU (posiciones 9 a 13).
		"""
		return sku[9:13]
		
	@staticmethod
	def _obtieneDimensionesSku(sku):
		"""Extrae las dimensiones a partir del SKU del producto.

		Args:
			sku (str): Código SKU del producto.

		Returns:
			str: Dimensiones extraídas del SKU (posiciones 3 a 9).
		"""
		return sku[3:9]
		
	@staticmethod
	def _obtieneModeloSku(sku):
		"""Obtiene el identificador numérico del modelo a partir del SKU del producto.

		Args:
			sku (str): Código SKU del producto.

		Returns:
			int: Identificador numérico del modelo correspondiente al SKU.
		"""
		
		modelo = sku[:3]
		id_modelo = GeneradorNumeroSeriePlato._obtieneModeloNumericoSku(modelo)
		return id_modelo
		
	@staticmethod
	def _obtieneModeloNumericoSku(modelo):
		"""Consulta en la base de datos el identificador numérico del modelo a partir de su nombre de SKU.

		Args:
			modelo (str): Nombre del modelo extraído del SKU (primeros 3 caracteres).

		Returns:
			int: Identificador numérico del modelo en la base de datos.
		"""
		db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		id_modelo = db.ejecutaNamedQuery('FD/Platos/ModeloDeSku', {"sku_name": modelo})
		return id_modelo[0]["id"]
		
	@staticmethod
	def _obtieneDimensionDekor(largo, ancho):
		"""Calcula el código de dimensiones para un plato de tipo Dekor.

		Args:
			largo (int): Largo del plato en milímetros.
			ancho (int): Ancho del plato en milímetros.

		Returns:
			str: Cadena de 6 dígitos con el largo y ancho normalizados.
		"""
		largo_nomralizado = str(largo).zfill(3)
		ancho_normalizado = str(ancho).zfill(3)
		return largo_nomralizado+ancho_normalizado
		
class GeneradorNumeroSerieMolde(GeneradorNumeroSerie):
	"""Generador especializado de números de serie para moldes, hereda de GeneradorNumeroSerie."""
	
	@staticmethod
	def construyeDesdeIdModeloYDimension(id_modelo, largo, ancho, numero_molde):
		"""Construye un generador de número de serie de molde a partir del modelo y sus dimensiones.

		Args:
			id_modelo (int): Identificador del modelo del molde.
			largo (int): Largo del molde en milímetros.
			ancho (int): Ancho del molde en milímetros.
			numero_molde (int): Número identificador del molde.

		Returns:
			GeneradorNumeroSerieMolde: Instancia configurada con los datos del molde.
		"""
		dimensiones = str(largo).zfill(3)+str(ancho).zfill(3)
		return GeneradorNumeroSerieMolde(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_MOLDE, 0, numero_molde, 0, id_modelo, dimensiones
			)
	
	@staticmethod
	def construyeDesdeSKU(sku, id_cliente, id_color):
		"""Construye un generador de número de serie de molde a partir de un SKU.

		Args:
			sku (str): Código SKU del producto.
			id_cliente (int): Identificador del cliente.
			id_color (int): Identificador del color.
		"""
		pass
		
	def _obtieneSeccionFechaNumeroSerie(self):
		"""Retorna la sección de fecha del número de serie del molde como cadena de ceros.

		Returns:
			str: Cadena de 12 ceros, ya que los moldes no utilizan fecha en el número de serie.
		"""
		return str('').zfill(12)

class GeneradorNumeroSerieResiblock(GeneradorNumeroSerie):
	"""Generador especializado de números de serie para elementos Resiblock, hereda de GeneradorNumeroSerie."""
	
	def _obtieneSeccionFechaNumeroSerie(self):
		"""Retorna la sección de fecha del número de serie Resiblock como cadena fija de ceros.

		Returns:
			str: Cadena '00000000' para los elementos de tipo Resiblock.
		"""
		return '00000000'

class GeneradorNumeroSerieEtiquetaMolde(GeneradorNumeroSerie):
	"""Generador especializado de números de serie para etiquetas de molde, hereda de GeneradorNumeroSerie."""
	
	@staticmethod
	def construyeDesdeMolde(id_modelo, largo, ancho, numero_molde):
		"""Construye un generador de número de serie de etiqueta de molde a partir del modelo y sus dimensiones.

		Args:
			id_modelo (int): Identificador del modelo del molde.
			largo (int): Largo del molde en milímetros.
			ancho (int): Ancho del molde en milímetros.
			numero_molde (int): Número identificador del molde.

		Returns:
			GeneradorNumeroSerieEtiquetaMolde: Instancia configurada con los datos del molde.
		"""
		dimensiones = str(largo).zfill(3)+str(ancho).zfill(3)
		id_cliente = GeneradorNumeroSerieEtiquetaMolde._obtieneSeccionClienteNumeroSerie()
		return GeneradorNumeroSerieEtiquetaMolde(
			GeneradorNumeroSerie.TIPO_NUMERO_SERIE_MOLDE, id_cliente, numero_molde, 0, id_modelo, dimensiones
			)
	
	@staticmethod
	def construyeDesdeSKU(sku, id_cliente, id_color):
		"""Construye un generador de número de serie de etiqueta de molde a partir de un SKU.

		Args:
			sku (str): Código SKU del producto.
			id_cliente (int): Identificador del cliente.
			id_color (int): Identificador del color.
		"""
		pass
	
	@staticmethod
	def _obtieneSeccionClienteNumeroSerie():
		"""Genera la sección del cliente para la etiqueta de molde usando los milisegundos actuales.

		Returns:
			str: Milisegundos de la fecha actual formateados a 5 dígitos.
		"""
		fecha_actual = system.date.now()
		milis = system.date.getMillis(fecha_actual)
		milis_formateado = str(milis).zfill(5)
		return milis_formateado