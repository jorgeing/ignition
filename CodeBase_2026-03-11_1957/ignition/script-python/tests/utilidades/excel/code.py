import unittest

class ExportadorExcelTests(unittest.TestCase):
	_nombre = 'test'
	_cabeceras = ['a','b']
	_datos_raw = [[1,2],[3,4]]
	
	def testExportadorExcel(self):
		dataset = system.dataset.toDataSet(self._cabeceras, self._datos_raw)
		export_excel = fd.utilidades.excel.ExportadorExcel(self._nombre, dataset)
		excel_bytes = export_excel.obtieneArrayBytes()
		self.assertTrue(len(excel_bytes)>0)