import re

class ManejadorSku:
	
	_codigo_sku = ''
	
	def __init__(self, codigo_sku):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._codigo_sku = codigo_sku
		if not self.esValido():
			raise Exception("Sku no valido: " + str(codigo_sku))
		
	def esValido(self):
		return self.esSkuFD() or self.esSkuPartNumber() or self.esSkuDekor() or self.esSkuCorte()		
		
	def obtieneSkuMolde(self):
		if self._contienePartNumber():
			return self._obtieneSkuMoldeFD()
		elif self.esSkuDekor():
			return self._obtieneSkuMoldedekor()
		else:
			raise Exception("No se puede obtener sku de molde para: "+str(self._codigo_sku))
			
	def obtieneIdColor(self):
		if self._contienePartNumber():
			return self._obtieneIdColorFD()
		elif self.esSkuDekor():
			return self._obtieneIdColorDekor()
		else:
			raise Exception("No se puede obtener id color para: "+str(self._codigo_sku))
			
	def esSkuFD(self):
	    #pattern = r'^(.{3}[0-9]{6}.{4}[A-Z]{1}[0-9]{2}[A-Z]{3})'
	    pattern = r'^(.{3}[0-9]{6}.{4}.{1}[0-9]{2}.{1}.{3})'
	    match = re.search(pattern, self._codigo_sku)
	    return match and len(self._codigo_sku)==20
	    
	def esSkuDekor(self):
		return len(self._codigo_sku)<=20 and (self._codigo_sku[0:2] == 'PL' or self._codigo_sku[0:3] == 'DEK')
	
	def esSkuCorte(self):
		return self._compruebaSiEsCorte()
	
	def esSkuPartNumber(self):
		pattern = r'^(.{3}[0-9]{6}.{4})'
		match = re.search(pattern, self._codigo_sku)
		return match and len(self._codigo_sku)==13
	
	def obtieneLargo(self):
		largo_str = self._codigo_sku[3:6]
		return int(largo_str)
		
	def obtieneAncho(self):
		ancho_str = self._codigo_sku[6:9]
		return int(ancho_str)
	
	def obtienePartNumberDeSku(self):
		return self._codigo_sku[:13]
	
	def _contienePartNumber(self):
		return self.esSkuFD() or self.esSkuPartNumber()
		
	def _obtieneSkuMoldeFD(self):
		return self._codigo_sku[0:9]
	
	def _obtieneIdColorFD(self):
		return self._codigo_sku[9:13]
		
	def _obtieneIdColorDekor(self):
		raise NotImplementedError("funcionalidad no implementada")
	
	def _compruebaSiEsCorte(self):
		modelos_corte = self._obtieneModelosDeCorte()
		modelo_sku = self._obtieneModeloDeSku()
		return modelo_sku in modelos_corte
	
	def _obtieneModelosDeCorte(self):
		ruta_select_modelos_corte = 'FD/Platos/ObtieneModelosCorte'
		modelos_corte_dataset = self._db.ejecutaNamedQuery(ruta_select_modelos_corte, {})
		modelos_corte = [modelos_corte_dataset.getValueAt(i, 0) for i in range(modelos_corte_dataset.getRowCount())]
		return modelos_corte
	
	def _obtieneModeloDeSku(self):
		return self._codigo_sku[:3]
		
class GeneradorSku:
	
	def __init__(self, modelo, color, largo, ancho):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._modelo = modelo
		self._color = color
		self._largo = self._dimensionesFormaUnificada(largo)
		self._ancho = self._dimensionesFormaUnificada(ancho)
		
	def generaPartNumber(self):
		return self._modelo + str(self._largo) + str(self._ancho) + str(self._color).zfill(4)
		
	def generaSkuSiNoHayOrdenPtoduccion(self):
		self._opciones = self._obtienePlatosCompatiblesPartNumber()
		return self._obtieneSkuDefault()
		
	def _obtieneSkuDefault(self):
		
		if not self._hayVariosCandidatos():
			return self._opciones[0]["CodArt"]
			
		elif self._hayVariosCandidatos():
			sku_kfg = self._skuEsKingFisher()
			sku_std = self._skuEsSTD()
			if len(sku_kfg) == 1:
				return sku_kfg[0]
			elif len(sku_std) ==  1:
				return sku_std[0]
			else:
				return self._skuEsOMS(sku_std)
		else:
			return self.generaPartNumber()
			
	def _hayVariosCandidatos(self,):
		return self._opciones.getRowCount() > 1
		
	def _skuEsSTD(self):
		sku = []
		for fila in self._opciones:
				if fila["CodArt"][17:] == 'STD':
					sku.append(fila["CodArt"])
		return sku
		
	def _skuEsOMS(self, sku):
		sku_oms = ''
		for lista in sku:
			if lista[13:16] == 'G20' or lista[13:16] == 'G30':
				sku_oms = lista
		return sku_oms
		
	def _skuEsKingFisher(self):
		sku = []
		for fila in self._opciones:
				if fila["CodArt"][17:] == 'KFG':
					sku.append(fila["CodArt"])
		return sku
		
	def _obtienePlatosCompatiblesPartNumber(self):
		return self._db.ejecutaNamedQuery('FD/Platos/ObtienePlatosCompatiblesPartNumber', {"part_number": self.generaPartNumber(), "CodEmp": fd.globales.ParametrosGlobales.obtieneCodEmp()})
		
	def _dimensionesFormaUnificada(self, dimension):
		return str(dimension).zfill(3)
	
