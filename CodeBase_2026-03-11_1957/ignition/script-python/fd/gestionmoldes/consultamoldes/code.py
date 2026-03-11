import re

class BuscadorMoldes:
	
	_bbdd = None
	_conversor_dec_hex = None
	
	def __init__(self, base_datos = 'FactoryDB', proyecto = 'CodeBase'):
		self._bbdd = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._conversor_dec_hex = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal
		
	def obtieneIdMoldePorEpc(self, epc):
		id_molde = None
		
		id_molde = self._compruebaSiEpcEsIdMolde(epc)
		
		if not id_molde:
			id_molde = self._compruebaSiEpcEsIdHexadecimal(epc)
			
		if not id_molde:
			id_molde = self._compruebaSiEpcEsTag(epc)
			
		return id_molde
		
	def _compruebaSiEpcEsIdMolde(self, epc):
		id_devuelto = None
		if self._uuidDecimalEsMolde(epc):
			id_devuelto = epc
		return id_devuelto
		
	def _compruebaSiEpcEsIdHexadecimal(self, epc):
		id_devuelto = None
		uuid_dec = self._conversor_dec_hex.convierteUuidHexadecimalEnDecimal(epc)
		if self._uuidDecimalEsMolde(uuid_dec):
			id_devuelto = uuid_dec	
		return id_devuelto
		
	def _compruebaSiEpcEsTag(self,epc):
		id_devuelto = self._buscaMoldePorTag(epc)
		return id_devuelto
		
	def _uuidDecimalEsMolde(self, uuid):
		patron = r"^200000000000000000\d{5}00000\d{10}$"
		match = re.search(patron, uuid)
		if match:
			return True
		else:
			return False
			
			
	def _buscaMoldePorTag(self, tag):
		params = {'tag':tag}
		id_devuelto = self._bbdd.ejecutaNamedQuery('FD/Moldes/ObtieneMoldeDesdeEpc', params)
		return id_devuelto
		
class BuscadorDimensionesMolde:
	
	RUTA_DIMENSIONES = 'FD/Moldes/ObtieneDimensionesDisponibles'
	
	_bbdd = None
	
	def __init__(self, id_modelo):
		self._bbdd = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self._id_modelo = id_modelo
	
	def obtieneDimensionesDisponibles(self):
		dimensiones = self._consultaDimensiones()
		diccionario_dimensiones = self._transformaADiccionario(dimensiones)
		return diccionario_dimensiones
	
	def _consultaDimensiones(self):
		params = {'id_modelo': self._id_modelo}
		dimensiones_crudo = self._bbdd.ejecutaNamedQuery(self.RUTA_DIMENSIONES, params)
		dimensiones_formateado = system.dataset.toPyDataSet(dimensiones_crudo)
		return dimensiones_formateado
	
	def _transformaADiccionario(self, dimensiones_dataset):
		dim_list=[]
		temp_dict={}
		length=-100
		if len(dimensiones_dataset)>0:
			for row in dimensiones_dataset:
				if row[0]!=length:
					if temp_dict:
						dim_list.append(temp_dict)
					length=row[0]
					temp_dict={'length':length,'widths':[]}
				temp_dict['widths'].append(row[1])
			dim_list.append(temp_dict)
		return dim_list