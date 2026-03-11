"""
Procesador de antenas RFID. Refactorizado con IA, validar antes
"""


class ProcesadorAntena2(object):
    """
    Procesa lecturas RFID de una antena industrial.
    
    Recibe datos sin procesar de una antena RFID, los clasifica automáticamente
    en moldes y etiquetas, y devuelve un resumen estructurado con estadísticas
    de cada lectura (cuántas veces se leyó, timestamps, potencia de señal).
    
    Soporta datos en formato JSON o diccionario Python.
    
    Ejemplo:
        procesador = ProcesadorAntena("ANT-01", datos_json, historico_previo)
        resultado = procesador.procesar()
        print resultado["molds"]      # Moldes detectados
        print resultado["labels"]     # Etiquetas detectadas
    """

    def __init__(self, nombre_antena, datos_lectura, objeto_destino_inicial, usa_formato_plano=False):
        """
        Inicializa el procesador.
        
        Args:
            nombre_antena (str): Identificador de la antena
            datos_lectura (dict|str): Datos de lectura en formato JSON o string
            objeto_destino_inicial (dict): Resultado anterior (para histórico)
            usa_formato_plano (bool): True para string, False para JSON/dict
        """
        self.nombre_antena = nombre_antena
        self.datos_lectura = datos_lectura
        self.usa_formato_plano = usa_formato_plano
        self.objeto_destino_inicial = objeto_destino_inicial or {}

        # Dependencias externas
        self._inicializarDependencias()
        
        # Estado interno
        self.estado_antena = 3
        self.tags_antenna = []
        
        # Resultados procesados
        self.moldes = []
        self.etiquetas = []
        self.rfid_interior = []
        
        # Histórico
        self.moldes_previos = []
        self.etiquetas_previas = []
        self.rfid_interior_previos = []
        
        # Resultado final
        self.resultado = {}
        
        # Flujo de inicialización
        self._leerDatosEntrada()
        self._cargarListasIniciales()

    def procesar(self):
        """
        Procesa los datos y devuelve el resultado estructurado.
        
        Returns:
            dict: {
                "now": datetime,
                "name": nombre_antena,
                "estado_antena_ok": bool,
                "molds": [lista de moldes],
                "labels": [lista de etiquetas],
                "rfid_interior": [lista RFID interior]
            }
        """
        self.moldes = self._clasificarYResumirTags(
            self._obtenerIdMolde, 
            self.moldes_previos
        )
        self.etiquetas = self._clasificarYResumirTags(
            self._obtenerIdEtiqueta, 
            self.etiquetas_previas
        )
        self._procesarRfidInterior()
        self._construirObjetoResultado()
        
        return self.resultado

    # ===== INICIALIZACIÓN =====

    def _inicializarDependencias(self):
        """Inicializa las herramientas externas."""
        self._buscador_moldes = fd.gestionmoldes.consultamoldes.BuscadorMoldes()
        self._conversor_hex_dec = fd.utilidades.transformaciones.ConversoresDecimalHexadecimal()
        self._logger = fd.utilidades.logger.LoggerFuncionesClase("ProcesadorAntena")

    def _leerDatosEntrada(self):
        """Extrae la lista de tags según el formato de entrada."""
        try:
            if self.usa_formato_plano:
                self._extraerDeStringPlano(self.datos_lectura)
            else:
                self._extraerDeDiccionarioJson(self.datos_lectura)
        except Exception as error:
            self._registrarErrorCritico("lectura de datos de entrada", error)
            self.tags_antenna = []
            self.estado_antena = 3

    def _extraerDeDiccionarioJson(self, datos):
        """Extrae tags y estado de un diccionario JSON o datos de Ignition."""
        try:
            # Convertir a diccionario Python si viene de Ignition
            datos_dict = self._convertirADictPython(datos)
        except Exception as error:
            self._logger.logWarning("Error convirtiendo datos a diccionario: {}".format(str(error)))
            self.tags_antenna = []
            self.estado_antena = 3
            return
        
        if "lista_epc" not in datos_dict:
            self._logger.logWarning("Campo 'lista_epc' no encontrado en datos")
            self.tags_antenna = []
            self.estado_antena = 3
            return
        
        self.tags_antenna = datos_dict["lista_epc"]
        self.estado_antena = self._obtenerEstadoSeguro(datos_dict.get("estado_antena", 3))

    def _convertirADictPython(self, datos):
        """Convierte objetos de Ignition a diccionarios Python normales."""
        # Si ya es un diccionario de Python, devolverlo
        if isinstance(datos, dict):
            return datos
        
        # Intentar convertir a diccionario (para objetos de Ignition)
        try:
            datos_convertidos = dict(datos)
            return datos_convertidos
        except (TypeError, ValueError):
            raise ValueError("Los datos no pudieron ser convertidos a diccionario")

    def _extraerDeStringPlano(self, cadena_lectura):
        """Extrae tags de una cadena delimitada por ';'."""
        # Convertir a string si es necesario
        if not isinstance(cadena_lectura, str):
            cadena_lectura = str(cadena_lectura)
        
        partes = cadena_lectura.split(";")
        
        if not partes or not partes[0]:
            raise ValueError("Cadena de lectura vacía o mal formada")
        
        self.estado_antena = self._obtenerEstadoSeguro(partes[0])
        timestamp_actual = system.date.now()
        
        self.tags_antenna = [
            self._construirDictTagDesdeEpc(epc, i, timestamp_actual)
            for i, epc in enumerate(partes[1:])
            if epc.strip()
        ]

    def _construirDictTagDesdeEpc(self, epc, indice, timestamp):
        """Construye un diccionario de tag con campos estándar."""
        return {
            "id": "lectura_" + str(indice),
            "rssi": 40,
            "epc": epc.strip(),
            "timestamp": timestamp
        }

    def _obtenerEstadoSeguro(self, valor_estado):
        """Convierte el estado a entero, con valor por defecto."""
        try:
            return int(valor_estado)
        except (ValueError, TypeError):
            return 3

    def _cargarListasIniciales(self):
        """Carga las listas históricas del objeto destino inicial."""
        try:
            # Convertir a diccionario si es necesario
            objeto_dict = self._convertirADictPython(self.objeto_destino_inicial)
            self.moldes_previos = self._extraerListaSegura(objeto_dict, "molds")
            self.etiquetas_previas = self._extraerListaSegura(objeto_dict, "labels")
            self.rfid_interior_previos = self._extraerListaSegura(objeto_dict, "rfid_interior")
        except Exception as error:
            self._registrarErrorCritico("carga de listas iniciales", error)

    def _extraerListaSegura(self, diccionario, clave):
        """Extrae una lista de un diccionario con validación."""
        try:
            lista = diccionario.get(clave, [])
            return lista if isinstance(lista, list) else []
        except (AttributeError, TypeError):
            return []

    # ===== CLASIFICACIÓN Y PROCESAMIENTO =====

    def _clasificarYResumirTags(self, funcion_obtener_id, tags_previos):
        """Clasifica tags, agrupa duplicados y compila estadísticas."""
        tags_por_id = {}
        
        for tag_raw in self.tags_antenna:
            tag_id = funcion_obtener_id(tag_raw)
            if tag_id:
                tag_normalizado = self._normalizarTag(tag_raw, tag_id)
                self._registrarOActualizarTag(tags_por_id, tag_normalizado)
        
        self._preservarTagsHistoricos(tags_por_id, tags_previos)
        return self._ordenarTagsPorSenial(tags_por_id.values())

    def _normalizarTag(self, tag, tag_id):
        """Normaliza un tag: ajusta RSSI, timestamp e ID."""
        tag_copia = dict(tag)
        tag_copia["rssi"] = self._normalizarRssi(tag_copia.get("rssi", 0))
        tag_copia["timestamp"] = self._obtenerTimestampActual()
        tag_copia["id"] = tag_id
        return tag_copia

    def _normalizarRssi(self, rssi_raw):
        """Convierte RSSI a rango válido (signed)."""
        try:
            rssi_int = int(rssi_raw)
            return rssi_int - 256 if rssi_int > 127 else rssi_int
        except (ValueError, TypeError):
            return 0

    def _obtenerTimestampActual(self):
        """Obtiene el timestamp actual en formato estándar."""
        return system.date.format(system.date.now(), 'yyyy-MM-dd HH:mm:ss')

    def _registrarOActualizarTag(self, tags_por_id, tag_normalizado):
        """Registra un tag nuevo o actualiza uno existente."""
        tag_id = tag_normalizado["id"]
        
        if tag_id in tags_por_id:
            self._actualizarEstadisticasTag(tags_por_id[tag_id], tag_normalizado)
        else:
            tags_por_id[tag_id] = self._crearResumenEstadisticoTag(tag_normalizado)

    def _crearResumenEstadisticoTag(self, tag):
        """Crea un resumen estadístico inicial para un tag nuevo."""
        return {
            "id": tag["id"],
            "tag_count": 1,
            "max_rssi": tag["rssi"],
            "min_rssi": tag["rssi"],
            "last_read": tag["timestamp"],
            "first_read": tag["timestamp"]
        }

    def _actualizarEstadisticasTag(self, resumen, tag_nuevo):
        """Actualiza las estadísticas de un tag ya registrado."""
        resumen["tag_count"] += 1
        resumen["max_rssi"] = max(resumen["max_rssi"], tag_nuevo["rssi"])
        resumen["min_rssi"] = min(resumen["min_rssi"], tag_nuevo["rssi"])
        resumen["last_read"] = tag_nuevo["timestamp"]

    def _preservarTagsHistoricos(self, tags_por_id, tags_previos):
        """Añade tags históricos que no reaparecieron en la lectura actual."""
        for tag_historico in tags_previos:
            tag_id = tag_historico.get("id")
            if tag_id and tag_id not in tags_por_id:
                tags_por_id[tag_id] = dict(tag_historico)

    def _ordenarTagsPorSenial(self, tags):
        """Ordena tags por potencia de señal máxima (descendente)."""
        return sorted(tags, key=lambda tag: tag.get("max_rssi", 0), reverse=True)

    # ===== IDENTIFICACIÓN DE TIPOS =====

    def _obtenerIdMolde(self, tag):
        """Obtiene el ID del molde si el tag corresponde a uno."""
        try:
            epc = tag.get("epc")
            if not epc:
                return None
            return self._buscador_moldes.obtieneIdMoldePorEpc(epc)
        except Exception as error:
            self._registrarErrorNoCritico("obtención de ID molde", error)
            return None

    def _obtenerIdEtiqueta(self, tag):
        """Obtiene el ID de la etiqueta si el tag corresponde a una."""
        try:
            epc = tag.get("epc")
            if not epc:
                return None
            
            epc_decimal = self._conversor_hex_dec.convierteUuidHexadecimalEnDecimal(epc)
            
            if self._esEtiquetaValida(epc_decimal):
                return epc_decimal
            return None
        except Exception as error:
            self._registrarErrorNoCritico("conversión de EPC a etiqueta", error)
            return None

    def _esEtiquetaValida(self, id_decimal):
        """Valida si un ID decimal cumple el criterio de etiqueta."""
        try:
            return (
                isinstance(id_decimal, str)
                and id_decimal[0] == '1'
                and len(id_decimal) == 38
            )
        except (IndexError, TypeError):
            return False

    # ===== PROCESAMIENTO ESPECIAL =====

    def _procesarRfidInterior(self):
        """Procesa tags de RFID interior."""
        self.rfid_interior = list(self.rfid_interior_previos)

    # ===== CONSTRUCCIÓN DE RESULTADO =====

    def _construirObjetoResultado(self):
        """Compone el objeto resultado final."""
        self.resultado = {
            "now": system.date.now(),
            "name": self.nombre_antena,
            "estado_antena_ok": self._esEstadoCorrecto(),
            "molds": self.moldes,
            "labels": self.etiquetas,
            "rfid_interior": self.rfid_interior
        }

    def _esEstadoCorrecto(self):
        """Determina si el estado de la antena es correcto."""
        return self.estado_antena == 3

    # ===== LOGGING =====

    def _registrarErrorCritico(self, contexto, error):
        """Registra un error crítico."""
        mensaje = "ERROR CRITICO en {}: {}".format(contexto, str(error))
        self._logger.logError(mensaje)

    def _registrarErrorNoCritico(self, contexto, error):
        """Registra un error no crítico."""
        mensaje = "Advertencia en {}: {}".format(contexto, str(error))
        self._logger.logWarning(mensaje)