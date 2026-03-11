from fd.utilidades.tags import *

class CabinaPintado:
	
	PATH_UDT_CABINA_TEST = '[via_platos]MaquinasTest/CabinaPinturaTest'
	PATH_UDT_CABINA_1 = '[via_platos]Via1PinturaLLenado/Cabina1'
	PATH_UDT_CABINA_2 = '[via_platos]Via2Pintura/Cabina2'
	
	_id_cabina = 0

	_gestor_tag_cabina = None
	
	def __init__(self, id_cabina):
		self._id_cabina = id_cabina
		self._obtieneGestorTagCabina()
		
	def obtieneRalActualCabina(self):
		ral_actual = self._gestor_tag_cabina.obtieneRalActualCabina()
		return ral_actual
		
	def obtieneRalAnteriorCabina(self):
		pass
		
	def _obtieneGestorTagCabina(self):
		path_udt_cabina = self._obtienePathUdtCabina()
		self._gestor_tag_cabina = GestorTagCabinaPintado(path_udt_cabina)
		
	def _obtienePathUdtCabina(self):
		if self._id_cabina == 1:
			path_udt_cabina = self.PATH_UDT_CABINA_1
		elif self._id_cabina == 2:
			path_udt_cabina = self.PATH_UDT_CABINA_2
		elif self._id_cabina == -1:
			path_udt_cabina = self.PATH_UDT_CABINA_TEST
		else:
			raise Exception("No existe cabina con id: "+self._id_cabina)
		return path_udt_cabina
		
	def _obtieneColoresInstaladosEnCabina():
		pass
		

class GestorTagCabinaPintado:
	
	_path_udt_cabina = ""
	
	def __init__(self, path_udt_cabina):
		self._path_udt_cabina = path_udt_cabina
		
	def obtieneRalActualCabina(self):
		path = self._path_udt_cabina+'/RAL_Actual.value'
		ral_actual = GestorTags.leeValorDeUnTag(path)
		return ral_actual


#Dado el path de la carpeta donde están los ral de los tanques de la estacion de pintura, devuelve la estructura para los botones de selector de color
def getColorsInStation(path_base):

	#Obtencion de reles disponibles
	tags_ral = system.tag.browse(path_base)
	paths_ral = map(lambda x : str(x["fullPath"]),tags_ral)
	rales = system.tag.readBlocking(paths_ral)
	rales= map(lambda x: x.value, rales)
	rales= list(set(rales))
	datos_colores = []
	for ral in rales:
		try:
			datos_colores.append(pyCache.getColorData(ral))
		except:
			datos_colores.append({"lname":str(ral), "id":str(ral)})

	#Generacion de resultado
	output=[]
	selectedStyle={"classes":""}
	unselectedStyle={"classes":""}
	
	for element in datos_colores:
		button={"text":element["lname"]+"/"+str(element["id"]),
			"value":element["id"],
			"selectedStyle":selectedStyle,
			"unselectedStyle":unselectedStyle
			}
		output.append(button)
		
	compatible_dataset=[]
	pydataset=[]
	
	return system.util.jsonEncode(output)
	#Lo que se debria hacer con la salida: system.tag.writeBlocking(self.view.params.color_selection_tag_path+"/compatible_colors", system.util.jsonEncode(output))