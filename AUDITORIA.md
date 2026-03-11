# Auditoría de Código — Librería Común Ignition 8.3 (CodeBase)

> Fecha: 2026-03-11  
> Proyecto: `CodeBase` — librería heredada por el resto de proyectos del SCADA Ignition 8.3

---

## 1. Estructura general de módulos

La librería está organizada bajo dos espacios de nombres principales:

```
script-python/
├── exchange/          # Utilidades de estructuras de datos tipo pandas (Jandas)
│   └── Jandas/
│       ├── Jandas/       # Módulo raíz / re-exportaciones
│       ├── dataframe/    # Clase DataFrame
│       ├── indexers/     # Indexadores iloc/loc
│       ├── series/       # Clase Series
│       └── vector/       # Vector base
├── fd/                # Librería de dominio del proyecto (Fábrica de Duchas)
│   ├── globales/         # Parámetros globales de la instalación
│   ├── excepciones/      # Jerarquía de excepciones personalizada
│   ├── utilidades/       # Capa de infraestructura y utilidades transversales
│   │   ├── logger/
│   │   ├── sql/
│   │   ├── tags/
│   │   ├── dataset/
│   │   ├── transformaciones/
│   │   ├── csv/
│   │   ├── excel/
│   │   ├── impresoras/
│   │   ├── scope/
│   │   ├── turnoproduccion/
│   │   ├── contrometro/
│   │   ├── airflow/
│   │   ├── apirest/
│   │   ├── manejorequest/
│   │   ├── simuladorplcs/
│   │   ├── integracionoperario/
│   │   └── OpcUA_NX/
│   ├── utilidades2/      # Funciones sueltas (legado, pendiente refactorizar)
│   ├── sku/              # Manejo y conversión de códigos SKU
│   ├── numerosserie/     # Generación y conversión de números de serie RFID
│   ├── moldes/           # Dominio de moldes de producción
│   ├── wip/              # Work In Progress — gestión de scrap
│   ├── almacen/          # Movimientos de almacén / materias primas
│   ├── inventario/       # Inventario RFID de platos y moldes
│   ├── inventarioelectronica/ # Inventario de componentes electrónicos
│   ├── ordenesproduccion/     # Re-exportaciones del dominio de órdenes
│   ├── etiquetas/             # Re-exportaciones del módulo de etiquetas
│   ├── etiquetas_externas/    # Etiquetas de clientes externos
│   ├── clasesordenesprod/     # Dominio completo de órdenes de producción
│   │   ├── gestion/           # GestorOrdenesProduccion, GestorPlanProduccion
│   │   ├── ordenes/           # OrdenProduccionBase, OrdenProduccionClavei, …
│   │   ├── asignadores/       # AsignadorOrdenProduccion (bloqueos pesimistas)
│   │   ├── selectores/        # SelectorOrdenProduccion, SelectorColor
│   │   ├── comprobadorwip/    # ComprobadorOrdenesProduccionWIP
│   │   ├── eventos/           # Eventos cabina pintura (entrada/salida molde)
│   │   ├── udt/               # Gestión del UDT de selección de órdenes en tags
│   │   ├── colaasignacion/    # Cola de peticiones de asignación (polling)
│   │   └── apirest/           # Endpoints REST relacionados con órdenes
│   ├── planificacionproduccion/
│   │   ├── plan/              # ConsultadorPlan (ventana de producción)
│   │   ├── presentacion/      # Presentación del plan en pantalla
│   │   └── sincronizacion/    # Sincronización plan Clavei → SCADA
│   ├── rfid/                  # Procesado de lecturas de antenas RFID
│   │   ├── infozonas/         # DatosZonaRFID — datos de zona por nombre
│   │   ├── procesaantena/     # ProcesadorAntena (v1)
│   │   ├── procesaantena2/    # ProcesadorAntena2 (v2, refactorizado con IA)
│   │   ├── tagsscada/         # ProcesadorTagsDeAntena (usa v1)
│   │   └── tagsscada2/        # ProcesadorTagsDeAntena2 (usa v2)
│   ├── moduloetiquetas/       # Módulo de impresión de etiquetas
│   │   ├── impresionetiquetas/ # ImpresorEtiquetas (HTTP → BarTender)
│   │   ├── modelosetiquetado/ # Modelos de etiquetas (RFID, logística, USA…)
│   │   ├── servicioetiquetado/ # EtiquetasVia — orquestador por vía
│   │   ├── etiquetasmultiples/ # Impresión de múltiples etiquetas
│   │   └── correctorclientesetiquetas/ # Corrección de cliente en etiquetas
│   ├── gestionmoldes/
│   │   ├── consultamoldes/    # BuscadorMoldes
│   │   ├── creacionmoldes/    # Creación de moldes en BBDD
│   │   └── gestionetiquetasmolde/ # Gestión de etiquetas físicas de molde
│   ├── maquinas/              # Estados y lógica de máquinas de producción
│   │   ├── estados/           # Estados de máquina (OEE, paros…)
│   │   ├── embalaje/          # Máquina de embalaje
│   │   ├── cabinapintado/     # Cabina de pintura
│   │   ├── stringsplc/via/    # Strings de comunicación con PLC
│   │   └── amasadora/         # Amasadora (calculos y depósitos)
│   ├── indicadores/           # KPIs y estadísticas de producción
│   │   ├── estadisticas_via/  # Estadísticas por vía de producción
│   │   ├── recuento_produccion/ # Recuento de unidades producidas
│   │   └── scripts_expresiones/ # Scripts auxiliares para expresiones Ignition
│   ├── rfidinteriorplato/     # Asignación de RFID interior a plato
│   ├── envasado/              # Módulo de envasado (escaneo + datos de cajas)
│   ├── antenas/               # Gestión de antenas RFID
│   ├── partesingenieria/      # Partes de ingeniería / guardias
│   ├── clavei/                # Integración con ERP Clavei
│   ├── bartender/             # Integración con BarTender (servidor etiquetas)
│   └── tareasprogramadas/     # Tareas programadas del Gateway
└── tests/                 # Tests unitarios por módulo
```

