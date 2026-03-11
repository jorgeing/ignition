class udtSeleccionOrdenesVia:
	
	_path = ""
	_info = {}
	
	_CLIENTE_DEFECTO = 99999
	
	_CONSULTANDO = "consultando"
	_PENDIENTE_ENVIO_PLC = "pendiente_envio_plc"
	_ESTADO_SELECCION_ENVIADO_PLC = "enviado_plc"
	_NO_MOLDE = "no_molde"
	_ERROR_PLC = "error_plc"
	_ERROR_CONSULTA = "error_consulta"
	
	def __init__(self, path):
		
		self._path = path
		
	@staticmethod
	def contruyeUdtSeleccionDesdeRutaEstandarYVia(via_produccion):
		path = "[rfid_tags]seleccionOrdenes/OrdenesVia" + str(via_produccion)
		return fd.clasesordenesprod.udt.udtSeleccionOrdenesVia(path)
		
	def obtieneInfoDiccionario(self):
		self._leeTag()
		return self._info
		
	def obtieneColorActual(self):
		self._leeTag()
		return self._info["ColorSelector"]["current_color"]
		
	def obtieneIdMoldeEnCabina(self):
		self._leeTag()
		return self._info["MoldeEnCabina"]
		
	def obtieneIdMoldeEntrada(self):
		self._leeTag()
		return self._info["MoldeEsperandoEntrar"]
		
	def obtieneIdMoldeEstimadoEnCabina(self):
		self._leeTag()
		return self._info["MoldeEstimadoEnCabina"]
		
	def obtieneIdMoldeACrear(self):
		self._leeTag()
		return self._info["MoldeCrear"]
	
	def obtieneRSSI(self):
		self._leeTag()
		return self._info.get("MaxRSSI", None)

	def obtienePlatoDentroRFID(self):
		self._leeTag()
		return self._info.get("PlatoDentroRFID", None)

	def obtieneOrdenProduccionPLC_JSON(self):
		self._leeTag()
		return self._info.get("OrdenProduccionPLC", "{}")

	def obtieneOrdenProduccionSCADA_JSON(self):
		self._leeTag()
		return self._info.get("OrdenEnCabinaPinturaJSON", "{}")

	def obtieneOrdenProduccionPreferida_JSON(self):
		plc = self.obtieneOrdenProduccionPLC_JSON()
		plc_txt = (plc or "").strip()
		if plc_txt and plc_txt != "{}":
			return plc
		return self.obtieneOrdenProduccionSCADA_JSON()

	def obtieneOrdenEnCabina(self):
		self._leeTag()
		return self._info.get("OrdenEnCabinaPintura", None)

	def obtieneCodigoClienteEnCabina(self):
		self._leeTag()
		return int(self._info.get("CodigoClienteEnCabinaPintura", self._CLIENTE_DEFECTO))

	def obtieneNombreModeloCabina(self):
		self._leeTag()
		return self._info.get("NombreModeloCabina", "")

	def obtieneEstadoCabina(self):
		self._leeTag()
		return int(self._info.get("EstadoCabina", 0))

	def obtieneColoresActivosCabina(self):
		via = self._extraeNumeroVia()
		if via == 1 or via == -1:
			path_cabina = "[via_platos]Via1PinturaLlenado/Cabina1/ColoresActivos"
		else:
			path_cabina = "[via_platos]Via2Pintura/Cabina2/ColoresActivos"

		try:
			tags_ral = system.tag.browse(path_cabina)
			paths_ral = [str(x["fullPath"]) for x in tags_ral]
			reads = system.tag.readBlocking(paths_ral) if paths_ral else []
			rales = list(set([r.value for r in reads if r is not None]))
		except:
			rales = []

		datos_colores = []
		for ral in rales:
			try:
				datos_color = self._obtieneDatosColorDesdeCache(ral)
				datos_colores.append(datos_color)
			except:
				datos_colores.append({"lname": str(ral), "id": int(ral) if str(ral).isdigit() else str(ral)})

		return datos_colores

	def obtieneIdPlanActual(self):
		return fd.utilidades.tags.GestorTags.leeValorDeUnTag('[rfid_tags]ProdOrders/CurrentPlanId')

	def obtieneIdMoldeEstimado(self):
		return fd.utilidades.tags.GestorTags.leeValorDeUnTag(self._obtienePathComponente('IdMoldeEstimado'))

	def obtieneColorCreadoEnCabina(self):
		crudo = fd.utilidades.tags.GestorTags.leeValorDeUnTag(self._obtienePathComponente('RalCreadoEnCabina'))
		try:
			return int(crudo)
		except:
			return -1

	def escribeUltimoMoldePintado(self, id_molde):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(
			self._obtienePathComponente('UltimoMoldePintado'), id_molde
		)

	def escribeEstadoCabinaPintura(self, estado_int):
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(
			self._obtienePathComponente('EstadoCabina'), int(estado_int)
		)

	def escribeMoldeEntrante(self, valor):
		via = self._extraeNumeroVia()
		if via == 1:
			path = '[rfid_tags]Antennas/Molds/line1_paint_input/mold_id_anterior'
		else:
			path = '[rfid_tags]Antennas/Molds/line2_paint_input/mold_id_anterior'
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(path, valor)
	
	def usaLimiteVentanaAmpliado(self):
		self._leeTag()
		return self._info["UsarVentanaAmpliado"]
		
	def resetUsarLimiteVentanaAmpliado(self):
		self._escribeEnTagsUdt(["UsarVentanaAmpliado"], False)
		self._leeTag()
		
	def resetRecalculaOrdenProduccion(self):
		self._escribeEnTagsUdt(["RecalculaOrdenProduccion"], False)
		self._leeTag()
		
	def actualizaOrdenesCompatibles(self, dataset_ordenes):
		self._escribeEnTagsUdt(["OrdenesCompatiblesPorMoldeYColor"], [dataset_ordenes])
		self._leeTag()
		
	def actualizaOrdenSeleccionada(self, orden_seleccionada):
		orden_produccion_asignadaJSON = self._formateaOrdenProduccionAJSON(orden_seleccionada)
		self._escribeEnTagsUdt(
			["OrdenSeleccionada", "OrdenSeleccionadaJSON", "CodigoClienteSeleccionado"],
			[orden_seleccionada.obtieneInfoComoDataset(), orden_produccion_asignadaJSON, int(orden_seleccionada.obtieneIdCliente())] 
			)
		self._leeTag()
	
	def transfiereEntradaACabina(self):
		self._escribeEnTagsUdt(
			["MoldeEnCabina","MoldeEstimadoEnCabina", "OrdenEnCabinaPintura", "OrdenEnCabinaPinturaJSON", "CodigoClienteEnCabinaPintura"],
			[self._info["MoldeEsperandoEntrar"], self._info["MoldeEsperandoEntrar"] ,self._info["OrdenSeleccionada"], self._info["OrdenSeleccionadaJSON"], self._info["CodigoClienteSeleccionado"]]
			)
		self._limpiaTagsEntrada()
		self._leeTag()
	
	def transfiereEntradaACabinaSiMoldesDistintos(self):
		if self.moldeEsperandoYCabinaDistintos():
			self.transfiereEntradaACabina()
		self._leeTag()
		
	def moldeEsperandoYCabinaDistintos(self):
		return self._info["MoldeEnCabina"] != self._info["MoldeEsperandoEntrar"]
		
	def refrescaUdtParaRecalcular(self):
		molde_estimado_dentro = self.obtieneIdMoldeEstimadoEnCabina()
		molde_entrada = self.obtieneIdMoldeEntrada()
		if molde_estimado_dentro == molde_entrada:
			self._escribeEnTagsUdt(
				["MoldeEstimadoEnCabina", "OrdenEnCabinaPintura"],
				['',[]]
			)
		self._leeTag()
		
	def estableceEstadoSeleccionOrden(self, estado):
		self._escribeEnTagsUdt(["EstadoSeleccionOrden"],[estado])
	
	def copiaMoldeEstimadoACabina(self):
		self._leeTag()
		id_molde_estimado = self._info.get("MoldeEstimadoEnCabina", "")
		if id_molde_estimado:
			self._escribeEnTagsUdt(["MoldeEnCabina"], [id_molde_estimado])

	def fijaMoldeUsado(self, id_molde, nombre_modelo, estado_cabina):
		self._escribeEnTagsUdt(
			["MoldeCrear", "NombreModeloCabina", "EstadoCabina"],
			[id_molde, nombre_modelo, int(estado_cabina)]
		)

	def reescribeOrdenProduccion(self, id_orden_detallado, sku, color_id, codcli):
		orden_produccion_json = {
			'prod_order': id_orden_detallado or '',
			'sku': sku or '',
			'color': int(color_id) if color_id is not None else -1,
			'client_id': int(codcli) if codcli is not None else self._CLIENTE_DEFECTO
		}
		json_txt = system.util.jsonEncode(orden_produccion_json)

		self._escribeEnTagsUdt(
			["OrdenProduccionPLC", "OrdenEnCabinaPinturaJSON", "OrdenEnCabinaPintura", "CodigoClienteEnCabinaPintura"],
			[json_txt, json_txt, id_orden_detallado or "", int(codcli) if codcli is not None else self._CLIENTE_DEFECTO]
		)

	def limpiaOrdenEnCabinaSiMismoMolde(self):
		self.refrescaUdtParaRecalcular()

	def escribeListaColoresCompatiblesPLC(self, lista_datos_colores):
		base = "[rfid_tags]PLC_Outputs/CabinaPintura/RAL_LIST_"
		rutas_ral, rutas_nombre, valores_ral, valores_nombre = [], [], [], []
		for i in range(30):
			rutas_ral.append(base + str(i) + "_/RAL_ID")
			rutas_nombre.append(base + str(i) + "_/RAL_NAME")
			if i < len(lista_datos_colores):
				valores_ral.append(lista_datos_colores[i][0])
				valores_nombre.append(lista_datos_colores[i][1])
			else:
				valores_ral.append(0)
				valores_nombre.append('')
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(rutas_ral, valores_ral)
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(rutas_nombre, valores_nombre)
	
	def actualizaColoresCompatiblesSelector(self, botones_json):
		via = self._extraeNumeroVia()
		tag_legacy = "[rfid_tags]seleccionOrdenes/OrdenesVia{v}/ColorSelector/compatible_colors".format(v=via)
		tag_nuevo  = "[rfid_tags]seleccionOrdenes/gestorOrdenesVia{v}/SelectorColor/compatible_colors".format(v=via)
		fd.utilidades.tags.GestorTags.escribeTagsConReintento([tag_legacy, tag_nuevo], [botones_json, botones_json])
		
	def _leeTag(self):
		self._info = fd.utilidades.tags.GestorTags.leeValorDeUnTag(self._path)
		
	def _formateaOrdenProduccionAJSON(self, orden_seleccionada):
		id_orden_detallado = orden_seleccionada.obtieneIdOrdenDetallada()
		sku = orden_seleccionada.obtieneSku()
		color = orden_seleccionada.obtieneIdColor()
		codigo_cliente = orden_seleccionada.obtieneIdCliente()
		orden_produccion_json = {'prod_order': id_orden_detallado, 'sku':sku, 'color':color, 'client_id':codigo_cliente}
		return system.util.jsonEncode(orden_produccion_json)
		
	def _limpiaTagsEntrada(self):
		self._escribeEnTagsUdt(
			["OrdenSeleccionada", "OrdenSeleccionadaJSON", "CodigoClienteSeleccionado"], 
			[None, "{}",self._CLIENTE_DEFECTO ]
		)
		self._leeTag()
		
	def _obtienePathComponente(self, path_relativo):
		return self._path + "/" + path_relativo
		
	def _escribeEnTagsUdt(self, lista_paths_relativos, lista_valores):
		lista_paths_absolutos = [self._obtienePathComponente(x) for x in lista_paths_relativos]
		fd.utilidades.tags.GestorTags.escribeTagsConReintento(lista_paths_absolutos, lista_valores)
	
	def _obtieneDatosColorDesdeCache(self, ral):
		try:
			ds = system.dataset.toPyDataSet(system.tag.readBlocking(['[rfid_tags]Cache/ColorsDataset'])[0].value)
			lista_rales = ds.getColumnAsList(0)
			idx = lista_rales.index(int(ral) if str(ral).isdigit() else ral)
			fila = ConversorFormatosDataset.filaDatasetADiccionario(ds, idx)
			return {"id": int(fila["id"]), "lname": str(fila["lname"])}
		except:
			return {"id": int(ral) if str(ral).isdigit() else str(ral), "lname": str(ral)}

	def _extraeNumeroVia(self):
		try:
			import re
			m = re.search(r"OrdenesVia(-?\d+)", self._path or "")
			return int(m.group(1)) if m else 1
		except:
			return 1