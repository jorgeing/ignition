import unittest

class GestorEtiquetasTest(unittest.TestCase):
	_sku_test = 'PRE1800707016C02CSTD'
	_id_cliente_test = 2182
	_escaner_test = 0
	_trabajador_test = 1234
	_impresora_test = 17
	_cantidad_test = 2
	
	def testImprimirEtiqueta(self):
		pass
		
		
def run():
	suite = unittest.TestLoader().loadTestsFromTestCase(GestorEtiquetasTest)
	output = unittest.TextTestRunner(verbosity=3).run(suite)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"