
def calculaPlatosAPartirDeKgDeMasa(kg_masa, densidad_masa, volumen_promedio):
	volumen_masa = (kg_masa / densidad_masa)
	platos_restantes = volumen_masa/ volumen_promedio
	return platos_restantes