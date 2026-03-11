import unittest

class GestorTagsTests(unittest.TestCase):
	
	def testEscrituraUnTagConReintentoFalla(self):
		path = "[rfid_tags]Falso"
		valor="test"
		with self.assertRaises(IOError):
			fd.utilidades.tags.GestorTags.escribeTagsConReintento(path, valor)
			
	def testEscrituraVariosTagConReintentoFalla(self):
		path = ["[rfid_tags]Falso", "[rfid_tags]Falso2"]
		valor=["test","test2"]
		with self.assertRaises(IOError):
			fd.utilidades.tags.GestorTags.escribeTagsConReintento(path, valor)
			
	def testEscrituraVariosTagConReintentoFalla(self):
		path = ["[rfid_tags]Tests/tag_test_1", "[rfid_tags]Tests/tag_test_2"]
		valor=[system.date.now(),system.date.now()]

		fd.utilidades.tags.GestorTags.escribeTagsConReintento(path, valor)