---

## 2. Funcionalidad por módulo

### 2.1 Capa de infraestructura (`fd/utilidades/`)

| Módulo | Clase principal | Función |
|--------|----------------|---------|
| `logger` | `LoggerBase`, `LoggerEstandarizado`, `LoggerFuncionesClase` | Sistema de logging estandarizado sobre `system.util.getLogger`. Incluye activación de debug en caliente. |
| `sql` | `ConstructorSQL`, `EjecutadorNamedQueriesConContexto` | Abstracción sobre Named Queries de Ignition con reintentos automáticos y soporte de transacciones. Detecta el scope (Gateway/Perspective/Cliente) para usar el proyecto correcto. |
| `tags` | `GestorTags`, `TagBuffer` | Lectura/escritura de tags OPC con reintentos. `TagBuffer` implementa un buffer circular en un tag JSON. |
| `dataset` | `ConversorFormatosDataset` | Conversión entre Dataset de Ignition, listas de diccionarios y JSON agrupado. |
| `transformaciones` | `ConversoresDecimalHexadecimal` | Conversión de UUID de 38 dígitos decimales a 32 caracteres hexadecimales y viceversa (formato RFID). |
| `scope` | `ScriptScope` | Detecta el scope de ejecución actual (Gateway, Perspective, Cliente, Designer). |
| `turnoproduccion` | `DatosTurno` | Calcula el turno de producción (mañana/tarde/noche) a partir de un timestamp. |
| `impresoras` | `InformacionImpresoras`, `InformacionPorNombreImpresoras`, `ConfiguracionImpresoras` | Obtiene datos de impresoras desde BBDD y gestiona la configuración de impresoras por vía. |
| `csv` | `ExportadorCSV` | Exporta un Dataset a fichero CSV con nombre fechado. |
| `excel` | `ExportadorExcel` | Exporta un Dataset a fichero Excel `.xlsx` con nombre fechado. |
| `contrometro` | `CronometroTareas` | Cronómetro de eventos para medir tiempos de ejecución en tareas. |
| `airflow` | `LanzadorDagAirflow` | Lanza DAGs en Apache Airflow 2.x mediante su API REST v2, con autenticación por token. |
| `apirest` | `DecodificadorRequestDataRobusto`, `RespuestaError` | Helpers para endpoints WebDev de Ignition. |
| `manejorequest` | `ManejoRequestCorte`, `ManejoRequestEscaneo` | Deserializa y valida los parámetros de requests de corte y escaneo. |
| `integracionoperario` | `IntegracionOperario` | Comprueba existencia y obtiene información de un operario en BBDD. |
| `OpcUA_NX` | `OpcUaNX` | Lectura/escritura de bloques de memoria de un PLC Omron NX vía OPC UA. |
| `simuladorplcs` | `GeneradorTextoCsvSimuladorPLCOmron` | Convierte exports de variables Omron a formato CSV del simulador de PLCs. |

