
class GestorDatosCajasEnvasado:
	
	CLIENTES_VALIDOS = ['KF', 'ADEO', 'Ideal STD']
	
	def __init__(self, datos_plan):
		self._datos_plan = datos_plan
	
	def agrupaDatosPorClienteColorYMolde(self):
		if self._datos_plan.getRowCount() == 0:
			return
		datos_agrupados = self._generaAgrupacion()
		dataset_agrupado = self._construyeDatasetAgrupado(datos_agrupados)
		return dataset_agrupado
	
	def _obtieneClienteDeReferencia(self, referencia):
		if not referencia:
			return None
		
		modelo = referencia[:3].upper()
		if modelo == 'REM':
			cliente = 'ADEO'
		elif modelo == 'PIR':
			cliente = 'KF'
		elif modelo == 'ULT':
			cliente = 'Ideal STD'
		else:
			cliente = None
		
		return cliente
	
	def _obtieneMoldeDeReferencia(self, referencia):
		if not referencia or referencia < 9:
			return None
		return referencia[:9]
	
	def _obtieneColorDeReferencia(self, referencia):
		if not referencia or referencia < 13:
			return None
		return referencia[9:13]
		
	def _generaAgrupacion(self):
		datos_agrupados = {}
		
		for indice in range(self._datos_plan.getRowCount()):
			referencia = self._datos_plan.getValueAt(indice, 'referencia').strip()
			cantida_total = self._datos_plan.getValueAt(indice, 'cantidadtotal')
			
			cliente = self._obtieneClienteDeReferencia(referencia)
			if cliente is None or cliente not in self.CLIENTES_VALIDOS:
				continue
			
			molde = self._obtieneMoldeDeReferencia(referencia)
			color = self._obtieneColorDeReferencia(referencia)
			
			datos_agrupados.setdefault(cliente, {}).setdefault(color, {}).setdefault(molde, {})
			datos_agrupados[cliente][color][molde] = datos_agrupados[cliente][color][molde].get(referencia, 0) + cantida_total
		
		return datos_agrupados
	
	def _construyeDatasetAgrupado(self, datos_agrupados):
		cabeceras = ['Etiquetas de filas', 'Cantidad Total']
		filas = self._generaFilasConSubtotales(datos_agrupados)
		dataset_agrupado = system.dataset.toDataset(cabeceras, filas)
		return dataset_agrupado
	
	def _generaFilasConSubtotales(self, datos_agrupados):
		filas = []
		for cliente in sorted(datos_agrupados.keys()):
			subtotal_cliente = 0
			for color in datos_agrupados[cliente]:
				for molde in datos_agrupados[cliente][color]:
					subtotal_cliente += datos_agrupados[cliente][color][molde]
			filas.append([cliente, subtotal_cliente])
			
			for color in sorted(datos_agrupados[cliente].keys()):
				subtotal_color = 0
				for molde in datos_agrupados[cliente][color]:
					subtotal_color += datos_agrupados[cliente][color][molde]
				filas.append([("\t -" + color).expandtabs(8), subtotal_color])
				
				for molde in sorted(datos_agrupados[cliente][color].keys()):
					subtotal_molde = datos_agrupados[cliente][color][molde]
					filas.append([("\t -" + molde).expandtabs(16), subtotal_molde])
		
		return filas
	
	