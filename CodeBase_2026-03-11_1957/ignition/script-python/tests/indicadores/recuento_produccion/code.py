import unittest

class ReportadorProduccionDesmoldeo(unittest.TestCase):
	
	_timestamp_inicio_test = system.date.parse('2024-08-01 17:30:09.000')
	_timestamp_fin_test = system.date.parse('2024-08-02 17:30:18.000')
	_id_linea = 1
	
	def testObtieneRecuentoEnPeriodo(self):
		reporteDesmoldeo = fd.indicadores.recuento_produccion.ReportadorProduccionDesmoldeo(self._timestamp_inicio_test, self._timestamp_fin_test, self._id_linea)
		desmoldeados = reporteDesmoldeo.obtieneRecuentoEnPeriodo()
		print(desmoldeados)
		self.assertTrue(desmoldeados>0)
		
	def testObtieneRecuentoDiaPorHoras(self):
		desmoldeados = fd.indicadores.recuento_produccion.ReportadorProduccionDesmoldeo.obtieneDatasetRecuentoDiarioPorHoras('2024-09-11')
		self.assertTrue(desmoldeados.getRowCount()>0)
		
def run():
	suite = unittest.TestLoader().loadTestsFromTestCase(ReportadorProduccionDesmoldeo)
	output = unittest.TextTestRunner(verbosity=3).run(suite)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"