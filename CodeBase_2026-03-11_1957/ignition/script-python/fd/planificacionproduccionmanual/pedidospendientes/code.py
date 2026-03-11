import fd.sku

class GestorPedidosClientes:
    
    def __init__(self):
        self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
        self._pedidos_pendientes = self._obtienePedidosPendientesClavei()
        self._planificacion_actual = self._obtienePlanificacionActualScada()
        
        self._columna_pedido = 'codped'
        self._columna_sku_pedidos = 'CodArt'      
        self._columna_sku_plan = 'referencia'      
        
        self._columnas_pedidos_clientes = self._obtieneColumnasPedidosPendientes()
    
    def _obtienePedidosPendientesClavei(self):
        pedidos_pendientes = self._db.ejecutaNamedQuery(
            'FD/PlanificacionProduccion/PlanificacionManual/ObtienePedidosPendientes', {}
        )
        return self._formateaDataset(pedidos_pendientes)
    
    def _obtienePlanificacionActualScada(self):
        planificacion_actual = self._db.ejecutaNamedQuery(
            'FD/PlanificacionProduccion/PlanificacionManual/ObtienePlanActual', {}
        )
        return self._formateaDataset(planificacion_actual)
    
    def _formateaDataset(self, dataset_crudo):
        return system.dataset.toPyDataSet(dataset_crudo)
    
    def _obtieneColumnasPedidosPendientes(self):
        return list(self._pedidos_pendientes.getColumnNames())
    
    def obtieneDatasetPedidosSinPlanificar(self):
        if not self._compruebaSiHayPedidosPendientes():
            return []
        
        lineas_planificadas = self._obtieneLineasYaPlanificadas()
        pedidos_sin_planificar = self._obtienePedidosAPlanificar(lineas_planificadas)
        return self._construyeDatasetPedidosSinPlanificar(pedidos_sin_planificar)
    
    def _compruebaSiHayPedidosPendientes(self):
        return self._pedidos_pendientes.getRowCount() > 0
    
    def _compruebaSiHayPlanificacion(self):
        return self._planificacion_actual.getRowCount() > 0
    
    def _obtieneLineasYaPlanificadas(self):
        lineas_planificadas = set()
        
        if not self._compruebaSiHayPlanificacion():
            return lineas_planificadas
        
        columnas_plan = list(self._planificacion_actual.getColumnNames())
        col_sku_plan = self._columna_sku_plan
        if col_sku_plan not in columnas_plan and 'referencia' in columnas_plan:
            col_sku_plan = 'referencia'
        
        for fila in self._planificacion_actual:
            codped = fila[self._columna_pedido]
            sku_plan = fila[col_sku_plan]
            if codped and sku_plan:
                lineas_planificadas.add((codped, sku_plan))
        
        return lineas_planificadas
            
    def _obtienePedidosAPlanificar(self, lineas_planificadas):
        pedidos_sin_planificar = []
        
        for pedido in self._pedidos_pendientes:
            codped = pedido[self._columna_pedido]
            sku_pedido = pedido[self._columna_sku_pedidos]
            
            if (codped, sku_pedido) not in lineas_planificadas:
                datos_pedido = [pedido[columna] for columna in self._columnas_pedidos_clientes]
                pedidos_sin_planificar.append(datos_pedido)
        
        return pedidos_sin_planificar

    def _construyeDatasetPedidosSinPlanificar(self, pedidos_sin_planificar):
        indice_sku = self._obtieneIndiceColumnaSku()
        
        if indice_sku is None:
            return self._creaPyDataset(
                self._columnas_pedidos_clientes,
                pedidos_sin_planificar
            )
        
        columnas_finales = self._obtieneColumnasFinalesConFlags()
        filas_finales = self._construyeFilasConFlags(pedidos_sin_planificar, indice_sku)
        
        return self._creaPyDataset(columnas_finales, filas_finales)

    def _obtieneNombreColumnaSku(self):
        return 'CodArt' 

    def _obtieneIndiceColumnaSku(self):
        nombre_columna_sku = self._obtieneNombreColumnaSku()
        try:
            return self._columnas_pedidos_clientes.index(nombre_columna_sku)
        except ValueError:
            return None

    def _obtieneColumnasFinalesConFlags(self):
        columnas = list(self._columnas_pedidos_clientes)
        columnas.append('corte')
        columnas.append('dekor')
        return columnas

    def _construyeFilasConFlags(self, pedidos_sin_planificar, indice_sku):
        filas_finales = []
        for fila in pedidos_sin_planificar:
            codigo_sku = fila[indice_sku]
            es_corte, es_dekor = self._calculaFlagsSku(codigo_sku)
            
            fila_extendida = list(fila)
            fila_extendida.append(es_corte)
            fila_extendida.append(es_dekor)
            filas_finales.append(fila_extendida)
        return filas_finales

    def _calculaFlagsSku(self, codigo_sku):
        try:
            manejador_sku = fd.sku.ManejadorSku(codigo_sku)
        except Exception, e:
            logger = system.util.getLogger('PedidosPendientes')
            logger.warn("SKU no válido en GestorPedidosClientes: %r (%s)" % (codigo_sku, e))
            return False, False
        es_corte = bool(manejador_sku.esSkuCorte())
        es_dekor = bool(manejador_sku.esSkuDekor())
        return es_corte, es_dekor

    def _creaPyDataset(self, columnas, filas):
        dataset = system.dataset.toDataSet(columnas, filas)
        return self._formateaDataset(dataset)