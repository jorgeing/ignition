class CorrectorClientes:
	"""Corrige el cliente genérico asignando el cliente real según el modelo del plato."""

	_cliente = 99999
	
	def __init__(self, modelo):
		"""Inicializa con el modelo del plato."""
		self._modelo = modelo
	
	def corrigeClienteGenerico(self):
		"""Devuelve el ID de cliente correcto según el modelo."""
		if self._modelo == 'REM':
			self._cliente = 4308
		elif self._modelo == 'PIR':
			self._cliente = 1409
		elif self._modelo == 'ULT' or self._modelo == 'MOS' or self._modelo == 'MOP':
			self._cliente = 4747
		elif self._modelo == 'NUS' or self._modelo == 'CON':
			self._cliente = 5575
		return self._cliente