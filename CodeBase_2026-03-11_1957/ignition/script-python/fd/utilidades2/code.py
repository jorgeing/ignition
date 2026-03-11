def writeTagWithRetry(paths, values, retries=5):
	trial = 0
	retry = True
	while trial<retries and retry==True:
		trial = trial + 1
		result = system.tag.writeBlocking(paths, values)
		retry = False
		for r in result:
			if r.isBadOrError():
				retry=True
	if trial==retries and retry==True:
		logger = system.util.getLogger("Writing tag")
		logger.error("Writing tag: " + str(paths) + "failed") 
		return False
	else:
		return True
		
def getFullDataFromShowertrayId(showertray_id):
	logger = system.util.getLogger("getFullDataFromShowertrayId")
	query = "SELECT * FROM rfid.filtered_showertray_lifecycle WHERE showertray_id = ?"
	logger.info(query)
	resultado = system.db.runPrepQuery(query, [str(showertray_id)])
	
	if resultado.getRowCount()>0:
		#return resultado[0]
		return filaDatasetADiccionario(resultado, 0)
	else:
		return None

def filaDatasetADiccionario(dataset, row_index):
	dictionary = {}
	for c in range(dataset.getColumnCount()):
		dictionary[dataset.getColumnName(c)]=dataset.getValueAt(row_index,c)
		
	return dictionary
	
def getCurrentShiftTime():
	now = system.date.now()
	hour = system.date.getHour24(now)
	if hour >= 22 and hour < 6:
		return system.date.setTime(now, 22, 0, 0)
	elif hour >= 14 and hour < 22:
		return system.date.setTime(now, 14, 0, 0)
	else:
		return system.date.setTime(now, 6, 0, 0)
	
def getCurrentProductionDay():
	current_shift = getCurrentShiftTime()
	hour = system.date.getHour24(current_shift)
	base_day = system.date.setTime(current_shift, 0, 0, 0)
	if hour < 22 :
		return base_day
	else:
		return system.date.addDays(base_day, 1)
		
def perspectiveUserHasAnyRole(session, allowedRoles):
	roles = session.props.auth.user.roles
	# Convertir los arrays a sets para una comparación eficiente
	roles_set = set(roles)
	roles_permitidos_set = set(allowedRoles)
	# Verificar si hay alguna intersección entre los dos sets
	return not roles_set.isdisjoint(allowedRoles)

# Del sku de Dekor, crea un sku base
def getBaseSku4Dekor(sku):
	dimension = ''
	largo = sku[5:8]
	ancho=''
	if int(largo[0:1]) > 3:
		largo = sku[5:7]
		largo = '0'+largo
		ancho = sku[7:10]
		if int(ancho[0:1]) > 3:
			ancho = sku[7:9]
			ancho = '0'+ancho
		else:
			ancho = sku[7:10]
	else:
		largo = sku[5:8]
		ancho = sku[8:11]
		if int(ancho[0:1]) > 3:
			ancho = sku[8:10]
			ancho = '0'+ancho
		else:
			ancho = sku[8:11]
	dimension = largo+ancho
	return dimension
	
def construyeIdOrdenProduccion(codemp, codeje, numord):
	return str(codemp)+'_'+str(codeje)+'_'+str(int(numord))


		
		

			

			


		
