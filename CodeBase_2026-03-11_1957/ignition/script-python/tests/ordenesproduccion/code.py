import unittest

class OrdenProduccionClaveiTests(unittest.TestCase):
	
	_id_orden_test = '01_2024_111675'
	_id_orden_test_detallada = '01_2024_111675\\1_20240702150331'
	
	def testConstructorRellenaBienIds(self):
		orden_test = fd.ordenesproduccion.OrdenProduccionClavei(self._id_orden_test_detallada)
		
		id_orden_devuelto = orden_test.obtieneIdOrden()
		id_orden_detallada_devuelto = orden_test.obtieneIdOrdenDetallada()
		
		self.assertEqual(id_orden_devuelto, self._id_orden_test)
		self.assertEqual(id_orden_detallada_devuelto, self._id_orden_test_detallada)
		
	def testSiExisteOrdenClaveiSeConsultaBien(self):
		orden_test = fd.ordenesproduccion.OrdenProduccionClavei(self._id_orden_test_detallada)
		datos_clavei = orden_test.obtieneInfo()
		self.assertTrue(bool(datos_clavei))
		
	def testSiNoExisteOrdenClaveiDevuelveExcepcion(self):
		id_orden_que_no_existe = "ABC\\1"
		with self.assertRaises(Exception):
			orden_test = fd.ordenesproduccion.OrdenProduccionClavei(id_orden_que_no_existe)
			orden_test.obtieneInfoClavei()

class AsignadorOrdenProduccionTests(unittest.TestCase):
	
	def setUp(self):
		self._id_bloqueo = "test"+str(system.date.toMillis(system.date.now()))
		self._id_bloqueo_destino = self._id_bloqueo + "_dest"
		self._codemp = '01'
		
		self._sku_molde = 'NAT100080'
		self._id_color = 9003
		self._ventana = 10000
	
	def testCicloCompletoBloqueoLiberacion(self):
		asignador = fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_bloqueo, self._codemp)
		orden_asignada = asignador.obtieneYBloqueaOrdenProduccion(self._sku_molde, self._id_color, self._ventana)
		orden_bloqueada = asignador.obtieneOrdenProduccionBloqueada()
		
		self.assertTrue(asignador.existeBloqueo())
		
		self.assertEqual(orden_asignada, orden_bloqueada)
		
		asignador_destino = fd.ordenesproduccion.AsignadorOrdenProduccion(self._id_bloqueo_destino, self._codemp)
		asignador.transfiereOrdenProduccion(self._id_bloqueo_destino)
		
		orden_transferida = asignador_destino.obtieneOrdenProduccionBloqueada()
		orden_en_bloqueo_origen = asignador.obtieneOrdenProduccionBloqueada()
		
		self.assertTrue(asignador_destino.existeBloqueo())
		self.assertEqual(orden_asignada, orden_transferida)
		self.assertEqual(orden_en_bloqueo_origen, None)
		
		asignador_destino.desbloqueaOrdenProduccion()
		orden_en_destino_tras_desbloquear = asignador_destino.obtieneOrdenProduccionBloqueada()
		self.assertEqual(orden_en_destino_tras_desbloquear, None)
		
		asignador.eliminaBloqueo()
		asignador_destino.eliminaBloqueo()
		
		self.assertFalse(asignador.existeBloqueo())
		self.assertFalse(asignador_destino.existeBloqueo())


class SelectorOrdenesProduccionTests(unittest.TestCase):
	pass
	

def run():
	suite_ordenproduccionclavei = unittest.TestLoader().loadTestsFromTestCase(OrdenProduccionClaveiTests)
	suite_asignadorordenproduccion = unittest.TestLoader().loadTestsFromTestCase(AsignadorOrdenProduccionTests)
	suite_selectorordenesproduccion = unittest.TestLoader().loadTestsFromTestCase(SelectorOrdenesProduccionTests)
	
	suites_testear = [
		suite_ordenproduccionclavei, 
		suite_asignadorordenproduccion,
		suite_selectorordenesproduccion
		]
		
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)

	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"