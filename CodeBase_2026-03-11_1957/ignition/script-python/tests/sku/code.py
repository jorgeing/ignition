import unittest

class SkuTest(unittest.TestCase):
	_sku_fd_test = "NAT1200809003G01XSTD"
	_sku_dekor_test = "PLARA12080"
	_sku_part_number_test = "NAT1200809003"
	
	def testSkuFD(self):
		sku = fd.sku.ManejadorSku(self._sku_fd_test)
		self.assertEqual(sku.obtieneSkuMolde(),'NAT120080')
		self.assertEqual(sku.obtieneIdColor(),'9003')
		
	def testSkuDekor(self):
		sku = fd.sku.ManejadorSku(self._sku_dekor_test)
		with self.assertRaises(Exception):
			sku.obtieneSkuMolde()
			sku.obtieneIdColor()
			
	def testPartNumber(self):
		sku = fd.sku.ManejadorSku(self._sku_part_number_test)
		self.assertEqual(sku.obtieneSkuMolde(),'NAT120080')
		self.assertEqual(sku.obtieneIdColor(),'9003')

	
	
def run():
	suite_sku = unittest.TestLoader().loadTestsFromTestCase(SkuTest)

	suites_testear = [
		suite_sku
		]
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"