from fd.utilidades.dataset import *
from fd.utilidades.sql import *

class TablaCalibraciones():
	
	_query_obtenerTodosDatos = "FD/CalibracionesAmasadora/ObtenerDatosCalibraciones"
	_query_obtenerUltimaCalibracion = "FD/CalibracionesAmasadora/ObtenerUltimaCalibracion"
	_query_insertarNuevaCalibracion = "FD/CalibracionesAmasadora/InsertarNuevaCalibracion"
	_usuario = None
	_capacidad = 0
	_division = 0
	_punto_decimal = 0
	_ajuste_ganancia = 0
	_ajuste_fino_ganancia = 0
	_zero = False
	
	def __init__(self, usuario, capacidad, division, punto_decimal, ajuste_ganancia, ajuste_fino_ganancia, zero):
		self._usuario = usuario
		self._capacidad = capacidad
		self._division = division
		self._punto_decimal = punto_decimal
		self._ajuste_ganancia = ajuste_ganancia
		self._ajuste_fino_ganancia = ajuste_fino_ganancia
		self._zero = zero
		
	def construyeTabla(self):
		datos = self._obtieneDatosCalibraciones()
		datos_formateados = self._formateaDatos(datos)
		return datos_formateados
		
	def _obtieneDatosCalibraciones(self):
		return EjecutadorNamedQueriesConContexto("registro_calibraciones.calibraciones_masas_amasadora","CodeBase").ejecutaNamedQuery(self._query_obtenerTodosDatos, {})
		
	def _formateaDatos(self, datos):
		datos_formateados = []
		for indice_fila in range(datos.getRowCount()):
			fila_formateada = ConversorFormatosDataset.filaDatasetADiccionario(datos, indice_fila)
			datos_formateados.append(fila_formateada)
		return datos_formateados
		
	def insertaNuevaCalibracion(self):
		parametros = self._generaDiccionarioParametrosCalibracion()
		self._insertaCalibracion(parametros)
		
	def _generaDiccionarioParametrosCalibracion(self):
		fecha_actual = system.date.now()
		self._comprobarParametrosCalibracion()
		parametros = {
			"fecha": fecha_actual,
			"usuario": self._usuario,
			"cap": self._capacidad,
			"d1": self._division,
			"dp": self._punto_decimal,
			"span": self._ajuste_ganancia,
			"fspan": self._ajuste_fino_ganancia,
			"zero": self._zero
		}
		return parametros
	
	def _comprobarParametrosCalibracion(self):
		calibracion_anterior = self._obtieneCalibracionAnterior()
		calibracion_anterior = calibracion_anterior[0] # Accede a la única fila existente
		if self._capacidad == "" or self._capacidad == 0:
			self._capacidad = calibracion_anterior['cap']
		if self._division == "" or self._division == 0:
			self._division = calibracion_anterior['d1']
		if self._punto_decimal == "" or self._punto_decimal == 0:
			self._punto_decimal = calibracion_anterior['dp']
		if self._ajuste_ganancia == "" or self._ajuste_ganancia == 0:
			self._ajuste_ganancia = calibracion_anterior['span']
		if self._ajuste_fino_ganancia == "" or self._ajuste_fino_ganancia == 0:
			self._ajuste_fino_ganancia = calibracion_anterior['fspan']
		
	def _obtieneCalibracionAnterior(self):
		return EjecutadorNamedQueriesConContexto("registro_calibraciones.calibraciones_masas_amasadora","CodeBase").ejecutaNamedQuery(self._query_obtenerUltimaCalibracion, {})
		
	def _insertaCalibracion(self, parametros):
		try:
			EjecutadorNamedQueriesConContexto("registro_calibraciones.calibraciones_masas_amasadora","CodeBase").ejecutaNamedQuery(self._query_insertarNuevaCalibracion, parametros)
			print("Fila insertada con éxito")
		except Exception as e:
			print("Error al insertar fila: ", e)
