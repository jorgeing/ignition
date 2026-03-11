import unittest
from fd.utilidades.turnoproduccion import *

class DatosTurnoTest(unittest.TestCase):
	
	_t_stamp_test_nocturno = system.date.parse('2024-08-03 01:37:00')
	_test_turno_nocturno_dict = {
		't_stamp_inicio' : system.date.parse('2024-08-02 22:00:00'),
		't_stamp_fin' : system.date.parse('2024-08-03 06:00:00'),
		'fecha_turno' : system.date.parse('2024-08-03 00:00:00'),
		'id_turno' : DatosTurno.ID_TURNO_NOCHE
	}
	
	_t_stamp_test_matutino = system.date.parse('2024-08-03 10:18:15')
	_test_turno_matutino_dict = {
		't_stamp_inicio' : system.date.parse('2024-08-03 06:00:00'),
		't_stamp_fin' : system.date.parse('2024-08-03 14:00:00'),
		'fecha_turno' : system.date.parse('2024-08-03 00:00:00'),
		'id_turno' : DatosTurno.ID_TURNO_MATUTINO
	}
	
	_t_stamp_test_tarde = system.date.parse('2024-08-03 16:34:22')
	_test_turno_tarde_dict = {
		't_stamp_inicio' : system.date.parse('2024-08-03 14:00:00'),
		't_stamp_fin' : system.date.parse('2024-08-03 22:00:00'),
		'fecha_turno' : system.date.parse('2024-08-03 00:00:00'),
		'id_turno' : DatosTurno.ID_TURNO_TARDE
	}
	
	def testCreaTurnoNoche(self):
		self._testeaTurnoGenerico(self._t_stamp_test_nocturno, self._test_turno_nocturno_dict )
		
	def testCreaTurnoMatutino(self):
		self._testeaTurnoGenerico(self._t_stamp_test_matutino, self._test_turno_matutino_dict )
		
	def testCreaTurnoTarde(self):
		self._testeaTurnoGenerico(self._t_stamp_test_tarde, self._test_turno_tarde_dict )
		
	def testObtieneTurnoMismoDia(self):
		turno = DatosTurno(self._t_stamp_test_nocturno)
		turno_noche = turno.obtieneTurnoDelMismoDia(DatosTurno.ID_TURNO_NOCHE)
		self.assertEqual(turno.obtieneTimestampInicio(),turno_noche.obtieneTimestampInicio())
		
	def testObtieneTurnoActual(self):
		ahora = system.date.now()
		turno_creado_constructor = DatosTurno(ahora)
		turno_creado_funcion = DatosTurno.obtieneDatosTurnoActual()
		self.assertEqual(turno_creado_constructor.obtieneTimestampInicio(), turno_creado_funcion.obtieneTimestampInicio())
		
	def testObtieneTimestampInicioHoraTurno(self):
		timestamp_test = system.date.parse('2024-08-03 01:37:00')
		turno = DatosTurno(timestamp_test)
		timestamp_0 = turno.obtieneTimestampInicioHoraDelTurno(0)
		timestamp_3 = turno.obtieneTimestampInicioHoraDelTurno(3)
		timestamp_8 = turno.obtieneTimestampInicioHoraDelTurno(8)
		self.assertEqual(timestamp_0, system.date.parse('2024-08-02 22:00:00'))
		self.assertEqual(timestamp_3, system.date.parse('2024-08-03 01:00:00'))
		self.assertEqual(timestamp_8, system.date.parse('2024-08-03 06:00:00'))
		
		
	def _testeaTurnoGenerico(self, t_stamp_entrada, t_stamp_test_dict):
		turno = DatosTurno(t_stamp_entrada)
		self.assertEqual(turno.obtieneTimestampInicio(), t_stamp_test_dict['t_stamp_inicio'])
		self.assertEqual(turno.obtieneTimestampFin(), t_stamp_test_dict['t_stamp_fin'])
		self.assertEqual(turno.obtieneFechaTurno(), t_stamp_test_dict['fecha_turno'])
		self.assertEqual(turno.obtieneIdTurno(), t_stamp_test_dict['id_turno'])
		self.assertEqual(turno.obtieneTurnoDiccionario(), t_stamp_test_dict)