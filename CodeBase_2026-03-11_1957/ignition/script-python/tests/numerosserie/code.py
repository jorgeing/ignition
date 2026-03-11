import unittest

class NumeroSerieTest(unittest.TestCase):
	_numero_serie_dec_test = "12312120956570218250000009003001180080"
	_numero_serie_hex_test = "111624E0B4CD1181000008302CAFEFB0"
	
	def testNumeroSerieCreadoDesdeDecimal(self):
		n_serie_test = fd.numerosserie.NumeroSerie(self._numero_serie_dec_test)
		self.assertEqual(n_serie_test.obtieneNumeroSerieDecimal(), self._numero_serie_dec_test)
		self.assertEqual(n_serie_test.obtieneNumeroSerieHexadecimal(), self._numero_serie_hex_test)
		
	def testNumeroSerieCreadoDesdeHexadecimal(self):
		n_serie_test = fd.numerosserie.NumeroSerie(self._numero_serie_hex_test)
		self.assertEqual(n_serie_test.obtieneNumeroSerieDecimal(), self._numero_serie_dec_test)
		self.assertEqual(n_serie_test.obtieneNumeroSerieHexadecimal(), self._numero_serie_hex_test)

class GeneradorNumeroSeriePlatoTests(unittest.TestCase):
	_mold_id_test = '20000000000000000050007000000010120080'
	_sku_test = 'HER1200809003'
	_id_cliente_test = 2182
	_id_color_test = 9003
	
	def testContruyeDesdeMolde(self):
		generador = fd.numerosserie.GeneradorNumeroSeriePlato.construyeDesdeMolde(self._mold_id_test, self._id_cliente_test, self._id_color_test)
		numero_serie = generador.obtieneNumeroSerie()
		self.assertEqual(38, len(numero_serie))
		self.assertEqual(int(self._mold_id_test[-9:]),int(numero_serie[-9:]))
		
	def testContruyeDesdeSKu(self):
		generador = fd.numerosserie.GeneradorNumeroSeriePlato.contruyeDesdeSku(self._sku_test, self._id_cliente_test)
		numero_serie = generador.obtieneNumeroSerie()
		self.assertEqual(38, len(numero_serie))
		self.assertEqual(int(120080),int(numero_serie[-6:]))
	
	
def run():
	suite_numeroserie = unittest.TestLoader().loadTestsFromTestCase(NumeroSerieTest)
	suite_generadornumeroserie_plato = unittest.TestLoader().loadTestsFromTestCase(GeneradorNumeroSeriePlatoTests)
	suites_testear = [
		suite_numeroserie,
		suite_generadornumeroserie_plato
		]
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"