import unittest

class IventarioTest(unittest.TestCase):
	
	_valores_test = ['none,TAG,COUNT,RSSI', 'E2806894000040094923B612,E2806894000040094923B612,1,-33', 'E28068940000400949230212,E28068940000400949230212,1,-33']
	_now = system.date.now()
	
	def testSubirInventario(self):
		gestor_subida_inventario = fd.inventario.inventarioRFID(self._valores_test, self._now, 'lugar1')
		gestor_subida_inventario.subirInventarioMoldes()
		#with self.assertRaises(IOError):
	
def run():
	suite = unittest.TestLoader().loadTestsFromTestCase(IventarioTest)
	output = unittest.TextTestRunner(verbosity=3).run(suite)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"