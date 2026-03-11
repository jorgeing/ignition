import unittest

class ConstructorSQLTests(unittest.TestCase):
	
	def testCreaMapeo(self):
		mapeo_esperado = {"nombreColumna": "nombre1", "tipo":fd.utilidades.ConstructorSQL.TIPO_COLUMNA_TEXTO}
		mapeo_calculado = fd.utilidades.ConstructorSQL.creaMapeo("nombre1", fd.utilidades.ConstructorSQL.TIPO_COLUMNA_TEXTO)
		self.assertEqual(mapeo_esperado,mapeo_calculado)
		
	def testgeneraStringValoresParaInsertMasivo(self):
		
		
		fecha_texto_prueba = "2024-07-08 00:00:00"
		fecha_prueba = system.date.parse(fecha_texto_prueba,"yyyy-MM-dd HH:mm:ss")
		
		dataset_prueba = [
			{"col_num":1,"col_text":"texto","col_date":fecha_prueba},
			{"col_num":2,"col_text":"texto2","col_date":fecha_prueba}
		]
		mapeos = [
			fd.utilidades.ConstructorSQL.creaMapeo("col_num", fd.utilidades.ConstructorSQL.TIPO_COLUMNA_NUMERO),
			fd.utilidades.ConstructorSQL.creaMapeo("col_text", fd.utilidades.ConstructorSQL.TIPO_COLUMNA_TEXTO),
			fd.utilidades.ConstructorSQL.creaMapeo("col_date", fd.utilidades.ConstructorSQL.TIPO_COLUMNA_FECHA)
		]
		
		insert_string_esperada = "( 1, 'texto', '2024-07-08 00:00:00' ),( 2, 'texto2', '2024-07-08 00:00:00' )"
		insert_string = fd.utilidades.ConstructorSQL.generaStringValoresParaInsertMasivo(dataset_prueba, mapeos)
		self.assertEqual(insert_string_esperada, insert_string)
		
		
		

class GestorTagsTests(unittest.TestCase):
	
	def testEscrituraUnTagConReintentoFalla(self):
		path = "[rfid_tags]Falso"
		valor="test"
		with self.assertRaises(IOError):
			fd.utilidades.GestorTags.escribeTagsConReintento(path, valor)
			
	def testEscrituraVariosTagConReintentoFalla(self):
		path = ["[rfid_tags]Falso", "[rfid_tags]Falso2"]
		valor=["test","test2"]
		with self.assertRaises(IOError):
			fd.utilidades.GestorTags.escribeTagsConReintento(path, valor)
			
	def testEscrituraVariosTagConReintentoFalla(self):
		path = ["[rfid_tags]Tests/tag_test_1", "[rfid_tags]Tests/tag_test_2"]
		valor=[system.date.now(),system.date.now()]

		fd.utilidades.GestorTags.escribeTagsConReintento(path, valor)

class ExportadorExcelTests(unittest.TestCase):
	_nombre = 'test'
	_cabeceras = ['a','b']
	_datos_raw = [[1,2],[3,4]]
	
	def testExportadorExcel(self):
		dataset = system.dataset.toDataSet(self._cabeceras, self._datos_raw)
		export_excel = fd.utilidades.ExportadorExcel(self._nombre, dataset)
		excel_bytes = export_excel.obtieneArrayBytes()
		self.assertTrue(len(excel_bytes)>0)
	
def run():
	suite_gestortags = unittest.TestLoader().loadTestsFromTestCase(GestorTagsTests)
	suite_constructorsql = unittest.TestLoader().loadTestsFromTestCase(ConstructorSQLTests)
	suite_exportadorexcel = unittest.TestLoader().loadTestsFromTestCase(ExportadorExcelTests)
	suites_testear = [
		suite_gestortags, 
		suite_constructorsql,
		suite_exportadorexcel
		]
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"