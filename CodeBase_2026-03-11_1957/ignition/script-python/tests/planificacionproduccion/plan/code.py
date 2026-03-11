import unittest

class ConsultadorPlanTests(unittest.TestCase):
	_numero_lineas_testear = 100
	_sku_molde_testear = 'NAT120080'
	_id_color_testear = 9003
	
	def testObtieneTodoPlan(self):
		gestor_plan = fd.planificacionproduccion.plan.ConsultadorPlan(self._numero_lineas_testear)
		plan = gestor_plan.obtieneTodoPlan()
		self.assertTrue(plan.getRowCount()>0)
		
	def testObtieneOrdenesPendientesAsignar(self):
		gestor_plan = fd.planificacionproduccion.plan.ConsultadorPlan(self._numero_lineas_testear)
		plan = gestor_plan.obtieneOrdenesPendientesAsignar()
		self.assertTrue(plan.getRowCount()>0)
		
	def testObtienePlanEnVentana(self):
		gestor_plan = fd.planificacionproduccion.plan.ConsultadorPlan(self._numero_lineas_testear)
		plan_ventana = gestor_plan.obtienePlanEnVentana()
		self.assertTrue(plan_ventana.getRowCount()==self._numero_lineas_testear)
	
	def testObtieneOrdenesEnVentanaCompatiblesConMoldeYColor(self):
		gestor_plan = fd.planificacionproduccion.plan.ConsultadorPlan()
		ordenes_compatibles = gestor_plan.obtieneOrdenesEnVentanaCompatiblesConMoldeYColor(self._sku_molde_testear,self._id_color_testear)
		self.assertTrue(ordenes_compatibles.getRowCount()>0)
	
def run():
	suite_generadornumeroserie_plato = unittest.TestLoader().loadTestsFromTestCase(ConsultadorPlanTests)
	suites_testear = [
		suite_generadornumeroserie_plato
		]
	alltests = unittest.TestSuite(suites_testear)
	output = unittest.TextTestRunner(verbosity=3).run(alltests)
	
	if output.wasSuccessful():
		print '\nPassed tests.'
	else:
		number_failed = len(output.failures) + len(output.errors)
		print "Failed "+str(number_failed)+ " test(s)"