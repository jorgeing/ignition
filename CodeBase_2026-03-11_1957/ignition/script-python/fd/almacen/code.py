from fd.utilidades.dataset import *

class MovimientoAlmacen: 
	
	APLICA_DESDE_SERVIDOR=0
	APLICA_DESDE_CLIENTE=1
	
	__movimiento = {}
	__sku=""
	__incremento_unidades=0
	__lote=""
	__inventario={}
	__volumen_unidad_manipulacion=0
	
	def __init__(self, sku, incremento_unidades, lote):
		self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
		self.__sku = sku
		self.__incremento_unidades = incremento_unidades
		self.__lote = lote
		self.__calculaMovimientoMateriaPrima()
	
	@staticmethod	
	def fromIndx( indx_movimiento):
		movimientoAlmacen = MovimientoAlmacen("",0,"")
		movimientoAlmacen.__obtieneMovimientoDesdeIndx(indx_movimiento)
		return movimientoAlmacen
		
	@staticmethod
	def decodificaQR(qr):
		qr_split = qr.split('/')
		return {"sku":qr_split[0], "lote":qr_split[1]}
		
	def getMovimiento(self):
		return self.__movimiento
	
	def __calculaMovimientoMateriaPrima(self):
		self.__obtieneInventarioDeSku()
		self.__calculaMovimientoDeStock()
		
	def __obtieneMovimientoDesdeIndx(self, indx_movimiento):
		query = "SELECT * FROM raw_material.movimiento_materias_primas WHERE indx = ?"
		self.__movimiento = ConversorFormatosDataset.filaDatasetADiccionario(system.db.runPrepQuery(query, [indx_movimiento]),0)

	def __obtieneInventarioDeSku(self):
		sku_param = {"sku":str(self.__sku)}
		inventario = self._db.ejecutaNamedQuery('FD/MateriasPrimas/Inventario', sku_param)
		if inventario.getRowCount()>0:
			self.__inventario = ConversorFormatosDataset.filaDatasetADiccionario(inventario,0)
	
	def __calculaMovimientoDeStock(self):
		if self.__inventario:
			ud_inventario = self.__inventario["unidades"]
			volumen_inventario = self.__inventario["volumen"]
			volumen_unidad_manipulacion = self.__inventario["volumen_ump"]
		else:
			ud_inventario = 0
			volumen_inventario = 0
			volumen_unidad_manipulacion = self.obtieneVolumenUnidadManipulacionDeSku()
		
		ud_nueva = ud_inventario + int(self.__incremento_unidades)
		volumen_nuevo = self.__incremento_unidades + (volumen_unidad_manipulacion*int(self.__incremento_unidades))
		regularizacion_vol = self.__incremento_unidades*volumen_unidad_manipulacion
		
		t_stamp = system.date.now()
		qr = self.generaCodigoQR()
		
		movimiento_almacen = {
			"sku": self.__sku,
			"volumen": volumen_nuevo,
			"lote": self.__lote,
			"t_stamp": t_stamp,
			"regularizacion_uds": self.__incremento_unidades,
			"regularizacion_vol": regularizacion_vol,
			"qr": qr
		}
		self.__movimiento = movimiento_almacen
		
	def generaCodigoQR(self):
		return self.__sku+'/'+self.__lote
		
	
	def aplicarMovimientoAlmacen(self, lado_ejecucion):
		movimiento_almacen_ejecutado = {}
		if self.__movimiento:
			if lado_ejecucion == self.APLICA_DESDE_CLIENTE:
				indice_movimiento_almacen = self._db.ejecutaNamedQuery('CodeBase','FD/MateriasPrimas/UpdateMovimientoAlmacen', self.__movimiento, getKey = 1)
			else:
				indice_movimiento_almacen = self._db.ejecutaNamedQuery('FD/MateriasPrimas/UpdateMovimientoAlmacen', self.__movimiento, getKey = 1)
			if indice_movimiento_almacen == 0:
					logger.error('No se ha actualizado el inventario nuevo lote')
					
			movimiento_almacen_ejecutado = self.__movimiento
			print(str(movimiento_almacen_ejecutado))
			movimiento_almacen_ejecutado["indx"]=indice_movimiento_almacen
			__movimiento = movimiento_almacen_ejecutado
		return movimiento_almacen_ejecutado

	def obtieneVolumenUnidadManipulacionDeSku(self):
		volumen_unidad_manipulacion = system.db.runScalarPrepQuery('select volumen from raw_material.materias_primas where sku = ?', [self.__sku])
		if not volumen_unidad_manipulacion:
			volumen_unidad_manipulacion=0
		return volumen_unidad_manipulacion
		
	def __movimientoStockEsCorrectoYPositivo(self):
		movimiento_almacen = self.__movimiento
		return movimiento_almacen["indx"] != 0 and movimiento_almacen["regularizacion_uds"] > 0
		
	def imprimeEtiquetaMovimientoSiNecesario(self,impresora):
		if self.__movimientoStockEsCorrectoYPositivo():
			self._imprimeEtiquetaMovimiento(impresora)
		
	def _imprimeEtiquetaMovimiento(self, impresora):
		logger=system.util.getLogger("printRawMaterialLabel")
		
		movimiento_almacen=self.__movimiento
		
		#url='http://SCADA-DOLORES:9081/Integration/raw_material_label/Execute'
		url = 'http://172.16.0.29:9081/Integration/raw_material_label/Execute'
		jsondic={'sku': movimiento_almacen["sku"], 'cantidad': movimiento_almacen["regularizacion_uds"], 'indx': movimiento_almacen["indx"], 'impresora': impresora}
		json=system.util.jsonEncode(jsondic)
		
		system.net.httpPost(url,'text', json, connectTimeout=20000)
		exito=True
		
		if exito==False:
			logger.error("Error imprimiendo etiqueta de materia prima, no se pudo establecer la conexion")