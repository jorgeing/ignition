from fd.utilidades.dataset import *
from fd.utilidades.sql import *

class Produccion():
	
	_query_obtener = "FD/PowerBI/ObtenerObjetivosProduccion"
	_query_actualizar = "FD/PowerBI/ActualizarObjetivosProduccion"
	_query_insertar = "FD/PowerBI/InsertarObjetivosProduccion"
	
	def __init__(self):
		pass
		
	def construyeTabla(self):
		datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_produccion","CodeBase").ejecutaNamedQuery(self._query_obtener, {})
		datos_formateados = self._formateaDatos(datos)
		datos_reestructurados = self._reestructuraDatos(datos_formateados)
		datos_con_estilo = self._generaJSONconEstilo(datos_reestructurados)
		return datos_con_estilo
		
	def _formateaDatos(self, datos):
		datos_formateados = []
		for indice_fila in range(datos.getRowCount()):
			fila_formateada = ConversorFormatosDataset.filaDatasetADiccionario(datos, indice_fila)
			datos_formateados.append(fila_formateada)
		return datos_formateados
	
	def _reestructuraDatos(self, datos):
	    datos_reestructurados = []
	    fila_reestructurada = None
	    for fila in datos:
	        fecha = fila['production_date']
	        turno = fila['shift']
	        objetivo = fila['production_target']
	        pour = fila['pour']
	        pack = fila['pack']
	        # Crear nueva fila si es necesario
	        fila_reestructurada, es_nueva_fecha = self._verificaFechaNueva(fila_reestructurada, fecha, turno, objetivo, pour, pack)
	        # Si es una nueva fecha y la fila previa está completa, se añade al dataset
	        if es_nueva_fecha and fila_reestructurada is not None:
	            datos_reestructurados.append(fila_reestructurada)
	    # Añadir la última fila después del bucle
	    if fila_reestructurada is not None:
	        datos_reestructurados.append(fila_reestructurada)
	    return datos_reestructurados
	
	def _verificaFechaNueva(self, fila_reestructurada, fecha, turno, objetivo, pour, pack):
	    es_nueva_fecha = False
	    if fila_reestructurada is None or fila_reestructurada['Fecha'] != fecha:
	        es_nueva_fecha = True
	        # Si ya existe una fila previa, devolver esa y luego crear una nueva
	        fila_reestructurada = {
	            "Fecha": fecha,
	            "Objetivo Turno 1": None,
	            "Objetivo Turno 2": None,
	            "Objetivo Turno 3": None,
	            "Pour Tuno 1": None,
	            "Pour Tuno 2": None,
	            "Pour Tuno 3": None,
	            "Pack Tuno 1": None,
	            "Pack Tuno 2": None,
	            "Pack Tuno 3": None
	        }
	    # Asignar el objetivo al turno correcto
	    fila_reestructurada = self._asignaObjetivo(fila_reestructurada, turno, objetivo, pour, pack)
	    return fila_reestructurada, es_nueva_fecha
	
	def _asignaObjetivo(self, fila_reestructurada, turno, objetivo, pour, pack):
	    if turno == 1:
	        fila_reestructurada["Objetivo Turno 1"] = objetivo
	        fila_reestructurada["Pour Turno 1"] = pour
	        fila_reestructurada["Pack Turno 1"] = pack
	    elif turno == 2:
	        fila_reestructurada["Objetivo Turno 2"] = objetivo
	        fila_reestructurada["Pour Turno 2"] = pour
	        fila_reestructurada["Pack Turno 2"] = pack
	    elif turno == 3:
	        fila_reestructurada["Objetivo Turno 3"] = objetivo
	        fila_reestructurada["Pour Turno 3"] = pour
	        fila_reestructurada["Pack Turno 3"] = pack
	    return fila_reestructurada
	    
	def _generaJSONconEstilo(self, datos):
		output_json = []
		
		estilo_coral = {"backgroundColor": "khaki"}
		estilo_blanco = {"backgroundColor": "white"}
		
		for fila in datos:
			objeto_fila = {}
			estilo_fila = {}
			
			fecha = fila.get("Fecha")
			if fecha:
				dia_semana = system.date.getDayOfWeek(system.date.parse(fecha, "yyyy-MM-dd"))
				if dia_semana == 1 or dia_semana == 7:
					estilo_fila = estilo_coral
				else:
					estilo_fila = estilo_blanco
					
			objeto_fila['value'] = fila
			objeto_fila['style'] = estilo_fila
			
			output_json.append(objeto_fila)
			
		return output_json
	    
	def actualizaDatos(self, datos, fechaInicio, fechaFin, objetivoT1, objetivoT2, objetivoT3, pourT1, pourT2, pourT3, packT1, packT2, packT3):
		fechaInicio, fechaFin = self._compruebaFechas(datos, fechaInicio, fechaFin)
		try:
			self._actualizaFilasEnBaseDatos(fechaInicio, fechaFin, objetivoT1, objetivoT2, objetivoT3, pourT1, pourT2, pourT3, packT1, packT2, packT3)
		except Exception as e:
			raise Exception('Error al actualizar base de datos: '+ str(e))
		datos_actualizados = self.construyeTabla()
		return datos_actualizados
	
	def _actualizaFilasEnBaseDatos(self, fechaInicio, fechaFin, objetivoT1, objetivoT2, objetivoT3, pourT1, pourT2, pourT3, packT1, packT2, packT3):
		parametros = {
			"fecha_inicio": fechaInicio,
			"objetivoT1": objetivoT1,
			"objetivoT2": objetivoT2,
			"objetivoT3": objetivoT3,
			"fecha_fin": fechaFin,
			"pourT1": pourT1,
			"pourT2": pourT2,
			"pourT3": pourT3,
			"packT1": packT1,
			"packT2": packT2,
			"packT3": packT3
		}
		EjecutadorNamedQueriesConContexto("powerbi.objetivos_produccion","CodeBase").ejecutaNamedQuery(self._query_actualizar, parametros)
	
	def _compruebaFechas(self, datos, fechaInicio, fechaFin):
		if fechaInicio is None and fechaFin is not None:
			fechaInicio = datos[0]["Fecha"]
			fechaInicio = system.date.parse(fechaInicio, "dd-MM-yyyy")
		elif fechaInicio is not None and fechaFin is None:
			fechaFin = datos[-1]["Fecha"]
			fechaFin = system.date.parse(fechaFin, "dd-MM-yyyy")
		return fechaInicio, fechaFin
		
	def anyadeObjetivosHastaManana(self):
	    # Obtener todos los datos existentes
	    datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_produccion", "CodeBase").ejecutaNamedQuery(self._query_obtener, {})
	    
	    # Obtener el último día registrado y sus datos
	    ultimo_dia = self._obtieneUltimoDiaRegistrado(datos)
	    print('Último día: ' + str(ultimo_dia))
	    siguiente_fecha_ultimo_dia = system.date.addDays(ultimo_dia, 1)
	    print('Siguiente fecha último día: ' + str(siguiente_fecha_ultimo_dia))
	    
	    # Determinar la fecha de mañana
	    fecha_manana = system.date.addDays(system.date.now(), 1)
	    print('Mañana: ' + str(fecha_manana))
	    
	    while system.date.isBefore(siguiente_fecha_ultimo_dia, fecha_manana) or siguiente_fecha_ultimo_dia == fecha_manana:
	        datos_a_insertar = self._obtieneDatosAInsertar(siguiente_fecha_ultimo_dia, datos)
	        if not self._existenDatosParaFecha(siguiente_fecha_ultimo_dia, datos):
	            self._insertaFilasParaFecha(siguiente_fecha_ultimo_dia, datos_a_insertar)
	        siguiente_fecha_ultimo_dia = system.date.addDays(siguiente_fecha_ultimo_dia, 1)
	
	def _existenDatosParaFecha(self, fecha, datos):
	    fecha_formateada = self._formateaFecha(fecha)
	    for fila in datos:
	        if self._formateaFecha(fila["production_date"]) == fecha_formateada:
	            return True
	    return False
	
	def _obtieneUltimoDiaRegistrado(self, datos):
	    ultimo_dia = None
	    for i in range(datos.getRowCount()):
	        fecha_fila = system.date.parse(self._formateaFecha(datos.getValueAt(i, "production_date")), "yyyy-MM-dd")
	        if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	            ultimo_dia = fecha_fila
	    return ultimo_dia
	
	def _obtieneDatosUltimoDiaPorTipo(self, datos, es_finde):
	    ultimo_dia = None
	    datos_ultimo_dia = []
	    for fila in datos:
	        fecha_fila = system.date.parse(self._formateaFecha(fila["production_date"]), "yyyy-MM-dd")
	        dia_semana = system.date.getDayOfWeek(fecha_fila)
	        # Condición para días entre semana o fines de semana
	        if (es_finde and dia_semana in [1, 7]) or (not es_finde and 2 <= dia_semana <= 6):
	            if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	                ultimo_dia = fecha_fila
	    
	    # Filtrar datos correspondientes al último día encontrado
	    if ultimo_dia:
	        datos_ultimo_dia = [
	            f for f in datos if self._formateaFecha(f["production_date"]) == self._formateaFecha(ultimo_dia)
	        ]
	    return datos_ultimo_dia
	
	def _obtieneDatosAInsertar(self, siguiente_fecha_ultimo_dia, datos):
	    dia_semana_siguiente_fecha_ultimo_dia = system.date.getDayOfWeek(siguiente_fecha_ultimo_dia)
	    es_finde = dia_semana_siguiente_fecha_ultimo_dia in [1, 7]
	    datos_a_insertar = self._obtieneDatosUltimoDiaPorTipo(datos, es_finde)
	    print('Datos a insertar: ' + str(datos_a_insertar))
	    return datos_a_insertar
	
	def _insertaFilasParaFecha(self, fecha, datos_ultimo_dia):
	    for fila in datos_ultimo_dia:
	        turno = fila["shift"]
	        objetivo = fila["production_target"]
	        parametros = {
	            "fecha": self._formateaFecha(fecha),
	            "turno": turno,
	            "objetivo": objetivo,
	            "codemp": 1,
	            "pour": True,
	            "pack": True
	        }
	        try:
	            EjecutadorNamedQueriesConContexto("powerbi.objetivos_produccion", "CodeBase").ejecutaNamedQuery(self._query_insertar, parametros)
	            print("Fila insertada con éxito")
	        except Exception as e:
	            print("Error al insertar fila: ", e)
	
	def _formateaFecha(self, fecha):
	    return system.date.format(fecha, "yyyy-MM-dd")


