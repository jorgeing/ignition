import unittest

class WipTestScrap(unittest.TestCase):
	_showertray_id = '12205222139579999950001009005006170070'
	_razon = 200
	
	def testScrap(self):
		gestor_scrap = fd.wip.GestionMotivosScrap(self._razon, self._showertray_id)
		motivo_asignado = gestor_scrap.asignaMotivo()
		resultado = system.util.jsonDecode(motivo_asignado)
		self.assertEqual(resultado, 200)



def run():
	suite_wip_scrap = unittest.TestLoader().loadTestsFromTestCase(WipTestScrap)
	
	suites_testear = [
		suite_wip_scrap
		]
		
	alltests = unittest.TestSuite(suites_testear)
	
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"