### 2.2 Dominio de SKU (`fd/sku/`)

| Clase | Función |
|-------|---------|
| `ManejadorSku` | Valida un código SKU y extrae el SKU de molde, color y dimensiones. Soporta formatos FD (20 chars), part-number (13), Dekor y corte. |
| `GeneradorSku` | Genera un SKU completo desde modelo + color + largo + ancho. |
| `ConversorSKUCorte` | Convierte un SKU de producto cortado a su semi-producto equivalente. |
| `ConversorSKUDekor` | Convierte un SKU Dekor a su semi-producto equivalente. |

### 2.3 Números de serie (`fd/numerosserie/`)

| Clase | Función |
|-------|---------|
| `NumeroSerie` | Convierte entre formato decimal (38 dígitos) y hexadecimal (32 chars) del número de serie RFID. Determina si el número corresponde a un plato o un molde. |
| `GeneradorNumeroSerie` | Genera un número de serie nuevo a partir de tipo, cliente, número de molde, color, modelo y dimensión. |
| `GeneradorNumeroSeriePlato` | Factoría especializada para números de serie de platos. |

### 2.4 Órdenes de producción (`fd/clasesordenesprod/`)

Este es el núcleo del sistema. El flujo es:

```
ERP Clavei → GestorPlanProduccion → BBDD SCADA (plan)
                                         ↓
ConsultadorPlan ← SelectorOrdenProduccion ← EventoObtieneYActualizaOrdenesCompatibles
       ↓                   ↓
AsignadorOrdenProduccion (bloqueo pesimista en BBDD)
       ↓
OrdenProduccionDetallada → udtSeleccionOrdenesVia (tags UDT)
```

| Módulo | Clase(s) | Función |
|--------|----------|---------|
| `gestion` | `GestorOrdenesProduccion`, `GestorEliminarOrdenesProduccion`, `GestorPlanProduccion`, `GestorLiberacionOrdenesProduccion` | CRUD de órdenes en SCADA. Sincronización del plan desde Clavei (truncate + bulk insert). |
| `ordenes` | `OrdenProduccionBase`, `OrdenProduccionClavei`, `OrdenProduccionScada`, `OrdenProduccionDetallada` | Jerarquía de dominio de una orden de producción. Carga información desde BBDD Clavei o SCADA según el tipo. |
| `asignadores` | `AsignadorOrdenProduccion`, `AsignadorOrdenProduccionDesdeNumeroSerie` | Bloqueo pesimista de órdenes en BBDD mediante UUID. Soporta transfer entre bloqueos. |
| `selectores` | `SelectorOrdenProduccion`, `SelectorColor`, `FiltroColoresPlatosDelPlan`, `GestorSalidaMoldesDeCabinaPintura` | Selección automática de la mejor orden compatible con el molde y color actuales. |
| `comprobadorwip` | `ComprobadorOrdenesProduccionWIP` | Tarea programada que detecta platos en WIP sin orden asignada y los reasigna. |
| `eventos` | `EventoObtieneYActualizaOrdenesCompatibles`, `EventoEntradaMoldeCabinaPintura`, `EventoCompruebaOrdenPlatoPintado`, `EventoSalidaMoldeCabinaPintura` | Eventos del ciclo de vida de un molde en la cabina de pintura. |
| `udt` | `udtSeleccionOrdenesVia` | Gestiona el UDT de Ignition que sincroniza el estado de selección de órdenes con el PLC. |
| `colaasignacion` | `PeticionesAsignacionOrdenes`, `ProcesadorUnicoDePeticionesAsignacionOrdenes` | Cola de asignación de órdenes por polling en BBDD (para evitar condiciones de carrera entre contextos). |

### 2.5 Planificación de producción (`fd/planificacionproduccion/`)