class ConversorSKUCorte:
	
	_codigo_sku = ''
	_manejador_sku = None
	
	REJILLA_SEMIPRODUCTO = '0000'
	SUFIJO_SEMIPRODUCTO = 'CUT'
	
	def __init__(self, codigo_sku, molde_marco = None):
		self._codigo_sku = codigo_sku
		self._manejador_sku = ManejadorSku(codigo_sku)
		self._molde_marco = molde_marco
		if not self._esCorte():
			raise Exception("Sku no es corte")
		
	def _esCorte(self):
		return self._manejador_sku.esSkuCorte()
	
	def convierteASkuSemiProducto(self):
		partnumber_semiproducto = self._obtienePartNumberSemiProducto()
		sku_semiproducto = self._construyeSkuSemiProducto(partnumber_semiproducto)
		return sku_semiproducto
	
	def _obtienePartNumberSemiProducto(self):
		modelo_semiproducto = self._obtieneModeloSemiProducto()
		dimensiones_y_color = self._obtieneDimensionesYColor()
		partnumber_semiproducto = modelo_semiproducto + dimensiones_y_color
		return partnumber_semiproducto
	
	def _obtieneModeloSemiProducto(self):
		modelo_semiproducto = ''
		if self._molde_marco:
			modelo_semiproducto = self._molde_marco
		else:
			modelo_producto_final = self._codigo_sku[:3]
			if modelo_producto_final == 'NAC':
				modelo_semiproducto = 'NAT'
			elif modelo_producto_final == 'HEC':
				modelo_semiproducto = 'HER'
			elif modelo_producto_final == 'PRC':
				modelo_semiproducto = 'PRE'
			elif modelo_producto_final == 'NEC':
				modelo_semiproducto = 'NEO'
			elif modelo_producto_final == 'KAC':
				modelo_semiproducto = 'KAL'
			elif modelo_producto_final == 'MAC':
				modelo_semiproducto = 'MAN'
		return modelo_semiproducto
	
	def _obtieneDimensionesYColor(self):
		return self._codigo_sku[3:13]
	
	def _construyeSkuSemiProducto(self, partnumber_semiproducto):
		sku_semiproducto = partnumber_semiproducto + self.REJILLA_SEMIPRODUCTO + self.SUFIJO_SEMIPRODUCTO
		return sku_semiproducto
	
class ConversorSKUDekor:
	
	_codigo_sku = ''
	_manejador_sku = None
	
	MODELO_SEMIPRODUCTO = 'NAT'
	COLOR_SEMIPRODUCTTO = '9003'
	REJILLA_SEMIPRODUCTO = '0000'
	SUFIJO_SEMIPRODUCTO = 'DEK'
	
	def __init__(self, codigo_sku):
		self._codigo_sku = codigo_sku
		self._manejador_sku = ManejadorSku(codigo_sku)
		if not self._esDekor():
			raise Exception("Sku no es dekor")
		
	def _esDekor(self):
		return self._manejador_sku.esSkuDekor()
	
	def convierteASkuSemiProducto(self):
		partnumber_semiproducto = self._obtienePartNumberSemiProducto()
		sku_semiproducto = self._construyeSkuSemiProducto(partnumber_semiproducto)
		return sku_semiproducto
	
	def _obtienePartNumberSemiProducto(self):
		modelo_semiproducto = self.MODELO_SEMIPRODUCTO
		dimensiones = self._obtieneDimensionesSemiProducto()
		color = self.COLOR_SEMIPRODUCTTO
		partnumber_semiproducto = modelo_semiproducto + dimensiones + color
		return partnumber_semiproducto
	
	def _obtieneDimensionesSemiProducto(self):
		dimensiones = ''
		if self._codigo_sku[0:2] == 'PL':
			largo = self._obtieneLargoSkuOld()
			ancho = self._obtieneAnchoSkuOld()
			dimensiones = largo + ancho
		elif self._codigo_sku[0:3] == 'DEK':
			dimensiones = self._codigo_sku[3:9]
		return dimensiones
	
	def _obtieneLargoSkuOld(self):
		largo = ''
		if int(self._codigo_sku[5]) <= 2:
				largo = self._codigo_sku[5:8]
		else:
			largo = (self._codigo_sku[5:7]).zfill(3)
		return largo
	
	def _obtieneAnchoSkuOld(self):
		ancho = ''
		if int(self._codigo_sku[8]) <= 2:
				ancho = self._codigo_sku[8:11]
		else:
			ancho = (self._codigo_sku[8:10]).zfill(3)
		return ancho
	
	def _construyeSkuSemiProducto(self, partnumber_semiproducto):
		sku_semiproducto = partnumber_semiproducto + self.REJILLA_SEMIPRODUCTO + self.SUFIJO_SEMIPRODUCTO
		return sku_semiproducto
	
	
	