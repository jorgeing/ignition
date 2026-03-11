import unittest

class EstadosTest(unittest.TestCase):
	
	_estados_test = system.db.runNamedQuery('FD/Supervision/ObtieneEstadosMaquina', {"maquina":'A5'})
	
	def testDevuelveEstados(self):
		return self._estados_test

def run():
	suite_estadosmaquina = unittest.TestLoader().loadTestsFromTestCase(EstadosTest)
	
	suites_testear = [
		suite_estadosmaquina
		]
		
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"