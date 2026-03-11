import unittest

class CabinaPintadoTest(unittest.TestCase):
	_id_cabina_test = -1
	_color_ral_test = 9003
	
	def test(self):
		gestor_pintado = fd.maquinas.cabinapintado.CabinaPintado(self._id_cabina_test)
		print(str(fd.maquinas.cabinapintado.CabinaPintado._gestor_tag_cabina))
		ral_leido = gestor_pintado.obtieneRalActualCabina()
		self.assertEqual(self._color_ral_test, ral_leido)
		
def run():
	suite = unittest.TestLoader().loadTestsFromTestCase(CabinaPintadoTest)
	output = unittest.TextTestRunner(verbosity=3).run(suite)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"