import unittest

class PlatoDuchaTest(unittest.TestCase):
	_numero_serie_plato_test_string = "12312120956570218250000009003001180080"
	
	def testConstructorDesdeNumeroSerie(self):
		numero_serie = fd.numerosserie.NumeroSerie(self._numero_serie_plato_test_string)
		plato_test = fd.platos.PlatoDucha(numero_serie)
		info_scada = plato_test.obtieneInfoScada()
		self.assertEqual(info_scada["showertray_id"],self._numero_serie_plato_test_string)




class GestorPlatosTest(unittest.TestCase):
	_mold_id_test = '20000000000000000050007000000010120080'
	_id_color_test = 9003
	_id_cliente_test = 2812
	
	def testCrearPlatoDEsdeMolde(self):
		id_color = 9003
		id_cliente = 2200
		#evento = fd.platos.EventoCreacionPlato(self._mold_id_test)
		#evento.creaPlatoDesdeMolde(self._id_color_test, self._id_cliente_test)
		#plato_evento = evento.obtieneNumeroSerie()
		#self.assertEqual(, plato_evento)
		
	
def run():
	suite_evento_creation_plato = unittest.TestLoader().loadTestsFromTestCase(GestorPlatosTest)
	suite_platoducha = unittest.TestLoader().loadTestsFromTestCase(PlatoDuchaTest)
	
	suites_testear = [
		suite_evento_creation_plato,
		suite_platoducha
		]
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"