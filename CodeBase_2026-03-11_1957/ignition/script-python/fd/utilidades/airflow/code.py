from java.text import SimpleDateFormat
from java.util import TimeZone

class LanzadorDagAirflow:
    URL_BASE_AIRFLOW = "http://10.25.0.111:8080"
    RUTA_TOKEN = "/auth/token"
    RUTA_DAGRUNS = "/api/v2/dags/{}/dagRuns"

    USUARIO_DEFECTO = "airflow"
    PASSWORD_DEFECTO = "airflow"

    def __init__(self, id_dag, usuario=None, password=None, url_base=None):
        self._id_dag = self._aTexto(id_dag)
        self._url_base = self._normalizarUrl(url_base or self.URL_BASE_AIRFLOW)

        self._usuario = usuario or self.USUARIO_DEFECTO
        self._password = password or self.PASSWORD_DEFECTO

        self._logger = system.util.getLogger("LanzadorDagAirflow")
        
        self._cliente_http = system.net.httpClient(version="HTTP_1_1")

        self._url_token = self._construirUrlToken()
        self._url_dagruns = self._construirUrlDagRuns()

    def ejecutar(self, usuario_disparador="desconocido", configuracion=None,
                logical_date=None, id_ejecucion=None, nota=None,
                intervalo_inicio=None, intervalo_fin=None, ejecutar_despues=None):
        token = self._obtenerToken()
        payload = self._construirPayloadDagRun(
            usuario_disparador=usuario_disparador,
            configuracion=configuracion,
            logical_date=logical_date,
            id_ejecucion=id_ejecucion,
            nota=nota,
            intervalo_inicio=intervalo_inicio,
            intervalo_fin=intervalo_fin,
            ejecutar_despues=ejecutar_despues
        )
        respuesta = self._crearDagRun(token, payload)
        return self._resumirDagRun(respuesta)

    def _obtenerToken(self):
        cuerpo = self._cuerpoToken()
        texto = self._postJsonConHttpPost(self._url_token, cuerpo, cabeceras_extra={"Accept": "application/json"})
        datos = self._parsearJson(texto, "Respuesta no JSON al pedir token.")
        token = datos.get("access_token")
        self._exigir(token, "No se recibio access_token. Body: {}".format(texto))
        return token

    def _cuerpoToken(self):
        return {"username": self._usuario, "password": self._password}

    def _construirPayloadDagRun(self, usuario_disparador, configuracion, logical_date,
                               id_ejecucion, nota, intervalo_inicio, intervalo_fin, ejecutar_despues):
        payload = {}
        payload["logical_date"] = self._asegurarLogicalDate(logical_date)
        payload["conf"] = self._construirConf(usuario_disparador, configuracion)

        self._anadirSiExiste(payload, "dag_run_id", id_ejecucion, a_texto=True)
        self._anadirSiExiste(payload, "note", nota, a_texto=True)
        self._anadirSiExiste(payload, "data_interval_start", intervalo_inicio, a_fecha_iso=True)
        self._anadirSiExiste(payload, "data_interval_end", intervalo_fin, a_fecha_iso=True)
        self._anadirSiExiste(payload, "run_after", ejecutar_despues, a_fecha_iso=True)

        return payload

    def _asegurarLogicalDate(self, logical_date):
        if logical_date is None:
            return self._ahoraUtcIsoZ()
        return self._aIsoZ(logical_date)

    def _construirConf(self, usuario_disparador, configuracion):
        conf = {"origen": "ignition", "usuario": self._aTexto(usuario_disparador)}
        if configuracion:
            conf.update(configuracion)
        return conf

    def _crearDagRun(self, token, payload):
        headers = self._cabecerasAutorizacion(token)
        
        respuesta = self._cliente_http.post(self._url_dagruns, headers=headers, data=payload)

        self._logger.info("Airflow dagRuns HTTP {} - {}".format(respuesta.getStatusCode(), respuesta.getText()))
        self._validarRespuestaDagRun(respuesta)

        return respuesta

    def _cabecerasAutorizacion(self, token):
        return {"Authorization": "Bearer {}".format(token), "Accept": "application/json"}

    def _validarRespuestaDagRun(self, respuesta):
        codigo = respuesta.getStatusCode()
        if codigo in (200, 201):
            return
        raise Exception("Error al lanzar DAG. HTTP {} - {}".format(codigo, respuesta.getText()))

    def _resumirDagRun(self, respuesta):
        datos = self._parsearJson(respuesta.getText(), "Respuesta no valida al lanzar DAG.")
        return datos.get("dag_id"), datos.get("dag_run_id"), datos.get("state")

    def _postJsonConHttpPost(self, url, body_dict, cabeceras_extra=None):
        cabeceras = {"Accept": "application/json"}
        if cabeceras_extra:
            cabeceras.update(cabeceras_extra)

        return system.net.httpPost(
            url=url,
            contentType="application/json",
            postData=system.util.jsonEncode(body_dict),
            headerValues=cabeceras
        )

    def _parsearJson(self, texto, mensaje_error):
        try:
            return system.util.jsonDecode(texto)
        except:
            raise Exception("{} Body: {}".format(mensaje_error, texto))

    def _ahoraUtcIsoZ(self):
        return self._formatearUtcIsoZ(system.date.now())

    def _aIsoZ(self, valor):
        if isinstance(valor, basestring):
            return valor
        return self._formatearUtcIsoZ(valor)

    def _formatearUtcIsoZ(self, fecha_java):
        fmt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'")
        fmt.setTimeZone(TimeZone.getTimeZone("UTC"))
        return fmt.format(fecha_java)

    def _construirUrlToken(self):
        return self._url_base + self.RUTA_TOKEN

    def _construirUrlDagRuns(self):
        return self._url_base + self.RUTA_DAGRUNS.format(self._id_dag)

    def _normalizarUrl(self, url):
        url = self._aTexto(url)
        return url[:-1] if url.endswith("/") else url

    def _aTexto(self, valor):
        return "" if valor is None else str(valor)

    def _anadirSiExiste(self, diccionario, clave, valor, a_texto=False, a_fecha_iso=False):
        if valor is None or valor == "":
            return
        if a_texto:
            diccionario[clave] = self._aTexto(valor)
            return
        if a_fecha_iso:
            diccionario[clave] = self._aIsoZ(valor)
            return
        diccionario[clave] = valor

    def _exigir(self, condicion, mensaje_error):
        if not condicion:
            raise Exception(mensaje_error)