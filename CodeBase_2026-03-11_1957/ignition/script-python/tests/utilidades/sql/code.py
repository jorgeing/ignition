import unittest

class ConstructorSQLTests(unittest.TestCase):
	
	def testCreaMapeo(self):
		mapeo_esperado = {"nombreColumna": "nombre1", "tipo":fd.utilidades.sql.ConstructorSQL.TIPO_COLUMNA_TEXTO}
		mapeo_calculado = fd.utilidades.sql.ConstructorSQL.creaMapeo("nombre1", fd.utilidades.sql.ConstructorSQL.TIPO_COLUMNA_TEXTO)
		self.assertEqual(mapeo_esperado,mapeo_calculado)
		
	def testgeneraStringValoresParaInsertMasivo(self):
		
		
		fecha_texto_prueba = "2024-07-08 00:00:00"
		fecha_prueba = system.date.parse(fecha_texto_prueba,"yyyy-MM-dd HH:mm:ss")
		
		dataset_prueba = [
			{"col_num":1,"col_text":"texto","col_date":fecha_prueba},
			{"col_num":2,"col_text":"texto2","col_date":fecha_prueba}
		]
		mapeos = [
			fd.utilidades.sql.ConstructorSQL.creaMapeo("col_num", fd.utilidades.sql.ConstructorSQL.TIPO_COLUMNA_NUMERO),
			fd.utilidades.sql.ConstructorSQL.creaMapeo("col_text", fd.utilidades.sql.ConstructorSQL.TIPO_COLUMNA_TEXTO),
			fd.utilidades.sql.ConstructorSQL.creaMapeo("col_date", fd.utilidades.sql.ConstructorSQL.TIPO_COLUMNA_FECHA)
		]
		
		insert_string_esperada = "( 1, 'texto', '2024-07-08 00:00:00' ),( 2, 'texto2', '2024-07-08 00:00:00' )"
		insert_string = fd.utilidades.sql.ConstructorSQL.generaStringValoresParaInsertMasivo(dataset_prueba, mapeos)
		self.assertEqual(insert_string_esperada, insert_string)