| Módulo | Clase | Función |
|--------|-------|---------|
| `plan` | `ConsultadorPlan` | Consulta el plan de producción con ventana configurable. Obtiene órdenes compatibles por molde/color y resúmenes por turno. |
| `presentacion` | — | Presenta el plan en componentes Perspective. |
| `sincronizacion` | — | Sincroniza el plan entre Clavei y SCADA. |

### 2.6 RFID (`fd/rfid/`)

| Módulo | Clase | Función |
|--------|-------|---------|
| `infozonas` | `DatosZonaRFID` | Accede a los datos de una zona RFID (molde, modelo, tags) desde tags OPC. |
| `procesaantena` | `ProcesadorAntena` | Procesa lecturas crudas de una antena RFID: clasifica moldes y etiquetas, mantiene histórico. |
| `procesaantena2` | `ProcesadorAntena2` | Versión refactorizada (con asistencia IA) de `ProcesadorAntena`. Misma funcionalidad con mejor estructura. |
| `tagsscada` | `ProcesadorTagsDeAntena` | Orquesta la lectura de un tag JSON de antena y escribe el resultado procesado en el tag destino (usa v1). |
| `tagsscada2` | `ProcesadorTagsDeAntena2` | Igual que `tagsscada` pero usa `ProcesadorAntena2` (v2). |

### 2.7 Módulo de etiquetas (`fd/moduloetiquetas/`)

| Módulo | Clase | Función |
|--------|-------|---------|
| `impresionetiquetas` | `ImpresorEtiquetas` | Envía petición HTTP a BarTender para imprimir una etiqueta. |
| `modelosetiquetado` | `EtiquetaRFID`, `EtiquetaLogistica`, `EtiquetaUSA`, `EtiquetaSchulte`, `EtiquetaMoldes`, `EtiquetasInteriores`, `EtiquetaRFIDCorteDekor` | Un modelo por tipo de etiqueta. Cada uno encapsula los parámetros y la plantilla BarTender correspondiente. |
| `servicioetiquetado` | `EtiquetasVia` | Orquestador: decide qué etiquetas imprimir según el plato/molde de la vía. |
| `etiquetasmultiples` | — | Impresión de múltiples etiquetas en una sola operación. |
| `correctorclientesetiquetas` | — | Corrige el cliente asignado a una etiqueta. |

### 2.8 Módulo de moldes (`fd/moldes/`, `fd/gestionmoldes/`)

| Clase | Función |
|-------|---------|
| `Molde` | Carga y expone la información de un molde desde BBDD (estado, ciclos, tags detectados, SKU modelo). |
| `GestorMoldes` | Activa/desactiva/repara moldes actualizando su estado en BBDD. |
| `EventoActualizaEstadoMolde` | Actualiza el estado de un molde tras eventos de producción. |
| `BuscadorMoldes` | Busca moldes por ID en caché o BBDD. |

### 2.9 Utilidades de datos de intercambio (`exchange/Jandas/`)

Implementación de estructuras de datos tipo `pandas` para Jython/Ignition:
- `DataFrame`: tabla de datos con columnas tipadas.
- `Series`: columna/serie de valores.
- `vector`: vector genérico base.
- `indexers`: acceso por posición (`iloc`) y etiqueta (`loc`).

---

## 3. Relaciones entre módulos

```
fd.globales
    └── fd.utilidades.tags

fd.utilidades.sql
    └── fd.utilidades.scope
    └── fd.utilidades.logger

fd.excepciones         ← importado por prácticamente todos los módulos

fd.sku
    └── fd.utilidades.sql

fd.numerosserie
    └── fd.utilidades.transformaciones
    └── fd.excepciones

fd.moldes
    └── fd.utilidades.sql
    └── fd.utilidades.dataset
    └── fd.utilidades.logger
    └── fd.excepciones

fd.clasesordenesprod.ordenes
    └── fd.utilidades.sql
    └── fd.utilidades.dataset
    └── fd.sku
    └── fd.globales

fd.clasesordenesprod.asignadores
    └── fd.utilidades.sql

fd.clasesordenesprod.gestion
    └── fd.clasesordenesprod.asignadores
    └── fd.globales
    └── fd.utilidades.sql

fd.clasesordenesprod.selectores
    └── fd.clasesordenesprod.asignadores
    └── fd.clasesordenesprod.udt
    └── fd.planificacionproduccion.plan
    └── fd.ordenesproduccion          (re-export de clasesordenesprod.ordenes)

fd.clasesordenesprod.eventos
    └── fd.clasesordenesprod.selectores
    └── fd.clasesordenesprod.udt
    └── fd.ordenesproduccion
    └── fd.moldes
    └── fd.platos

fd.rfid.tagsscada
    └── fd.rfid.procesaantena
    └── fd.utilidades.tags

fd.rfid.tagsscada2
    └── fd.rfid.procesaantena2
    └── fd.utilidades.tags

fd.moduloetiquetas.servicioetiquetado
    └── fd.moduloetiquetas.modelosetiquetado
    └── fd.moduloetiquetas.impresionetiquetas
    └── fd.utilidades.sql

fd.planificacionproduccion.plan
    └── fd.utilidades.sql
```

