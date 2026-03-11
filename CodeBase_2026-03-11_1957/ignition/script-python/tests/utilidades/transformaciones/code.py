import unittest

class ConversoresTests(unittest.TestCase):
	_numero_serie_dec_test2 = "12312120956570218250000009003001180080"
	_numero_serie_hex_test2 = "111624E0B4CD1181000008302CAFEFB0"
	
	_numero_serie_dec_test = "81311240000000000000000000000000011133"
	_numero_serie_hex_test = "70D78E328CA740000000000000002B7D"
	
	def testConvierteUuidDecimalEnHexadecimal(self):
		conversor = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal
		self.assertEqual(conversor.convierteUuidDecimalEnHexadecimal(self._numero_serie_dec_test), self._numero_serie_hex_test)
		
	def testConvierteUuidHexadecimalEnDecimal(self):
		conversor = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal
		self.assertEqual(conversor.convierteUuidHexadecimalEnDecimal(self._numero_serie_hex_test), self._numero_serie_dec_test)
		
		
def run():
	suite_conversor = unittest.TestLoader().loadTestsFromTestCase(ConversoresTests)
	suites_testear = [
		suite_conversor
		]
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"