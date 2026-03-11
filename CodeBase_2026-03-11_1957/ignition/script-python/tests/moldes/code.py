import unittest

class MoldesTest(unittest.TestCase):
	_mold_id_test = '20000000000000000050006000000099120080'
	_tags_leidos_test = 3
	_molde_test = fd.moldes.Molde(_mold_id_test)
	
	def testExcepcionSiNoExisteMolde(self):
		molde_test_no_existente = "123456798"
		with self.assertRaises(Exception):
			molde = fd.moldes.Molde(molde_test_no_existente)
	
	def testMoldePuedeEstarActivo(self):
		activo = self._molde_test.moldePuedeEstarActivo(self._tags_leidos_test)
			
	def testObtieneEstadoMolde(self):
		self._molde_test.obtieneEstadoMolde()
		
	def testLimiteDeCiclos(self):
		self._molde_test.limiteDeCiclos()
		
	def testCiclosActuales(self):
		self._molde_test.ciclosActuales()
		
	def testObtieneObservaciones(self):
		self._molde_test.obtieneEstadoMolde()

class GestorMoldesTest(unittest.TestCase):
	_mold_id_test = '20000000000000000050006000000099120080'
	_molde_test = fd.moldes.Molde(_mold_id_test)
		
	def testDPendienteReparar(self):
		gestor_molde = fd.moldes.GestorMoldes(self._molde_test)
		
		molde_actualizado = gestor_molde.moldeAPendienteReparacion()
		
		self._molde_test.refresca()
		estado_molde = self._molde_test.obtieneEstadoMolde()
		
		self.assertEqual(estado_molde, fd.moldes.GestorMoldes.ID_ESTADO_PENDIENTE_REPARACION)
		
	def testMoldeEnReparacion(self):
		gestor_molde = fd.moldes.GestorMoldes(self._molde_test)
		
		molde_actualizado = gestor_molde.moldeEnReparacion()
		
		self._molde_test.refresca()
		estado_molde = self._molde_test.obtieneEstadoMolde()
		
		self.assertEqual(estado_molde, fd.moldes.GestorMoldes.ID_ESTADO_REPARACION)
		
	def testDarBajaMolde(self):
		gestor_molde = fd.moldes.GestorMoldes(self._molde_test)
		
		molde_actualizado = gestor_molde.darBajaMolde()
		
		self._molde_test.refresca()
		estado_molde = self._molde_test.obtieneEstadoMolde()
		self.assertEqual(estado_molde, fd.moldes.GestorMoldes.ID_ESTADO_BAJA)
		
	def testDarAltaMolde(self):
		gestor_molde = fd.moldes.GestorMoldes(self._molde_test)
		
		molde_actualizado = gestor_molde.activarMolde()
		
		self._molde_test.refresca()
		estado_molde = self._molde_test.obtieneEstadoMolde()
		self.assertEqual(estado_molde, fd.moldes.GestorMoldes.ID_ESTADO_ACTIVO)
	
	
class GestorTagsMoldesTest(unittest.TestCase):
	_mold_id_test = '20000000000000000050006000000099120080'
	_tags_leidos_test = 2
	_molde = fd.moldes.Molde(_mold_id_test)
	
	def testCompruebaFalsosPendientesReparacion(self):
		gestor_tag_test = fd.moldes.GestorTagsMoldes(self._tags_leidos_test, self._molde)
		gestor_tag_test.compruebaYActualizaFalsosPendientesReparacion()
	
	
	
class GestorBusquedaEPCMoldesTest(unittest.TestCase):
	_moldes_seleccionados_test = [
  "20000000000000000050001000000006100080",
  "20000000000000000050006000000011100100",
  "20000000000000000050008000000009140090",
  "20000000000000000050006000000011120090",
  "20000000000000000050007000000009100080"
	]
	
	
	def testDevuelveEPCMolde(self):
		gestor_epc = fd.moldes.GestorBusquedaEPCMoldes(self._moldes_seleccionados_test)
		epc_moldes = gestor_epc.devuelveEPCMolde()
		print('EPC_moldes_seleccionados: ' + str(epc_moldes))
		
	def testMuestraMoldesSeleccionados(self):
		gestor_epc = fd.moldes.GestorBusquedaEPCMoldes(self._moldes_seleccionados_test)
		moldes_seleccionados = gestor_epc.muestraMoldesSeleccionados()
		print('moldes_seleccionados: ' + str(moldes_seleccionados))
		
		
def run():
	suite_moldes = unittest.TestLoader().loadTestsFromTestCase(MoldesTest)
	suite_gestor_moldes = unittest.TestLoader().loadTestsFromTestCase(GestorMoldesTest)
	suite_gestor_tags = unittest.TestLoader().loadTestsFromTestCase(GestorTagsMoldesTest)
	suite_gestor_epc = unittest.TestLoader().loadTestsFromTestCase(GestorBusquedaEPCMoldesTest)
	
	suites_testear = [
		#suite_moldes,
		suite_gestor_moldes
		#suite_gestor_tags,
		#suite_gestor_epc
		]
		
	alltests = unittest.TestSuite(suites_testear)
	
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"