class Productividad():
	
	_query_obtener = "FD/PowerBI/ObtenerObjetivosProductividad"
	_query_actualizar = "FD/PowerBI/ActualizarObjetivosProductividad"
	_query_insertar = "FD/PowerBI/InsertarObjetivosProductividad"
	
	def __init__(self):
		pass
		
	def construyeTabla(self):
		datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_productividad","CodeBase").ejecutaNamedQuery(self._query_obtener, {})
		datos_formateados = self._formateaDatos(datos)
		datos_reestructurados = self._reestructuraDatos(datos_formateados)
		output_json = self._generaJSONconEstilo(datos_reestructurados)
		return output_json
		
	def _formateaDatos(self, datos):
		datos_formateados = []
		for indice_fila in range(datos.getRowCount()):
			fila_formateada = ConversorFormatosDataset.filaDatasetADiccionario(datos, indice_fila)
			datos_formateados.append(fila_formateada)
		return datos_formateados
		
	def _reestructuraDatos(self, datos):
	    datos_reestructurados = []
	    for fila in datos:
	        fecha = fila['productivity_date']
	        objetivo = fila['productivity_target']
	        fila_reestructurada = {
	            "Fecha": fecha,
	            "Objetivo": objetivo
	        }
	        datos_reestructurados.append(fila_reestructurada)
	    return datos_reestructurados
	    
	def _generaJSONconEstilo(self, datos):
		output_json = []
		
		estilo_coral = {"backgroundColor": "khaki"}
		estilo_blanco = {"backgroundColor": "white"}
		
		for fila in datos:
			objeto_fila = {}
			estilo_fila = {}
			
			fecha = fila.get("Fecha")
			if fecha:
				dia_semana = system.date.getDayOfWeek(system.date.parse(fecha, "yyyy-MM-dd"))
				if dia_semana == 1 or dia_semana == 7:
					estilo_fila = estilo_coral
				else:
					estilo_fila = estilo_blanco
					
			objeto_fila['value'] = fila
			objeto_fila['style'] = estilo_fila
			
			output_json.append(objeto_fila)
			
		return output_json
	
	def actualizaDatos(self, datos, fechaInicio, fechaFin, objetivo):
		fechaInicio, fechaFin = self._compruebaFechas(datos, fechaInicio, fechaFin)
		try:
			self._actualizaFilasEnBaseDatos(fechaInicio, fechaFin, objetivo)
		except Exception as e:
			raise Exception('Error al actualizar base de datos: '+str(e))
		datos_actualizados = self.construyeTabla()
		return datos_actualizados
	
	def _actualizaFilasEnBaseDatos(self, fechaInicio, fechaFin, objetivo):
		parametros = {
			"fecha_inicio": fechaInicio,
			"objetivo": objetivo,
			"fecha_fin": fechaFin
		}
		EjecutadorNamedQueriesConContexto("powerbi.objetivos_productividad","CodeBase").ejecutaNamedQuery(self._query_actualizar, parametros)
	
	def _compruebaFechas(self, datos, fechaInicio, fechaFin):
		if fechaInicio is None and fechaFin is not None:
			fechaInicio = datos[0]["Fecha"]
			fechaInicio = system.date.parse(fechaInicio, "dd-MM-yyyy")
		elif fechaInicio is not None and fechaFin is None:
			fechaFin = datos[-1]["Fecha"]
			fechaFin = system.date.parse(fechaFin, "dd-MM-yyyy")
		return fechaInicio, fechaFin
	
	def anyadeObjetivosHastaManana(self):
	    # Obtener todos los datos existentes
	    datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_productividad", "CodeBase").ejecutaNamedQuery(self._query_obtener, {})
	    
	    # Obtener el último día y sus datos
	    ultimo_dia = self._obtieneUltimoDiaRegistrado(datos)
	    print('ultimo dia: ' + str(ultimo_dia))
	    # Determinar la fecha de mañana
	    fecha_manana = system.date.addDays(system.date.now(), 1)
	    print('mañana: ' + str(fecha_manana))
	    # Insertar filas desde el día siguiente al último día hasta mañana
	    siguiente_fecha_ultimo_dia = system.date.addDays(ultimo_dia, 1)
	    print('Siguiente fecha último día: ' + str(siguiente_fecha_ultimo_dia))
	    while system.date.isBefore(siguiente_fecha_ultimo_dia, fecha_manana) or siguiente_fecha_ultimo_dia == fecha_manana:
	    	objetivo_a_insertar = self._obtieneObjetivoAInsertar(siguiente_fecha_ultimo_dia, datos)
	        self._insertaFilaParaFecha(siguiente_fecha_ultimo_dia, objetivo_a_insertar)
	        siguiente_fecha_ultimo_dia = system.date.addDays(siguiente_fecha_ultimo_dia, 1)
	
	def _obtieneUltimoDiaRegistrado(self, datos):
	    ultimo_dia = None
	    for i in range(datos.getRowCount()):
	    	fecha_fila = system.date.parse(self._formateaFecha(datos.getValueAt(i, "productivity_date")), "yyyy-MM-dd")
	    	if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	    		ultimo_dia = fecha_fila
	    return ultimo_dia
	
	def _obtieneObjetivoAInsertar(self, siguiente_fecha_ultimo_dia, datos):
	    objetivo_a_insertar = None
	    dia_semana_siguiente_fecha_ultimo_dia = system.date.getDayOfWeek(siguiente_fecha_ultimo_dia)
	    if dia_semana_siguiente_fecha_ultimo_dia >= 2 and dia_semana_siguiente_fecha_ultimo_dia <= 6:
	    	objetivo_a_insertar = self._obtieneObjetivoUltimoDiaEntreSemana(datos)
	    else:
	    	objetivo_a_insertar = 0
	    return objetivo_a_insertar
	
	def _obtieneObjetivoUltimoDiaEntreSemana(self, datos):
	    # Determinar el último día que sea entre semana (lunes a viernes) disponible en los datos
	    ultimo_dia = None
	    objetivo_ultimo_dia = None
	    for fila in datos:
	        fecha_fila = system.date.parse(self._formateaFecha(fila["productivity_date"]), "yyyy-MM-dd")
	        dia_semana = system.date.getDayOfWeek(fecha_fila)
	        # Verificar si es entre semana (lunes a viernes)
	        if dia_semana >= 2 and dia_semana <= 6:  # Lunes (2) a Viernes (6)
	            if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	                ultimo_dia = fecha_fila
	                objetivo_ultimo_dia = fila["productivity_target"]
	    return objetivo_ultimo_dia    
	
	def _insertaFilaParaFecha(self, fecha, objetivo):
	    parametros = {
	        "fecha": self._formateaFecha(fecha),
	        "codemp": 1,
	        "objetivo": objetivo
	    }
	    try:
	        EjecutadorNamedQueriesConContexto("powerbi.objetivos_productividad", "CodeBase").ejecutaNamedQuery(self._query_insertar, parametros)
	        print("Fila insertada con éxito")
	    except Exception as e:
	        print("Error al insertar fila: ",e)
	
	def _formateaFecha(self, fecha):
	    return system.date.format(fecha, "yyyy-MM-dd")