---

## 4. Puntos de mejora — Bugs críticos

### BUG-01 — Variable `ids` no definida en `eventos/code.py`

**Archivo:** `fd/clasesordenesprod/eventos/code.py`  
**Método:** `EventoCompruebaOrdenPlatoPintado._ajustaEstadoColor`  
**Línea:** `if ids:`

La variable `ids` no existe en ese ámbito. El código justo encima obtiene `ids_colores`. Provoca `NameError` en tiempo de ejecución si el color no es compatible con el modelo.

```python
# ❌ Antes
ids_colores = self._obtieneIdsColoresCompatibles()
datos_colores = []
if ids:   # ← NameError

# ✅ Después
ids_colores = self._obtieneIdsColoresCompatibles()
datos_colores = []
if ids_colores:
```

---

### BUG-02 — Variable `db` sin `self` en `gestion/code.py`

**Archivo:** `fd/clasesordenesprod/gestion/code.py`  
**Método:** `GestorPlanProduccion._obtieneOrdenesProduccionDeClavei`

```python
# ❌ Antes
ordenes_produccion = db.ejecutaNamedQuery(...)  # NameError: 'db' no definida

# ✅ Después
ordenes_produccion = self._db.ejecutaNamedQuery(...)
```

---

### BUG-03 — `getRowCount` sin llamar como función en `gestion/code.py`

**Archivo:** `fd/clasesordenesprod/gestion/code.py`  
En dos lugares se compara el método `getRowCount` con un entero sin invocarlo:

```python
# ❌ Antes (siempre True: compara el método, no su resultado)
if ordenes_produccion.getRowCount != 0:

# ✅ Después
if ordenes_produccion.getRowCount() != 0:
```

---

### BUG-04 — `obtieneTextoTransformado` y `_transformaTextoOmronASimuladorPLC` en `simuladorplcs/code.py`

**Archivo:** `fd/utilidades/simuladorplcs/code.py`  
Múltiples errores en `GeneradorTextoCsvSimuladorPLCOmron`:

```python
# ❌ Antes
def obtieneTextoTransformado(self):
    return _texto_transformado   # falta self.

def _transformaTextoOmronASimuladorPLC():  # falta self
    lineas_sin_encabezado = self._obtenerLineasSinEncabezado(self._lineasTextoGeneradoOmron)  # atributo incorrecto

def _transformaYFormateaColumnas(self, columnas):
    tipo_dato_mapeado_simulador = self._mapearTipoDatoOmronASimulador(tipo_dato)  # tipo_dato no definido
    
# Y fuera de alineación:
        self._texto_transformado = self._texto_transformado + linea_formateada  # indentación mixta

# ✅ Después — ver correcciones en el código
```

---

### BUG-05 — `request.get[...]` en lugar de `request.get(...)` en `manejorequest/code.py`

**Archivo:** `fd/utilidades/manejorequest/code.py`  
Método `__init__` de `ManejoRequestCorte`:

```python
# ❌ Antes (subscript sobre el método, no llamada)
self._production_order_id = request.get['production_order_id']
self._frame_options = request.get['frame_options']

# ✅ Después
self._production_order_id = request.get('production_order_id')
self._frame_options = request.get('frame_options')
```

---

### BUG-06 — `_compruebaIntegridadDatos` no definida en `ManejoRequestCorte`

**Archivo:** `fd/utilidades/manejorequest/code.py`  
`ManejoRequestCorte.__init__` llama a `self._compruebaIntegridadDatos()` pero el método no está definido en la clase. `ManejoRequestEscaneo` sí lo define.

