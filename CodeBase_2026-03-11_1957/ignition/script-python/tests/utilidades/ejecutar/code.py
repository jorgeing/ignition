import unittest

def run():
	suite_gestortags = unittest.TestLoader().loadTestsFromTestCase(tests.utilidades.tags.GestorTagsTests)
	suite_constructorsql = unittest.TestLoader().loadTestsFromTestCase(tests.utilidades.sql.ConstructorSQLTests)
	suite_exportadorexcel = unittest.TestLoader().loadTestsFromTestCase(tests.utilidades.excel.ExportadorExcelTests)
	suite_datosturno = unittest.TestLoader().loadTestsFromTestCase(tests.utilidades.turnoproduccion.DatosTurnoTest)
	
	
	suites_testear = [
		suite_gestortags, 
		suite_constructorsql,
		suite_exportadorexcel,
		suite_datosturno
		]
		
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"