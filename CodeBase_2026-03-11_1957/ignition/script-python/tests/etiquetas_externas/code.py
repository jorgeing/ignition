import unittest

class GestorImpresionEtiquetasPorSku(unittest.TestCase):
	_sku_test = 'PRE1800707016C02CSTD'
	_id_cliente_test = 2182
	_escaner_test = 0
	_trabajador_test = 1234
	_impresora_test = 17
	_cantidad_test = 200
	
	def testImprimirEtiquetaNumeroValido(self):
		evento = fd.etiquetas_externas.eventoImpresionEtiquetasPorSku(self._sku_test, self._id_cliente_test, self._escaner_test, self._trabajador_test, self._impresora_test)
		evento.imprimirEtiquetasLogisticaPorSkuYCantidad(2)
		
	def testImprimirEtiquetaNumNoValido(self):
		evento = fd.etiquetas_externas.eventoImpresionEtiquetasPorSku(self._sku_test, self._id_cliente_test, self._escaner_test, self._trabajador_test, self._impresora_test)
		with self.assertRaises(Exception):
			evento.imprimirEtiquetasLogisticaPorSkuYCantidad(200)
		
		
def run():
	suite = unittest.TestLoader().loadTestsFromTestCase(GestorImpresionEtiquetasPorSku)
	output = unittest.TextTestRunner(verbosity=3).run(suite)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"