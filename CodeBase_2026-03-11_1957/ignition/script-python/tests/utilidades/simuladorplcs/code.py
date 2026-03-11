import unittest

class generadorTextoCsvSimuladorPLCOmron(unittest.TestCase):
	
	textoOmron= """
	HOST	NAME	DATATYPE	ADDRESS	COMMENT	TAGLINK	RW	POU
		string	STRING(64)			TRUE	RW	
		HMI_REQUEST.BODY	BOOL			TRUE	RW	
	
	"""
	
	
	def testTransformaTextoCorrecto(self):
		pass