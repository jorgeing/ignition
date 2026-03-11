class DatosTurno:
	
	HORAS_TURNO = 8
	HORA_INICIO_TURNO_NOCHE = 22
	HORA_INICIO_TURNO_MATUTINO = 6
	HORA_INICIO_TURNO_TARDE = 14
	HORA_MEDIANOCHE = 0
	
	ID_TURNO_NOCHE = 1
	ID_TURNO_MATUTINO = 2
	ID_TURNO_TARDE = 3
	
	_t_stamp_entrada = 0
	_t_stamp_inicio = 0
	_t_stamp_fin = 0
	_fecha_turno = 0
	_id_turno = 0
	
	def __init__(self, t_stamp_dentro_del_turno):
		self._t_stamp_entrada = t_stamp_dentro_del_turno
		self._calculaFechaTurno()
		self._calculaInicioEIdTurno()
		self._calculaFinTurno(self._t_stamp_inicio)
		
	@staticmethod
	def obtieneDatosTurnoActual():
		return DatosTurno(system.date.now())
		
	@staticmethod
	def obtieneTurnoPorFechaIdTurno(fecha,id_turno):
		return DatosTurno(fecha).obtieneTurnoDelMismoDia(id_turno)
		
	@classmethod
	def obtieneRangoHorasTurno(cls, hora_inicio_turno):
		if hora_inicio_turno == cls.HORA_INICIO_TURNO_NOCHE:
			return [22, 23, 0, 1, 2, 3, 4, 5]
		elif hora_inicio_turno == cls.HORA_INICIO_TURNO_MATUTINO:
			return range(6,14)
		elif hora_inicio_turno == cls.HORA_INICIO_TURNO_TARDE: 
			return range(14,22)
		else:
			raise ValueError("Turno no válido")
		
	def obtieneTimestampInicio(self):
		return self._t_stamp_inicio
		
	def obtieneTimestampFin(self):
		return self._t_stamp_fin
		
	def obtieneFechaTurno(self):
		return self._fecha_turno
		
	def obtieneIdTurno(self):
		return self._id_turno
		
	def obtieneTurnoDiccionario(self):
		return {
			't_stamp_inicio' : self._t_stamp_inicio,
			't_stamp_fin' : self._t_stamp_fin,
			'fecha_turno' : self._fecha_turno,
			'id_turno': self._id_turno
		}
		
	def obtieneTurnoDelMismoDia(self, id_turno):
		fecha_para_crear_turno = None
		
		if id_turno == self.ID_TURNO_NOCHE:
			fecha_para_crear_turno = self._calculaTimestampInicioTurnoNoche()
		elif id_turno == self.ID_TURNO_MATUTINO:
			fecha_para_crear_turno = self._calculaTimestampInicioTurnoMatutino()
		elif id_turno == self.ID_TURNO_TARDE:
			fecha_para_crear_turno = self._calculaTimestampInicioTurnoTarde()
		else:
			raise fd.excepciones.IdSolicitadoException(str(id_turno))
			
		return DatosTurno(fecha_para_crear_turno)
		
	def obtieneTimestampInicioHoraDelTurno(self, offset_horas):
		t_stamp_calculado = system.date.addHours(self._t_stamp_inicio, offset_horas)
		return t_stamp_calculado
		

	def _calculaFechaTurno(self):
		current_shift = self._t_stamp_entrada
		hour = system.date.getHour24(current_shift)
		base_day = system.date.setTime(current_shift, 0, 0, 0)
		if hour < self.HORA_INICIO_TURNO_NOCHE :
			self._fecha_turno =  base_day
		else:
			self._fecha_turno = system.date.addDays(base_day, 1)
			
	def _esTurnoNoche(self):
		hour = system.date.getHour24(self._t_stamp_entrada)
		return hour >= self.HORA_INICIO_TURNO_NOCHE or hour < self.HORA_INICIO_TURNO_MATUTINO
			
	def _esTurnoTarde(self):
		hour = system.date.getHour24(self._t_stamp_entrada)
		return hour >= self.HORA_INICIO_TURNO_TARDE and hour < self.HORA_INICIO_TURNO_NOCHE
			
	def _esTurnoMatutino(self):
		return not (self._esTurnoNoche() or self._esTurnoTarde())

	def _calculaInicioEIdTurno(self):
		if self._esTurnoNoche():
			self._t_stamp_inicio = self._calculaTimestampInicioTurnoNoche()
			self._id_turno = self.ID_TURNO_NOCHE
		elif self._esTurnoTarde():
			self._t_stamp_inicio = self._calculaTimestampInicioTurnoTarde()
			self._id_turno = self.ID_TURNO_TARDE
		elif self._esTurnoMatutino():
			self._t_stamp_inicio = self._calculaTimestampInicioTurnoMatutino()
			self._id_turno = self.ID_TURNO_MATUTINO
			
	def _calculaTimestampInicioTurnoNoche(self):
		fecha_temp = system.date.addDays(self._fecha_turno, -1)
		return system.date.setTime(fecha_temp, self.HORA_INICIO_TURNO_NOCHE, 0, 0)
		
	def _calculaTimestampInicioTurnoMatutino(self,):
		return system.date.setTime(self._fecha_turno, self.HORA_INICIO_TURNO_MATUTINO, 0, 0)
		
	def _calculaTimestampInicioTurnoTarde(self):
		return system.date.setTime(self._fecha_turno, self.HORA_INICIO_TURNO_TARDE, 0, 0)
		
	def _calculaFinTurno(self, t_stamp_inicio):
		self._t_stamp_fin = system.date.addHours(t_stamp_inicio, self.HORAS_TURNO)

	
		
	