---

### BUG-07 — Indentación mixta en `excepciones/code.py`

Las tres primeras clases usan **4 espacios** para la línea `def __init__` y **tabuladores** para el cuerpo del método. Python 3 no admite esta mezcla.

---

## 5. Puntos de mejora — Convenciones de código

### CONV-01 — Nombres de clases en minúsculas

Varias clases no siguen el estándar PascalCase:

| Archivo | Clase actual | Clase correcta |
|---------|-------------|----------------|
| `fd/utilidades/manejorequest/code.py` | `manejoRequestCorte` | `ManejoRequestCorte` |
| `fd/utilidades/manejorequest/code.py` | `manejoRequestEscaneo` | `ManejoRequestEscaneo` |
| `fd/inventario/code.py` | `inventarioRFID` | `InventarioRFID` |
| `fd/utilidades/simuladorplcs/code.py` | `generadorTextoCsvSimuladorPLCOmron` | `GeneradorTextoCsvSimuladorPLCOmron` |

---

### CONV-02 — `fd/utilidades2/code.py`: funciones sueltas en lugar de clases

El módulo `utilidades2` contiene funciones sueltas a nivel de módulo (`writeTagWithRetry`, `getFullDataFromShowertrayId`, `filaDatasetADiccionario`, `getCurrentShiftTime`, etc.) que duplican funcionalidad ya implementada con mayor calidad en otros módulos (`GestorTags`, `ConversorFormatosDataset`, `DatosTurno`).

**Recomendación:** deprecar `utilidades2` y migrar sus consumidores a los módulos correspondientes.

---

### CONV-03 — Duplicación de consultas a BBDD en `InformacionImpresoras`

Los métodos `obtieneNombreImpresora`, `obtieneServidorImpresion` y `obtieneNombreImpresoraA4` ejecutan **la misma Named Query** tres veces. Sería más eficiente cargar la información en el constructor y exponerla con métodos getter.

```python
# Recomendado
class InformacionImpresoras:
    def __init__(self, printer_id):
        self._db = fd.utilidades.sql.EjecutadorNamedQueriesConContexto('FactoryDB', 'CodeBase')
        self._printer_id = printer_id
        self._info = self._cargaInfo()

    def _cargaInfo(self):
        try:
            resultado = self._db.ejecutaNamedQuery('FD/Etiquetas/ObtieneInformacionImpresora', {"printer_id": self._printer_id})
            return resultado[0]
        except Exception as e:
            raise Exception('No se ha podido obtener informacion de la impresora: ' + str(e))

    def obtieneNombreImpresora(self):
        return self._info["printer_name"]

    def obtieneServidorImpresion(self):
        return self._info["printer_server"]

    def obtieneNombreImpresoraA4(self):
        return self._info["printer_a4"]
```

---

### CONV-04 — `MovimientoAlmacen` usa doble guion bajo (`__`)

**Archivo:** `fd/almacen/code.py`  
La clase usa `__movimiento`, `__sku`, etc. (name mangling de Python), lo que es inconsistente con el resto del código que usa `_` simple para indicar privacidad. Este patrón dificulta la herencia y el testing.

**Recomendación:** cambiar a `_movimiento`, `_sku`, etc.

---

### CONV-05 — `GestorSalidaMoldesDeCabinaPintura` duplica `EventoSalidaMoldeCabinaPintura`

**Archivo:** `fd/clasesordenesprod/selectores/code.py`  
Esta clase es un refactor más antiguo del evento, y el propio comentario en el código indica `# MOVIDO A EVENTOS COMO EventoSalidaMoldeCabinaPintura`. Debería eliminarse para evitar confusión.

---

### CONV-06 — Métodos incompletos en `fd/etiquetas/code.py`

`eventoImpresionEtiquetas` tiene varios métodos con `pass` que no están implementados:

```python
def imprimirEtiquetasRFID(self, impresora_rfid):
    pass  # ← sin implementar

def imprimirEtiquetasPlatosEnvasados(self):
    pass  # ← sin implementar
```

Si la clase está en construcción, debería lanzar `NotImplementedError` en lugar de `pass` silencioso.

---

### CONV-07 — Métodos en `fd/wip/code.py` que no retornan valor

