import unittest

def run():
	suite_cabinapintado = unittest.TestLoader().loadTestsFromTestCase(tests.maquinas.cabinapintado.CabinaPintadoTest)
	
	suites_testear = [
		suite_cabinapintado
		]
		
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"