class Scrap():
	
	_query_obtener = "FD/PowerBI/ObtenerObjetivosScrap"
	_query_actualizar = "FD/PowerBI/ActualizarObjetivosScrap"
	_query_insertar = "FD/PowerBI/InsertarObjetivosScrap"
	
	def __init__(self):
		pass
		
	def construyeTabla(self):
		datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_scrap","CodeBase").ejecutaNamedQuery(self._query_obtener, {})
		datos_formateados = self._formateaDatos(datos)
		datos_reestructurados = self._reestructuraDatos(datos_formateados)
		output_json = self._generaJSONconEstilo(datos_reestructurados)
		return output_json
	
	def _formateaDatos(self, datos):
		datos_formateados = []
		for indice_fila in range(datos.getRowCount()):
			fila_formateada = ConversorFormatosDataset.filaDatasetADiccionario(datos, indice_fila)
			datos_formateados.append(fila_formateada)
		return datos_formateados
		
	def _reestructuraDatos(self, datos):
	    datos_reestructurados = []
	    for fila in datos:
	        fecha = fila['scrap_date']
	        objetivo = fila['scrap_target']
	        if objetivo == None:
	        	objetivo = 0
	        else:
	        	objetivo = objetivo*100
	        fila_reestructurada = {
	            "Fecha": fecha,
	            "Objetivo (%)": objetivo
	        }
	        datos_reestructurados.append(fila_reestructurada)
	    return datos_reestructurados
	    
	def _generaJSONconEstilo(self, datos):
		output_json = []
		
		estilo_coral = {"backgroundColor": "khaki"}
		estilo_blanco = {"backgroundColor": "white"}
		
		for fila in datos:
			objeto_fila = {}
			estilo_fila = {}
			
			fecha = fila.get("Fecha")
			if fecha:
				dia_semana = system.date.getDayOfWeek(system.date.parse(fecha, "yyyy-MM-dd"))
				if dia_semana == 1 or dia_semana == 7:
					estilo_fila = estilo_coral
				else:
					estilo_fila = estilo_blanco
					
			objeto_fila['value'] = fila
			objeto_fila['style'] = estilo_fila
			
			output_json.append(objeto_fila)
			
		return output_json
	
	def actualizaDatos(self, datos, fechaInicio, fechaFin, objetivo):
		print('Objetivo: '+str(objetivo))
		objetivo = float(objetivo)/100
		print('Objetivo (%): ' +str(objetivo))
		fechaInicio, fechaFin = self._compruebaFechas(datos, fechaInicio, fechaFin)
		try:
			self._actualizaFilasEnBaseDatos(fechaInicio, fechaFin, objetivo)
		except Exception as e:
			raise Exception('Error al actualizar base de datos: '+str(e))
		datos_actualizados = self.construyeTabla()
		return datos_actualizados
	
	def _actualizaFilasEnBaseDatos(self, fechaInicio, fechaFin, objetivo):
		parametros = {
			"fecha_inicio": fechaInicio,
			"objetivo": objetivo,
			"fecha_fin": fechaFin
		}
		EjecutadorNamedQueriesConContexto("powerbi.objetivos_scrap","CodeBase").ejecutaNamedQuery(self._query_actualizar, parametros)
	
	def _compruebaFechas(self, datos, fechaInicio, fechaFin):
		if fechaInicio is None and fechaFin is not None:
			fechaInicio = datos[0]["Fecha"]
			fechaInicio = system.date.parse(fechaInicio, "dd-MM-yyyy")
		elif fechaInicio is not None and fechaFin is None:
			fechaFin = datos[-1]["Fecha"]
			fechaFin = system.date.parse(fechaFin, "dd-MM-yyyy")
		return fechaInicio, fechaFin
	
	def anyadeObjetivosHastaManana(self):
	    # Obtener todos los datos existentes
	    datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_scrap", "CodeBase").ejecutaNamedQuery(self._query_obtener, {})
	    
	    # Obtener el último día que sea entre semana y sus datos
	    ultimo_dia = self._obtieneUltimoDiaRegistrado(datos)
	    # Determinar la fecha de mañana
	    fecha_manana = system.date.addDays(system.date.now(), 1)
	    # Insertar filas desde el día siguiente al último día hasta mañana
	    siguiente_fecha_ultimo_dia = system.date.addDays(ultimo_dia, 1)
	    while system.date.isBefore(siguiente_fecha_ultimo_dia, fecha_manana) or siguiente_fecha_ultimo_dia == fecha_manana:
	    	objetivo_a_insertar = self._obtieneObjetivoAInsertar(siguiente_fecha_ultimo_dia, datos)
	        self._insertaFilaParaFecha(siguiente_fecha_ultimo_dia, objetivo_a_insertar)
	        siguiente_fecha_ultimo_dia = system.date.addDays(siguiente_fecha_ultimo_dia, 1)
	
	def _obtieneUltimoDiaRegistrado(self, datos):
	    ultimo_dia = None
	    for i in range(datos.getRowCount()):
	    	fecha_fila = system.date.parse(self._formateaFecha(datos.getValueAt(i, "scrap_date")), "yyyy-MM-dd")
	    	if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	    		ultimo_dia = fecha_fila
	    return ultimo_dia
	
	def _obtieneObjetivoAInsertar(self, siguiente_fecha_ultimo_dia, datos):
	    objetivo_a_insertar = None
	    dia_semana_siguiente_fecha_ultimo_dia = system.date.getDayOfWeek(siguiente_fecha_ultimo_dia)
	    if dia_semana_siguiente_fecha_ultimo_dia >= 2 and dia_semana_siguiente_fecha_ultimo_dia <= 6:
	    	objetivo_a_insertar = self._obtieneObjetivoUltimoDiaEntreSemana(datos)
	    else:
	    	objetivo_a_insertar = 0
	    return objetivo_a_insertar
	
	def _obtieneObjetivoUltimoDiaEntreSemana(self, datos):
	    # Determinar el último día que sea entre semana (lunes a viernes) disponible en los datos
	    ultimo_dia = None
	    objetivo_ultimo_dia = None
	    for fila in datos:
	        fecha_fila = system.date.parse(self._formateaFecha(fila["scrap_date"]), "yyyy-MM-dd")
	        dia_semana = system.date.getDayOfWeek(fecha_fila)
	        # Verificar si es entre semana (lunes a viernes)
	        if dia_semana >= 2 and dia_semana <= 6:  # Lunes (2) a Viernes (6)
	            if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	                ultimo_dia = fecha_fila
	                objetivo_ultimo_dia = fila["scrap_target"]
	    return objetivo_ultimo_dia    
	
	def _insertaFilaParaFecha(self, fecha, objetivo):

	    parametros = {
	        "fecha": self._formateaFecha(fecha),
	        "codemp": 1,
	        "objetivo": objetivo
	    }
	    try:
	        EjecutadorNamedQueriesConContexto("powerbi.objetivos_scrap", "CodeBase").ejecutaNamedQuery(self._query_insertar, parametros)
	        print("Fila insertada con éxito")
	    except Exception as e:
	        print("Error al insertar fila: ",e)
	
	def _formateaFecha(self, fecha):
	    return system.date.format(fecha, "yyyy-MM-dd")

