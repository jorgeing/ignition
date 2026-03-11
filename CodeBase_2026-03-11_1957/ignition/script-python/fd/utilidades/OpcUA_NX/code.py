class OpcUaNX:

	OPC_SERVER = "Ignition OPC UA Server"
	NS = 1 
	BASE = "[plc_via_driver]DB.SHOWERTRAY_RECYPE"
	TAG_DESTINO = "[tags_de_prueba]db_plc_via1"
	
	headers = ["MODEL", "HEIGHT", "WIDTH", "VOLUME", "INDX"]
	prefix  = "ns=" + str(NS) + ";s="
	
	FIELD_MODELO  = "MODEL"
	FIELD_LARGO   = "HEIGHT"
	FIELD_ANCHO   = "WIDTH"
	FIELD_VOLUMEN = "VOLUME"
    
	@staticmethod
	def leerColumna(fieldName, n_ciclos, bloque_mem):
	    valores = [None] * (n_ciclos * bloque_mem)
	    for ciclo in range(n_ciclos):
	        start = ciclo * bloque_mem
	        end = start + bloque_mem
	        opcPaths = []
	        for i in range(start, end):
	            path = OpcUaNX.prefix + OpcUaNX.BASE + "[" + str(i) + "]." + fieldName
	            opcPaths.append(path)
	       	print(str(OpcUaNX.OPC_SERVER))    
	       	print(str(opcPaths))    
	        results = system.opc.readValues(OpcUaNX.OPC_SERVER, opcPaths)

	        
	        for j, r in enumerate(results):
	            valores[start + j] = r.value
	    return valores
		
	@staticmethod
	def LeerVolumenPlatosPLC(n_ciclos, bloque_mem):
		TOTAL = n_ciclos * bloque_mem
		modelos   = OpcUaNX.leerColumna("MODEL", n_ciclos, bloque_mem)
		largos    = OpcUaNX.leerColumna("HEIGHT", n_ciclos, bloque_mem)
		anchos    = OpcUaNX.leerColumna("WIDTH", n_ciclos, bloque_mem)
		volumenes = OpcUaNX.leerColumna("VOLUME", n_ciclos, bloque_mem)
		data = []
		
		for i in range(TOTAL):
		    data.append([modelos[i], largos[i], anchos[i], volumenes[i], i])  
		dataset = system.dataset.toDataSet(OpcUaNX.headers, data)
		system.tag.writeBlocking([OpcUaNX.TAG_DESTINO], [dataset])

	@staticmethod
	def EscribirVolumenPlatosPLC(idxComp, modelo, largo, ancho, volumen):
		idx = int(idxComp)
		modelo  = int(modelo)  
		largo   = int(largo)
		ancho   = int(ancho)
		volumen = int(volumen)
		
		baseIdx = OpcUaNX.BASE + "[" + str(idx) + "]."
		path_modelo  = OpcUaNX.prefix + baseIdx + OpcUaNX.FIELD_MODELO
		path_largo   = OpcUaNX.prefix + baseIdx + OpcUaNX.FIELD_LARGO
		path_ancho   = OpcUaNX.prefix + baseIdx + OpcUaNX.FIELD_ANCHO
		path_volumen = OpcUaNX.prefix + baseIdx + OpcUaNX.FIELD_VOLUMEN
		paths  = [path_modelo, path_largo, path_ancho, path_volumen]
		
		values = [modelo, largo, ancho, volumen]
		system.opc.writeValues(OpcUaNX.OPC_SERVER, paths, values)
		
	@staticmethod		
	def ActualizarTablaVolumenesSCADA(idxComp, modelo, largo, ancho, volumen):
		
		idx = int(idxComp)
		Model  = int(modelo)  
		Lenght   = int(largo)
		Width   = int(ancho)
		Volume = int(volumen)

		dataset = fd.utilidades.tags.GestorTags.leeValorDeUnTag(OpcUaNX.TAG_DESTINO)
		valores_actualizados ={"MODEL": Model, "HEIGHT": Lenght , "WIDTH": Width, "VOLUME": Volume}
		logger = system.util.getLogger("log_volumenes")
		logger.info(str(valores_actualizados))

		dataset = system.dataset.updateRow(dataset, idx, valores_actualizados)
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(OpcUaNX.TAG_DESTINO, dataset)
		
	
