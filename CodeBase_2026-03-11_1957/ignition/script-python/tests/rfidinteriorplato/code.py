import unittest

class GestorAsignacionRFIDTest(unittest.TestCase):
	_info_tag_test = system.tag.readBlocking('[rfid_tags]Antennas/Molds/test_reader')[0]
	
	def testGuardaRFIDparaPlato(self):
		gestor_asignacion = fd.rfidinteriorplato.EventoAsignacionRFIDDentroDelPlato(self._info_tag_test, 3)
		lineas_creadas_modificadas = gestor_asignacion.guardaRFIDparaPlato()
		self.assertEqual(lineas_creadas_modificadas, 1)
		print(lineas_creadas_modificadas)
		#gestor_asignacion.verificaLosChipsGuardados()
		
class GestorInformacionParaLaAntena(unittest.TestCase):
	
	_query_tag_test = 'E2801191A503006B0F3E2AA4'
	solucion_test = {'code':200,'message':'OK', 'IDHex':'E2801191A503006B0F3E2AA4', 'IDDec':'E2801191A503006B0F3E2AA4', 'type':'label'}

	def testInformacionParaLaAntena(self):
		generador = fd.rfidinteriorplato.InformacionParaLaAntena(self._query_tag_test)
		resp = generador.generaJson()
		print(str(resp))
		self.assertEqual(resp, self.solucion_test)
		
class GestorValidacionRFID(unittest.TestCase):
	
	_query_tag_test = 'E2801191A503006B0F404044'
	_showertray_id_test = '12410111144000012550001009003001130090'
	_path_rfid_anterior_test = '[rfid_tags]Antennas/Molds/line1_line_output/rfid_id_interior_anterior'
	
	def testEsValido(self):
		validador = fd.rfidinteriorplato.ValidacionValorTag(self._query_tag_test, self._showertray_id_test)
		respuesta = validador.esRFIDValido()
		print(str(respuesta))
		
class GestorAsignadorRFIDInterior(unittest.TestCase):
	
	_path_test = '[rfid_tags]Antennas/Zones/catapult1'
	
	def testAsignaSiValido(self):
		validador = fd.rfidinteriorplato.AsignadorRFIDInterior.asignaSiValido(self._path_test)
		print(str(validador))
		
		
		
class GestorCodificacionRfid(unittest.TestCase):
	_test_cantidad = 10
	
	def testGeneraUuids(self):
		gestor_generador = fd.rfidinteriorplato.GeneradorCodificacionRfid(self._test_cantidad)
		lista_uuids = gestor_generador.generaUuidUnico()
		print(lista_uuids)
		
	def testCompruebaCRC(self):
		pass
	
	
def run():
	
	suite_asignadorRFID = unittest.TestLoader().loadTestsFromTestCase(GestorAsignacionRFIDTest)
	suite_validadorRFID = unittest.TestLoader().loadTestsFromTestCase(GestorValidacionRFID)
	suite_validadorEstatico = unittest.TestLoader().loadTestsFromTestCase(GestorAsignadorRFIDInterior)
	
	suites_testear = [
		suite_validadorRFID, 
		suite_validadorEstatico
		#suite_asignadorRFID
		]
	
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"