`_generaUrlDesmoldeo`, `_generaParametrosPeticionDesmoldeo`, `_generaParametrosPeticionEnvasado` y `_generaParametrosPeticionScrap` no retornan el valor calculado, lo que provoca que `asignaMotivo` falle silenciosamente al intentar usar `self._url` y `self._parametros` que quedan vacíos.

---

### CONV-08 — `procesaantena` y `procesaantena2` coexisten sin deprecar la v1

La existencia de ambas versiones del procesador de antena (v1 y v2) genera ambigüedad. El comentario en `procesaantena2` indica "Refactorizado con IA, validar antes". Una vez validado, la v1 debería quedar marcada como deprecada o eliminarse.

---

### CONV-09 — SQL raw en algunos módulos que ya usan Named Queries

Algunos módulos mezclan `system.db.runPrepQuery`/`runPrepUpdate` (SQL directo) con Named Queries. Ejemplo en `clasesordenesprod/gestion/code.py`:

```python
# Consulta directa (difícil de mantener, sin versionado)
query_params_datos = 'select Codemp, codser, exactprodorder from FDOS_NEWORDERS_INFO where FinalProductOrder = ?'
params_datos = system.db.runPrepQuery(query_params_datos, [prod_ord], 'ClaveiDB')
```

**Recomendación:** mover todas las consultas a Named Queries para centralizar el mantenimiento SQL.

---

### CONV-10 — Logging directo con `system.util.getLogger` fuera del patrón estándar

Algunos métodos crean loggers inline en lugar de usar `LoggerBase` / `LoggerFuncionesClase`:

```python
# ❌ Patrón ad-hoc
logger = system.util.getLogger("creaPlatoEnPLC")
logger.error("Error creando plato: " + str(e))

# ✅ Patrón estandarizado del proyecto
self._logger = fd.utilidades.logger.LoggerFuncionesClase("GestorSalidaMoldesDeCabinaPintura")
self._logger.logError("Error creando plato: " + str(e))
```

---

### CONV-11 — `CronometroTareas._lista_eventos` como atributo de clase

**Archivo:** `fd/utilidades/contrometro/code.py`  
La lista `_lista_eventos = []` está definida a nivel de clase, lo que causa que **todas las instancias compartan la misma lista**. Debe inicializarse en `__init__` (ya lo hace, pero el atributo de clase no debería existir).

```python
# Eliminar la línea de clase:
# _lista_eventos = []   ← BORRAR
```

---

## 6. Resumen de prioridades

| Prioridad | ID | Descripción |
|-----------|-----|-------------|
| 🔴 Crítica | BUG-01 | `NameError` en `_ajustaEstadoColor` |
| 🔴 Crítica | BUG-02 | `NameError` en `_obtieneOrdenesProduccionDeClavei` |
| 🔴 Crítica | BUG-03 | Comparación de método sin invocar en `getRowCount` |
| 🔴 Crítica | BUG-04 | Múltiples errores en `GeneradorTextoCsvSimuladorPLCOmron` |
| 🔴 Crítica | BUG-05 | `request.get[...]` en `ManejoRequestCorte` |
| 🟠 Alta | BUG-06 | `_compruebaIntegridadDatos` no definida en `ManejoRequestCorte` |
| 🟠 Alta | BUG-07 | Indentación mixta en `excepciones/code.py` |
| 🟡 Media | CONV-01 | Nombres de clase en minúsculas |
| 🟡 Media | CONV-03 | Múltiples consultas DB en `InformacionImpresoras` |
| 🟡 Media | CONV-06 | Métodos incompletos (`pass`) en `etiquetas/code.py` |
| 🟡 Media | CONV-07 | Métodos sin retorno en `wip/code.py` |
| 🟢 Baja | CONV-02 | Deprecar `utilidades2` |
| 🟢 Baja | CONV-04 | Double underscore en `almacen` |
| 🟢 Baja | CONV-05 | Eliminar `GestorSalidaMoldesDeCabinaPintura` obsoleta |
| 🟢 Baja | CONV-08 | Deprecar `procesaantena` v1 |
| 🟢 Baja | CONV-09 | SQL raw → Named Queries |
| 🟢 Baja | CONV-10 | Logging ad-hoc → patrón `LoggerFuncionesClase` |
| 🟢 Baja | CONV-11 | `_lista_eventos` como atributo de clase |
