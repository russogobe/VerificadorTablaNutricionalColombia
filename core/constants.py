MAX_FOTOS = 8

TITLE_ALIASES = [
    'INFORMACION NUTRICIONAL', 'DATOS DE NUTRICION', 'INFORMACION NUTRIMENTAL',
    'NUTRITION FACTS', 'SUPPLEMENT FACTS'
]
SECONDARY_HEADER_ALIASES = [
    'PERFIL NUTRICIONAL COMPLEMENTARIO',
    'PERFIL NUTRICIONAL COMPLEMENTARIO POR PORCION',
    'COMPLEMENTARIO POR PORCION',
]
SECONDARY_ROW_MARKERS = ['MEQ/L', 'OSMOLALIDAD', 'MOSM/L']
PORTION_ALIASES = ['TAMANO DE PORCION', 'PORCION', 'SERVING SIZE']
SERVINGS_CONTAINER_ALIASES = ['PORCIONES POR ENVASE', 'SERVINGS PER CONTAINER', 'SERVING PER CONTAINER']
PER_100_ALIASES = ['POR 100 G', 'POR 100 ML', '100 G', '100 ML']
PER_PORTION_ALIASES = ['POR PORCION', 'AMOUNT PER SERVING', 'PER SERVING']
SWEETENER_TERMS = ['SUCRALOSE', 'ACESULFAME', 'ASPARTAME', 'SACCHARIN', 'STEVIA', 'EDULCORANTE', 'SWEETENER']

FRONT_SEAL_TERMS = {
    'sodio': ['EXCESO EN SODIO', 'HIGH IN SODIUM'],
    'azucar': ['EXCESO EN AZUCARES', 'HIGH IN SUGAR'],
    'grasa': ['EXCESO EN GRASAS SATURADAS', 'HIGH IN SATURATED FAT'],
    'edulcorante': ['CONTIENE EDULCORANTES', 'CONTAINS SWEETENERS'],
}

NUTRIENTS = [
    dict(k='energia', nombre='Calorías', alias=['CALORIAS', 'CALORIA', 'ENERGIA', 'KCAL', 'CALORIES'], unidad='KCAL', orden=1),
    dict(k='grasa', nombre='Grasa Total', alias=['TOTAL FAT', 'GRASA TOTAL', 'GRASAS TOTALES'], unidad='G', orden=2),
    dict(k='saturada', nombre='Grasa Saturada', alias=['SATURATED FAT', 'GRASA SATURADA', 'GRASAS SATURADAS'], unidad='G', orden=3),
    dict(k='trans', nombre='Grasa Trans', alias=['TRANS FAT', 'GRASA TRANS', 'GRASAS TRANS'], unidad='G', orden=4),
    dict(k='carbos', nombre='Carbohidratos Totales', alias=['TOTAL CARBOHYDRATE', 'CARBOHIDRATOS TOTALES'], unidad='G', orden=5),
    dict(k='fibra', nombre='Fibra Dietaria', alias=['DIETARY FIBER', 'FIBER', 'FIBRA DIETARIA', 'FIBRA DIETETICA'], unidad='G', orden=6),
    dict(k='aztot', nombre='Azúcares Totales', alias=['TOTAL SUGARS', 'AZUCARES TOTALES'], unidad='G', orden=7),
    dict(k='azadd', nombre='Azúcares Añadidos', alias=['ADDED SUGARS', 'INCLUDES ADDED SUGARS', 'AZUCARES ANADIDOS'], unidad='G', orden=8),
    dict(k='proteina', nombre='Proteína', alias=['PROTEIN', 'PROTEINA', 'PROTEINAS'], unidad='G', orden=9),
    dict(k='sodio', nombre='Sodio', alias=['SODIUM', 'SODIO'], unidad='MG', orden=10),
]

MICROS = [
    dict(k='calcio', nombre='Calcio', alias=['CALCIUM', 'CALCIO'], unidad='MG'),
    dict(k='hierro', nombre='Hierro', alias=['IRON', 'HIERRO'], unidad='MG'),
    dict(k='potasio', nombre='Potasio', alias=['POTASSIUM', 'POTASIO'], unidad='MG'),
]
