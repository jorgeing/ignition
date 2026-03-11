from fd.utilidades.dataset import *

class EventoEscaneo:
	
	TIEMPO_CURADO = 240 #minutos
	
	def __init__(self, diccionario):
		self._ejecutadorNamedQueries = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB','CodeBase')
		
		self._id_plato = diccionario['showertray_id']
		self._envasador = diccionario['worker_id']
		self._dekor = diccionario['dekor']
		
		self._codemp = fd.globales.ParametrosGlobales.obtieneCodEmp() 
		self._tiempos = self._obtieneDatasetTiemposPlato()
		self._info_plato = self._obtieneInfoPlato()
		self._clientes = self._obtieneClientes()
		self._orden_produccion = self._obtieneOrdenProduccion()
		self._tiempo_cuna = self._obtieneTiempoEnCuna()
		self._info_adicional_plato = self._obtieneInformacionAdicionalPlato()
	
	def escaneaPlatoAEnvasar(self):
		self._actualizaDatosEscaneo()
		return self._obtieneResultadoEscaneo()
	
	def _compruebaIntegridadDatos(self):
		pass
	
	def _obtieneInfoPlato(self):
		info_plato = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Envasado/ObtieneInfoPlato', {'showertray_id': self._id_plato})
		return info_plato
		
	def _obtieneInformacionAdicionalPlato(self):
		info_adicional_plato = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Etiquetas/ObtieneJsonConDatosPorID', {'s_id': self._id_plato, "company_code":fd.globales.ParametrosGlobales.obtieneCodEmp()})
		return ConversorFormatosDataset.filaDatasetADiccionario(info_adicional_plato, 0)
		
	def _obtieneTiempoEnCuna(self):
		tiempo_desmoldeo = self._tiempos['line_output']
		if tiempo_desmoldeo:
			return system.date.minutesBetween(tiempo_desmoldeo, system.date.now())
		else:
			tiempo_etiquetas = self._tiempos['rfid_label_added']
			tiempo_desmoldeo = system.date.addMinutes(tiempo_etiquetas, 20)
			return system.date.minutesBetween(tiempo_desmoldeo, system.date.now())
		
	def _obtieneDatasetTiemposPlato(self):
		dataset_tiempos = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Platos/ObtieneTiemposPlato', {'showertray_id': self._id_plato})
		if dataset_tiempos.getRowCount()>0:
			return dataset_tiempos[0]
		else:
			return []
		
	def _sePuedeEnvasar(self):
		if self._tiempo_cuna > self.TIEMPO_CURADO:
			return True
		elif self._tiempos['packaged']>0:
			return True
		else:
			return False
	
	def _obtieneColores(self):
		colores = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Envasado/ObtieneListaColores', {})
		colores_formateados = self._formateaColoresAJson(colores)
		return colores_formateados
	
	def _formateaColoresAJson(self, colores):
		sort_dataset= system.dataset.sort(colores, 'id', False)
		pydataset=system.dataset.toPyDataSet(sort_dataset)
		
		lista_colores=[]
		for fila in pydataset:
			lista_colores.append({'id':fila['id'], 'name':fila['worker_name'] + ' - ' + str(fila['id'])})
		return lista_colores
	
	def _obtieneClientes(self):
		if not self._dekor:
			clientes = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Envasado/ObtieneClientes', {'showertray_id': self._id_plato, 'company': self._codemp})
		else:
			clientes = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Envasado/ObtieneClientesDekor', {'showertray_id': self._id_plato, 'company': self._codemp})
		clientes_formateados = self._formateaClientesAJson(clientes)
		return clientes_formateados
	
	def _formateaClientesAJson(self, clientes):
		sort_dataset = system.dataset.sort(clientes, 'client_number', True)
		pydataset = system.dataset.toPyDataSet(sort_dataset)
	
		lista_clientes=[]
		objeto_cliente={}
		cliente_previo=None
		
		for fila in pydataset:
			#print(fila)
			cli_id = fila['client_number']
			cli_name = fila['client_name']
			if cli_id!=cliente_previo:
				if cliente_previo:
					lista_clientes.append(objeto_cliente)
				objeto_cliente={'id':cli_id, 'name':cli_name, 'options':[]}
				cliente_previo=cli_id
			
			objeto_cliente['options'].append({'sku':fila['sku'],'description':fila['description']})
		
		lista_clientes.append(objeto_cliente)
		
		return lista_clientes
	
	def _obtieneOrdenProduccion(self):
		orden_produccion = self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Envasado/ObtieneOrdenProduccion', {'showertray_id': self._id_plato})
		info_orden_produccion = self._obtieneInfoOrdenProduccion(orden_produccion)
		if not info_orden_produccion:
			self._obtieneSkuPredeterminado()
		return info_orden_produccion
	
	def _obtieneSkuPredeterminado(self):
		info_plato = system.dataset.toPyDataSet(self._info_plato)
		modelo = info_plato[0][0]
		color = info_plato[0][3]
		largo = info_plato[0][1][:3]
		ancho = info_plato[0][1][3:]
		generador_sku = fd.sku.GeneradorSku(modelo, color, largo, ancho)
		self._sku_generico = generador_sku.generaSkuSiNoHayOrdenPtoduccion()
	
	def _obtieneInfoOrdenProduccion(self, orden_produccion):
		info_orden_produccion = {}
		if orden_produccion.getRowCount() > 0:
			orden_produccion = system.dataset.toPyDataSet(orden_produccion)
			if orden_produccion[0][2] != None:
				info_orden_produccion = {
										'codcli': orden_produccion[0][0], 
										'referencia': orden_produccion[0][1], 
										'prodorder_id': orden_produccion[0][2],
										'description': orden_produccion[0][3],
										'client': orden_produccion[0][4]
										}
		return info_orden_produccion
	
	def _actualizaDatosEscaneo(self):
		sku, cliente = self._obtieneSkuClientePlato()
		opcion_envasado, rejilla = self._obtieneOpcionEnvasadoYRejilla(sku)
		self._ejecutadorNamedQueries.ejecutaNamedQuery('FD/Envasado/InsertaOActualizaDatosEscaneo', {'envasador': self._envasador, 'sku': sku, 'showertray_id': self._id_plato, 'cliente': cliente, 'opcion_envasado':opcion_envasado, 'rejilla':rejilla})
	
	def _obtieneSkuClientePlato(self):
		plato_ducha = fd.platos.PlatoDucha(self._id_plato)
		info_plato = plato_ducha.obtieneInfoScada()
		if info_plato:
			sku = info_plato['sku'] if info_plato['sku'] else self._sku_generico

			if info_plato['client_number'] == 218 or info_plato['client_number'] == 2182:
				cliente = 'F&D / STOCK'
			else:
				cliente = info_plato['client_name']
		else:
			sku = ''
			cliente = ''
		return sku, cliente
	
	def _obtieneOpcionEnvasadoYRejilla(self, sku): 
		opcion_envasado = sku[-3:]
		rejilla = sku[-7:-3]
		return opcion_envasado, rejilla
	
	def _obtieneResultadoEscaneo(self):
		if self._info_plato.getRowCount() > 0:
			info_plato = system.dataset.toPyDataSet(self._info_plato)
			color = {'id': info_plato[0][3], 'name': info_plato[0][4] + ' - ' + str(info_plato[0][3])}
			if len(self._orden_produccion) > 0:
				respuesta_json = {'code': 200, 'message': 'OK', 'model': info_plato[0][0], 'dimension': info_plato[0][1], 'color': color, 'clients': self._clientes, 'tiempo_cuna': self._tiempo_cuna, 'envasar': self._sePuedeEnvasar(), 'tiempo_cuna_objetivo': self.TIEMPO_CURADO, 'production_order': self._orden_produccion, 'descripcion': self._info_adicional_plato['description']}
			else:
				respuesta_json = {'code': 200, 'message': 'OK', 'model': info_plato[0][0], 'dimension': info_plato[0][1], 'color': color, 'clients': self._clientes, 'tiempo_cuna': self._tiempo_cuna, 'envasar': self._sePuedeEnvasar(), 'tiempo_cuna_objetivo': self.TIEMPO_CURADO, 'descripcion': self._info_adicional_plato['description']}
			return {'json': respuesta_json}
		else:
			return {'json':{'message':'Showertary Not Found', 'code':400}}
			