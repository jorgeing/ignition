from collections import OrderedDict

class ConversorFormatosDataset:
	
	@staticmethod
	def filaDatasetADiccionario(dataset, row_index):
		dictionary = {}
		for c in range(dataset.getColumnCount()):
			dictionary[dataset.getColumnName(c)]=dataset.getValueAt(row_index,c)
			
		return dictionary

	@staticmethod
	def diccionarioAFilaDataset(diccionario):
		
		claves = diccionario.keys()
		valores = diccionario.values()
		return system.dataset.toPyDataSet(
			system.dataset.toDataSet(claves, [valores])
			)
	
	@staticmethod
	def datasetAListaDeDiccionarios(dataset):
		pyDataset = system.dataset.toPyDataSet(dataset)
		columnas = list(pyDataset.getColumnNames())
		lista_diccionarios = []
		for fila in pyDataset:
			diccionario = {}
			for idx,columna in enumerate(columnas):
				diccionario[columna] = fila[idx]
			lista_diccionarios.append(diccionario)
		return lista_diccionarios
	
	@staticmethod
	def listaDeDiccionariosADataset(lista_diccionarios):
		if not lista_diccionarios:
			return system.dataset.toDataSet([], [])
		columnas = list(lista_diccionarios[0].keys())
		filas = []
		for diccionario in lista_diccionarios:
			fila = []
			for columna in columnas:
				fila.append(diccionario.get(columna, None))
			filas.append(fila)
		return system.dataset.toDataSet(columnas, filas)
	
	@staticmethod
	def datasetAJsonAgrupado(dataset, group_key, children_key="options", excluirGroupKeyEnHijos=True):

		ConversorFormatosDataset._validarDataset(dataset)
		ConversorFormatosDataset._validarColumna(dataset, group_key)
		ConversorFormatosDataset._validarTextoNoVacio(children_key, "children_key")

		filas = ConversorFormatosDataset.datasetAListaDeDiccionarios(dataset)
		grupos = ConversorFormatosDataset._agruparDiccionariosPorClave(filas, group_key)

		return ConversorFormatosDataset._construirJsonAgrupado(
			grupos,
			group_key,
			children_key,
			excluirGroupKeyEnHijos
		)

	@staticmethod
	def _agruparDiccionariosPorClave(lista_diccionarios, group_key):
		grupos = OrderedDict()
		for d in lista_diccionarios:
			valor = d.get(group_key)
			if valor not in grupos:
				grupos[valor] = []
			grupos[valor].append(d)
		return grupos

	@staticmethod
	def _construirJsonAgrupado(grupos, group_key, children_key, excluirGroupKeyEnHijos):
		resultado = []
		for valor_grupo, filas in grupos.items():
			hijos = ConversorFormatosDataset._construirHijos(
				filas,
				group_key,
				excluirGroupKeyEnHijos
			)
			resultado.append({
				group_key: valor_grupo,
				children_key: hijos
			})
		return resultado

	@staticmethod
	def _construirHijos(filas, group_key, excluirGroupKeyEnHijos):

		if not excluirGroupKeyEnHijos:
			return [dict(f) for f in filas]

		hijos = []
		for f in filas:
			item = dict(f)
			item.pop(group_key, None)
			hijos.append(item)

		return hijos

	@staticmethod
	def _validarDataset(dataset):
		if dataset is None:
			raise ValueError("dataset no puede ser None.")

	@staticmethod
	def _validarColumna(dataset, column_name):
		columnas = list(dataset.getColumnNames())
		if column_name not in columnas:
			raise ValueError(
				"La columna '{}' no existe. Columnas disponibles: {}".format(
					column_name, columnas
				)
			)

	@staticmethod
	def _validarTextoNoVacio(texto, nombre_param):
		if texto is None or str(texto).strip() == "":
			raise ValueError("{} debe ser un string no vacío.".format(nombre_param))