class Retrabajo():
	
	_query_obtener = "FD/PowerBI/ObtenerObjetivosRetrabajo"
	_query_actualizar = "FD/PowerBI/ActualizarObjetivosRetrabajo"
	_query_insertar = "FD/PowerBI/InsertarObjetivosRetrabajo"
	
	def __init__(self):
		pass
		
	def construyeTabla(self):
		datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_retrabajo","CodeBase").ejecutaNamedQuery(self._query_obtener, {})
		datos_formateados = self._formateaDatos(datos)
		datos_reestructurados = self._reestructuraDatos(datos_formateados)
		output_json = self._generaJSONconEstilo(datos_reestructurados)
		return output_json
	
	def _formateaDatos(self, datos):
		datos_formateados = []
		for indice_fila in range(datos.getRowCount()):
			fila_formateada = ConversorFormatosDataset.filaDatasetADiccionario(datos, indice_fila)
			datos_formateados.append(fila_formateada)
		return datos_formateados
		
	def _reestructuraDatos(self, datos):
	    datos_reestructurados = []
	    for fila in datos:
	        fecha = fila['rework_date']
	        objetivo = fila['rework_target']
	        if objetivo == None:
	        	objetivo = 0
	        else:
	        	objetivo = objetivo*100
	        fila_reestructurada = {
	            "Fecha": fecha,
	            "Objetivo (%)": objetivo
	        }
	        datos_reestructurados.append(fila_reestructurada)
	    return datos_reestructurados
	    
	def _generaJSONconEstilo(self, datos):
		output_json = []
		
		estilo_coral = {"backgroundColor": "khaki"}
		estilo_blanco = {"backgroundColor": "white"}
		
		for fila in datos:
			objeto_fila = {}
			estilo_fila = {}
			
			fecha = fila.get("Fecha")
			if fecha:
				dia_semana = system.date.getDayOfWeek(system.date.parse(fecha, "yyyy-MM-dd"))
				if dia_semana == 1 or dia_semana == 7:
					estilo_fila = estilo_coral
				else:
					estilo_fila = estilo_blanco
					
			objeto_fila['value'] = fila
			objeto_fila['style'] = estilo_fila
			
			output_json.append(objeto_fila)
			
		return output_json
	
	def actualizaDatos(self, datos, fechaInicio, fechaFin, objetivo):
		print('Objetivo: '+str(objetivo))
		objetivo = float(objetivo)/100
		print('Objetivo (%): ' +str(objetivo))
		fechaInicio, fechaFin = self._compruebaFechas(datos, fechaInicio, fechaFin)
		try:
			self._actualizaFilasEnBaseDatos(fechaInicio, fechaFin, objetivo)
		except Exception as e:
			raise Exception('Error al actualizar base de datos: '+str(e))
		datos_actualizados = self.construyeTabla()
		return datos_actualizados
	
	def _actualizaFilasEnBaseDatos(self, fechaInicio, fechaFin, objetivo):
		parametros = {
			"fecha_inicio": fechaInicio,
			"objetivo": objetivo,
			"fecha_fin": fechaFin
		}
		EjecutadorNamedQueriesConContexto("powerbi.objetivos_retrabajo","CodeBase").ejecutaNamedQuery(self._query_actualizar, parametros)
	
	def _compruebaFechas(self, datos, fechaInicio, fechaFin):
		if fechaInicio is None and fechaFin is not None:
			fechaInicio = datos[0]["Fecha"]
			fechaInicio = system.date.parse(fechaInicio, "dd-MM-yyyy")
		elif fechaInicio is not None and fechaFin is None:
			fechaFin = datos[-1]["Fecha"]
			fechaFin = system.date.parse(fechaFin, "dd-MM-yyyy")
		return fechaInicio, fechaFin
	
	def anyadeObjetivosHastaManana(self):
	    # Obtener todos los datos existentes
	    datos = EjecutadorNamedQueriesConContexto("powerbi.objetivos_retrabajo", "CodeBase").ejecutaNamedQuery(self._query_obtener, {})
	    
	    # Obtener el último día que sea entre semana y sus datos
	    ultimo_dia = self._obtieneUltimoDiaRegistrado(datos)
	    # Determinar la fecha de mañana
	    fecha_manana = system.date.addDays(system.date.now(), 1)
	    # Insertar filas desde el día siguiente al último día hasta mañana
	    siguiente_fecha_ultimo_dia = system.date.addDays(ultimo_dia, 1)
	    while system.date.isBefore(siguiente_fecha_ultimo_dia, fecha_manana) or siguiente_fecha_ultimo_dia == fecha_manana:
	    	objetivo_a_insertar = self._obtieneObjetivoAInsertar(siguiente_fecha_ultimo_dia, datos)
	        self._insertaFilaParaFecha(siguiente_fecha_ultimo_dia, objetivo_a_insertar)
	        siguiente_fecha_ultimo_dia = system.date.addDays(siguiente_fecha_ultimo_dia, 1)
	
	def _obtieneUltimoDiaRegistrado(self, datos):
	    ultimo_dia = None
	    for i in range(datos.getRowCount()):
	    	fecha_fila = system.date.parse(self._formateaFecha(datos.getValueAt(i, "rework_date")), "yyyy-MM-dd")
	    	if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	    		ultimo_dia = fecha_fila
	    return ultimo_dia
	
	def _obtieneObjetivoAInsertar(self, siguiente_fecha_ultimo_dia, datos):
	    objetivo_a_insertar = None
	    dia_semana_siguiente_fecha_ultimo_dia = system.date.getDayOfWeek(siguiente_fecha_ultimo_dia)
	    if dia_semana_siguiente_fecha_ultimo_dia >= 2 and dia_semana_siguiente_fecha_ultimo_dia <= 6:
	    	objetivo_a_insertar = self._obtieneObjetivoUltimoDiaEntreSemana(datos)
	    else:
	    	objetivo_a_insertar = 0
	    return objetivo_a_insertar
	
	def _obtieneObjetivoUltimoDiaEntreSemana(self, datos):
	    # Determinar el último día que sea entre semana (lunes a viernes) disponible en los datos
	    ultimo_dia = None
	    objetivo_ultimo_dia = None
	    for fila in datos:
	        fecha_fila = system.date.parse(self._formateaFecha(fila["rework_date"]), "yyyy-MM-dd")
	        dia_semana = system.date.getDayOfWeek(fecha_fila)
	        # Verificar si es entre semana (lunes a viernes)
	        if dia_semana >= 2 and dia_semana <= 6:  # Lunes (2) a Viernes (6)
	            if ultimo_dia is None or system.date.isAfter(fecha_fila, ultimo_dia):
	                ultimo_dia = fecha_fila
	                objetivo_ultimo_dia = fila["rework_target"]
	    return objetivo_ultimo_dia    
	
	def _insertaFilaParaFecha(self, fecha, objetivo):

	    parametros = {
	        "fecha": self._formateaFecha(fecha),
	        "codemp": 1,
	        "objetivo": objetivo
	    }
	    try:
	        EjecutadorNamedQueriesConContexto("powerbi.objetivos_retrabajo", "CodeBase").ejecutaNamedQuery(self._query_insertar, parametros)
	        print("Fila insertada con éxito")
	    except Exception as e:
	        print("Error al insertar fila: ",e)
	
	def _formateaFecha(self, fecha):
	    return system.date.format(fecha, "yyyy-MM-dd")