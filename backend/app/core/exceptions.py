# BusinessException: una excepción propia del proyecto, distinta de las
# excepciones genéricas de Python (ValueError, Exception, etc.).
# La usamos para representar errores de REGLAS DE NEGOCIO (por ejemplo,
# "ese email ya está registrado"), a diferencia de errores técnicos
# (una excepción de conexión a la base, por ejemplo).
#
# ¿Por qué crear una clase propia en vez de usar ValueError directamente?
# Porque más adelante, cuando construyamos los endpoints, vamos a poder
# "atrapar" específicamente BusinessException y convertirla en una
# respuesta HTTP 400 clara para quien use la API — sin arriesgarnos a
# atrapar por error cualquier otro ValueError inesperado del sistema
# que en realidad sería un bug, no una regla de negocio.
class BusinessException(Exception):
    pass