"""Genera el informe PDF. Dependencia de documentación: reportlab (no del programa Java)."""
from pathlib import Path
from xml.sax.saxutils import escape
import math
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, PolyLine
from reportlab.graphics import renderSVG
from reportlab.pdfbase import pdfmetrics

# Incrustar las fuentes cuando Nimbus está disponible evita sustituciones
# de tipografía en otros visores. El código Java no depende de estas fuentes.
fontes = {
    'Helvetica': 'NimbusSans-Regular', 'Helvetica-Bold': 'NimbusSans-Bold',
    'Times-Roman': 'NimbusRoman-Regular', 'Times-Bold': 'NimbusRoman-Bold',
    'Times-Italic': 'NimbusRoman-Italic', 'Times-BoldItalic': 'NimbusRoman-BoldItalic',
    'Courier': 'NimbusMonoPS-Regular'
}
for alias, nombre in fontes.items():
    afm = Path('/usr/share/fonts/type1/urw-base35') / (nombre + '.afm')
    pfb = Path('/usr/share/fonts/X11/Type1') / (nombre + '.pfb')
    if afm.exists() and pfb.exists():
        face = pdfmetrics.EmbeddedType1Face(str(afm), str(pfb))
        pdfmetrics.registerTypeFace(face)
        pdfmetrics.registerFont(pdfmetrics.Font(alias, face.name, 'WinAnsiEncoding'))

ROOT = Path(__file__).resolve().parents[1]
DESTINO = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'Informe_Parqueadero_Andres_Sisa.pdf'
DESTINO.parent.mkdir(parents=True, exist_ok=True)
NAVY = colors.HexColor('#16324b')
TEAL = colors.HexColor('#087e8b')
PALE = colors.HexColor('#eef4f7')
GRAY = colors.HexColor('#536473')
LIGHT = colors.HexColor('#d6e0e7')
W = A4[0] - 108
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom', fontName='Helvetica-Bold', fontSize=27, leading=33, textColor=NAVY, spaceAfter=18))
styles.add(ParagraphStyle(name='H1Custom', fontName='Helvetica-Bold', fontSize=18, leading=23, textColor=NAVY, spaceAfter=14))
styles.add(ParagraphStyle(name='H2Custom', fontName='Helvetica-Bold', fontSize=11.8, leading=16, textColor=TEAL, spaceBefore=10, spaceAfter=7))
styles.add(ParagraphStyle(name='BodyCustom', fontName='Times-Roman', fontSize=11.2, leading=15, alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle(name='SmallCustom', fontName='Helvetica', fontSize=9.2, leading=12.8, textColor=GRAY, spaceAfter=7))
styles.add(ParagraphStyle(name='CellCustom', fontName='Helvetica', fontSize=9.1, leading=12.4))
styles.add(ParagraphStyle(name='CellHead', fontName='Helvetica-Bold', fontSize=9.1, leading=12.4, textColor=colors.white))
styles.add(ParagraphStyle(name='CodeCustom', fontName='Courier', fontSize=8.1, leading=11.5, backColor=PALE, borderPadding=10, spaceBefore=6, spaceAfter=12))
styles.add(ParagraphStyle(name='RefCustom', fontName='Times-Roman', fontSize=10.3, leading=13.5, leftIndent=18, firstLineIndent=-18, spaceAfter=9, splitLongWords=True))
story=[]

def p(text, style='BodyCustom'):
    story.append(Paragraph(text, styles[style]))

def h(text): p(text, 'H2Custom')
def title(n, text):
    p(n.upper(), 'SmallCustom')
    p(text, 'H1Custom')

def code(text): story.append(Preformatted(text, styles['CodeCustom']))
def page(): story.append(PageBreak())
def table(headers, rows, widths):
    data=[[Paragraph(escape(str(c)), styles['CellHead']) for c in headers]]
    data += [[Paragraph(str(c), styles['CellCustom']) for c in r] for r in rows]
    t=Table(data, colWidths=[W*x for x in widths], hAlign='LEFT', repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, PALE]),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LINEBELOW',(0,-1),(-1,-1),0.5,LIGHT)
    ]))
    story.append(t)
    story.append(Spacer(1,9))

def arrow(d, points, dashed=False):
    flat=[v for pt in points for v in pt]
    kw={'strokeColor':GRAY,'strokeWidth':1}
    if dashed: kw['strokeDashArray']=[3,3]
    d.add(PolyLine(flat,**kw))
    (x0,y0),(x1,y1)=points[-2:]
    angle=math.atan2(y1-y0,x1-x0)
    a=5
    d.add(Line(x1,y1,x1-a*math.cos(angle-.48),y1-a*math.sin(angle-.48),strokeColor=GRAY))
    d.add(Line(x1,y1,x1-a*math.cos(angle+.48),y1-a*math.sin(angle+.48),strokeColor=GRAY))

def uml():
    d=Drawing(487,445)
    def box(x,y,w,height,name,attrs,methods):
        d.add(Rect(x,y,w,height,fillColor=colors.white,strokeColor=NAVY,strokeWidth=1))
        d.add(Rect(x,y+height-25,w,25,fillColor=NAVY,strokeColor=NAVY))
        d.add(String(x+w/2,y+height-17,name,fontName='Helvetica-Bold',fontSize=10,fillColor=colors.white,textAnchor='middle'))
        yy=y+height-40
        for s in attrs:
            d.add(String(x+8,yy,s,fontName='Helvetica',fontSize=8.1,fillColor=NAVY)); yy-=13
        d.add(Line(x,yy+5,x+w,yy+5,strokeColor=LIGHT))
        yy-=10
        for s in methods:
            d.add(String(x+8,yy,s,fontName='Helvetica',fontSize=8.1,fillColor=NAVY)); yy-=13
    box(5,355,193,72,'Main',[],['+ main(String[]): void'])
    box(250,305,223,137,'Parqueadero',['- visitas: List<Vehiculo>','- archivos: ArchivoParqueadero','- tarifa: Tarifa'],['+ registrarEntrada(...): Vehiculo','+ registrarSalida(...): Cobro','+ consultarTotalCaja(): BigDecimal'])
    box(5,160,193,159,'Vehiculo',['- id: long','- placa: String','- entrada: LocalDateTime','- salida: LocalDateTime'],['+ normalizarPlaca(String): String','+ estaDentro(): boolean','+ conSalida(...): Vehiculo'])
    box(250,153,223,112,'ArchivoParqueadero',['- directorio: Path'],['+ cargarVehiculos(): List<Vehiculo>','+ guardarVehiculos(...): void','+ guardarCaja(...): void'])
    box(5,5,193,121,'Cobro',['- vehiculo: Vehiculo','- horasCobradas: long','- total: BigDecimal'],['+ getTotal(): BigDecimal'])
    box(250,5,223,112,'Tarifa',['+ PRECIO_HORA: BigDecimal'],['+ calcularHoras(...): long','+ calcularTotal(...): BigDecimal'])
    arrow(d,[(198,389),(250,389)],True)
    d.add(String(209,398,'usa',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    arrow(d,[(250,328),(225,328),(225,274),(198,274)])
    d.add(String(200,282,'0..*',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    d.add(String(230,335,'1',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    arrow(d,[(362,305),(362,265)])
    d.add(String(369,282,'1',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    arrow(d,[(250,208),(198,208)],True)
    d.add(String(203,216,'lee',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    arrow(d,[(101,126),(101,160)])
    d.add(String(109,138,'1',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    arrow(d,[(198,58),(250,58)],True)
    d.add(String(204,67,'calcula',fontName='Helvetica',fontSize=7,fillColor=GRAY))
    arrow(d,[(473,330),(485,330),(485,60),(473,60)],True)
    return d

def footer(canvas,doc):
    canvas.saveState()
    if doc.page>1:
        canvas.setStrokeColor(LIGHT); canvas.line(54,A4[1]-37,A4[0]-54,A4[1]-37)
        canvas.setFont('Helvetica',8); canvas.setFillColor(GRAY)
        canvas.drawString(54,A4[1]-28,'DEBER 1  |  PROGRAMACIÓN EN JAVA')
        canvas.drawRightString(A4[0]-54,A4[1]-28,'Andrés Sisa')
    canvas.setStrokeColor(LIGHT); canvas.line(54,41,A4[0]-54,41)
    canvas.setFont('Helvetica',8); canvas.setFillColor(GRAY)
    canvas.drawString(54,28,'Control de ingreso, salida y caja del parqueadero')
    canvas.drawRightString(A4[0]-54,28,str(doc.page))
    canvas.restoreState()

# 1. Portada
story.append(Spacer(1,21))
p('UNIVERSIDAD POLITÉCNICA SALESIANA','H2Custom')
p('PROGRAMACIÓN EN JAVA · DEBER 1','SmallCustom')
story.append(Spacer(1,40))
p('Sistema de control<br/>de un parqueadero','TitleCustom')
p('Ingreso de vehículos, registro de salidas<br/>y cobro por hora o fracción','H2Custom')
story.append(Spacer(1,27))
table(['Dato','Detalle'],[
    ['Estudiante','Andrés Sisa'],['Lenguaje y entorno de destino','Java 17 · Eclipse IDE'],
    ['Interfaz','Consola'],['Fecha','18 de octubre de 2026'],
    ['Tarifa solicitada','USD 0,50 por hora o fracción'],
    ['Persistencia','vehiculos.txt y caja.txt']],[.36,.64])
h('Resumen')
p('Se implementó una aplicación orientada a objetos para registrar visitas al parqueadero, calcular el valor de cada salida y conservar el historial en archivos de texto. El trabajo sigue las cuatro etapas de la consigna: análisis, diseño, construcción y validación. Se ejecutaron 30 casos de lógica y persistencia y 7 casos de consola, todos aprobados. El proyecto incluye configuración de Eclipse, código comentado y commits Git reales por funcionalidad.')
p('La validación se realizó con Java en Linux. El código y sus commits por funcionalidad están publicados en GitHub. El proyecto está preparado para importarse y ejecutarse en Eclipse.','SmallCustom')
story.append(Spacer(1,12))
p('Contenido: análisis (2), diseño (3-4), construcción (5), validación (6-7), evidencias (8), Eclipse y Git (9), conclusiones y referencias (10).','SmallCustom')

# 2. Análisis
page(); title('01 · Análisis','Problema, entradas y resultados')
h('Objetivo general')
p('Desarrollar una aplicación Java que controle el ingreso y la salida de vehículos de un parqueadero, determine el valor a pagar a razón de USD 0,50 por hora o fracción y almacene la información en los archivos indicados.')
h('Requisitos y criterios de aceptación')
table(['ID','Requisito','Cómo se verifica'],[
 ['R1','Registrar placa, fecha y hora de ingreso.','El vehículo aparece dentro y permanece al reiniciar.'],
 ['R2','Registrar salida de un vehículo activo.','Se cierra la visita y se muestra su comprobante.'],
 ['R3','Cobrar USD 0,50 por hora iniciada.','60 min = 0,50; 60 min y 1 s = 1,00.'],
 ['R4','Guardar datos en vehiculos.txt y caja.txt.','Los TXT se crean y conservan información legible.'],
 ['R5','Organizar el código mediante clases.','Se separan interfaz, negocio, datos y cálculo.'],
 ['R6','Validar con caja negra y caja blanca.','Casos, resultados y rutas documentados.'],
 ['R7','Entregar informe y commits importantes.','PDF incluido y commits publicados en GitHub.']
],[.08,.45,.47])
h('Entradas, procesos y salidas')
table(['Entradas','Procesos','Salidas'],[
 ['Opción del menú y placa.','Normalizar placa y buscar visita activa.','Confirmación o mensaje de error.'],
 ['Fecha y hora de entrada/salida.','Validar orden temporal; calcular duración y horas.','Comprobante y valor a pagar.'],
 ['Historial guardado.','Leer visitas y acumular importes.','Vehículos dentro, historial y total de caja.']
],[.29,.39,.32])
h('Alcance')
p('Se elige consola, una de las alternativas que aparecen en la pizarra. La consigna no exige cupo máximo, tarifas diferenciadas ni interfaz gráfica. La solución agrega consultas y validaciones para poder demostrar el funcionamiento completo. La caja representa el total acumulado de visitas finalizadas, sin cierre diario.')

# 3. Diseño de clases
page(); title('02 · Diseño','Diagrama de clases')
p('La aplicación contiene seis clases principales. Vehiculo representa una visita, por lo que una misma placa puede aparecer varias veces en el historial después de completar sus salidas. Cada visita dispone de un identificador independiente.')
diagram=uml(); story.append(diagram)
renderSVG.drawToFile(diagram,str(ROOT/'docs'/'diagrama_clases.svg'))
p('Figura 1. Relaciones principales y miembros relevantes. + indica acceso público; - indica acceso privado. Las líneas discontinuas representan dependencias. Se omiten constructores, getters y algunos parámetros para facilitar la lectura. El archivo diagrama_clases.mmd contiene la versión editable. Fuente: elaboración del proyecto.','SmallCustom')
h('Distribución de responsabilidades')
p('<b>Main</b> interactúa con la consola; <b>Parqueadero</b> aplica las reglas; <b>ArchivoParqueadero</b> lee y escribe; <b>Vehiculo</b> conserva los datos de la visita; <b>Tarifa</b> calcula horas e importe; <b>Cobro</b> reúne el comprobante. Esta separación permite probar el negocio sin utilizar el menú.')

# 4. Diseño funcional y de datos
page(); title('02 · Diseño','Reglas, archivos y secuencia de salida')
h('Regla de negocio')
p('Para una duración positiva, el número de horas cobradas corresponde al redondeo hacia arriba de la duración expresada en horas. El importe es ese número multiplicado por 0,50. Se consideran segundos y fracciones de segundo para no perder una fracción después de una hora exacta.')
code('horas_cobradas = techo(duracion / una_hora)\ntotal_usd = horas_cobradas * 0.50')
p('<b>Supuestos explícitos:</b> duración cero genera USD 0,00; una salida anterior se rechaza. Las fechas son locales al equipo. La placa acepta de 5 a 10 letras/números, con al menos una letra y un número; se eliminan guiones y se convierten letras a mayúsculas. Esta validación es del ejercicio, no una verificación oficial de matrícula.')
h('Diseño de los archivos de texto')
table(['Archivo','Campos y significado'],[
 ['vehiculos.txt','id;placa;entrada;salida<br/>Una fila por visita; salida vacía equivale a vehículo dentro.'],
 ['caja.txt','id;placa;entrada;salida;horas_cobradas;total_usd<br/>Una fila por visita finalizada; importe decimal en USD.']
],[.25,.75])
p('Los campos se separan con punto y coma; se escribe en UTF-8. Las fechas del archivo usan ISO, por ejemplo 2026-10-18T08:00. El historial es la fuente principal; caja se genera a partir de las visitas cerradas. Así, un reinicio no agrega cobros duplicados.')
h('Secuencia del método registrarSalida')
table(['Paso','Acción'],[
 ['1','Normalizar la placa y buscar una visita activa. Si no existe, rechazar.'],
 ['2','Validar que la salida no sea anterior a la entrada.'],
 ['3','Crear la visita cerrada; calcular las horas y el importe.'],
 ['4','Guardar el nuevo historial antes de cambiar el estado en memoria.'],
 ['5','Actualizar caja y devolver el comprobante. Si caja falla, avisar y conservar la salida registrada.']
],[.1,.9])
p('La escritura usa un temporal y luego reemplaza el archivo de destino. Si el sistema no admite movimiento atómico, se usa reemplazo normal. No existe una transacción atómica entre ambos TXT; la reconstrucción de caja permite recuperarla desde el historial.','SmallCustom')

# 5. Construcción
page(); title('03 · Construcción','Implementación y métodos importantes')
p('El proyecto usa Java 17 sin dependencias externas de ejecución. Se incluyen .project, .classpath, preferencias UTF-8 y una configuración de lanzamiento para Eclipse. Los paquetes son ec.edu.ups.parqueadero; src contiene el programa y test contiene las pruebas.')
h('Cálculo de horas iniciadas')
code('Duration tiempo = Duration.between(entrada, salida);\nif (tiempo.isNegative()) {\n    throw new IllegalArgumentException(\n        "La salida no puede ser anterior a la entrada.");\n}\nlong segundos = tiempo.getSeconds();\nlong horas = segundos / 3600;\nif (segundos % 3600 != 0 || tiempo.getNano() != 0) {\n    horas++;\n}\nreturn horas;')
p('El fragmento corresponde a la lógica de calcularHoras. Duration permite representar intervalos con segundos y nanosegundos (Oracle, s. f.-b). El importe usa BigDecimal creado desde la cadena "0.50", multiplicado por horas enteras, para conservar exactitud decimal (Oracle, s. f.-a).')
h('Métodos que organizan la solución')
table(['Método','Responsabilidad'],[
 ['registrarEntrada','Evita placas activas duplicadas, asigna ID y guarda una nueva visita.'],
 ['registrarSalida','Busca la visita activa, valida el tiempo, guarda su salida y devuelve Cobro.'],
 ['calcularHoras / calcularTotal','Aplica la regla de hora o fracción y calcula el importe.'],
 ['cargarVehiculos','Lee el historial y detecta líneas inválidas, IDs repetidos y visitas superpuestas.'],
 ['guardarVehiculos / guardarCaja','Escribe los dos archivos con su formato definido.'],
 ['consultarTotalCaja','Suma los importes de las visitas finalizadas.']
],[.39,.61])
h('Manejo de errores')
p('El menú controla opciones inválidas, fechas imposibles, placas incorrectas y errores de archivo. Si la entrada de consola termina a mitad de un registro, se cancela la operación. Las listas devueltas al exterior son inmodificables para impedir que se altere el historial sin guardar.')

# 6. Caja negra
page(); title('04 · Validación','Pruebas de caja negra')
p('Se comparan entradas y resultados observables. Las fechas base son 18/10/2026 a las 08:00:00; se cambia la salida según cada caso. Las pruebas usan directorios temporales independientes.')
table(['Caso','Entrada o condición','Esperado / obtenido'],[
 ['T01','Misma fecha de entrada y salida.','USD 0,00 / 0,00'],
 ['T02-T03','1 segundo; 59 min 59 s.','USD 0,50 / 0,50'],
 ['T04','60 minutos exactos.','USD 0,50 / 0,50'],
 ['T05','60 minutos y 1 segundo.','USD 1,00 / 1,00'],
 ['T06-T07','2 horas; 24 horas.','USD 1,00 y 12,00 / iguales'],
 ['T08','23:50 a 00:10 del día siguiente.','USD 0,50 / 0,50'],
 ['T10, T17','Salida anterior a la entrada.','Rechazo sin cambiar estado / OK'],
 ['T14','Ingreso abc1234 con ABC-1234 dentro.','Duplicado rechazado / OK'],
 ['T16, T18','Placa desconocida; segunda salida.','Sin cobro adicional / OK'],
 ['T19-T21','Reingreso, reinicio y caja eliminada.','Recuperación sin duplicados / OK'],
 ['T30','Tres visitas de 20 minutos.','Caja USD 1,50 / 1,50']
],[.16,.47,.37])
h('Verificación del menú en procesos Java reales')
table(['Caso','Escenario y resultado'],[
 ['U01','Entrada, listado, salida de 61 minutos y caja: USD 1,00.'],
 ['U02','Cerrar y volver a abrir: activo y caja conservados.'],
 ['U03','Opción no numérica y fecha 30 de febrero: errores controlados.'],
 ['U04','Fecha vacía: usa la hora actual.'],
 ['U05','Fin de entrada a mitad de operación: cancelación sin guardar.'],
 ['U06','Duplicado, salida desconocida y fecha anterior: caja inalterada.'],
 ['U07','Historial con cabecera inválida: diagnóstico y salida con código 1.']
],[.16,.84])
p('Resultado: 7/7 escenarios de consola aprobados. El registro completo se entrega en docs/evidencias/pruebas-consola.txt.','SmallCustom')

# 7. Caja blanca
page(); title('04 · Validación','Pruebas de caja blanca')
p('Los casos también se seleccionan según las decisiones internas del código. La tabla vincula condiciones con pruebas ejecutadas; no constituye una medición automática del porcentaje de cobertura.')
table(['Método o decisión','Rutas verificadas','Casos'],[
 ['Tarifa.calcularHoras','Duración negativa; cero; hora exacta; resto de segundos; nanosegundo adicional.','T01, T02, T04, T09, T10'],
 ['registrarEntrada','Placa nueva; duplicada activa; reingreso válido; superposición histórica.','T13, T14, T19, T26'],
 ['registrarSalida','Visita activa; fecha anterior; placa ausente; visita ya cerrada.','T15-T18'],
 ['cargarVehiculos','Archivo nuevo; existente; línea inválida; ID repetido; dos visitas activas.','T12, T13, T22, T27, T28'],
 ['guardarCambios / actualizarCaja','Guardado correcto; fallo del historial; fallo de caja y recuperación.','T20, T21, T23, T24'],
 ['Protección de datos','Historial ausente con caja existente; listas inmodificables; suma exacta.','T25, T29, T30']
],[.28,.48,.24])
h('Resultado reproducible')
p('Se compiló el código con advertencias de javac activadas y se ejecutó PruebasParqueadero. El ejecutor usa comprobaciones que lanzan AssertionError si el resultado difiere; no depende de habilitar la opción -ea. Los temporales de las pruebas se eliminan al finalizar.')
code('PRUEBAS PARQUEADERO | Java 17.0.20\n[OK] T23 Fallo de caja avisa y permite recuperarla\n[OK] T24 Fallo al guardar historial no cambia memoria\n[OK] T25 No borra caja si falta un historial con cobros\n[OK] T26 Impide reingreso anterior a una salida previa\n[OK] T27 Rechaza identificadores repetidos en archivo\n[OK] T28 Rechaza visitas activas duplicadas en archivo\n[OK] T29 No expone listas modificables\n[OK] T30 Suma tres cobros con exactitud decimal\nRESULTADO: 30/30 pruebas aprobadas.')
p('Extracto del registro real docs/evidencias/pruebas-java.txt. Se omiten los casos iniciales en esta página; el archivo conserva todos los resultados.','SmallCustom')
h('Límites de la validación')
p('Se verificaron los casos descritos con OpenJDK 17.0.20 en Linux. No se ejecutó la interfaz de Eclipse ni los scripts de Windows en este entorno. No se midió cobertura con JaCoCo ni se simularon todas las fallas posibles de disco; tampoco se validó uso simultáneo por varios procesos.')

# 8. Evidencias
page(); title('04 · Evidencias','Ejecución y archivos obtenidos')
p('La demostración ingresó ABC-1234 a las 08:00 y XYZ-5678 a las 09:00; luego registró la salida de ABC-1234 a las 09:01. El segundo vehículo permaneció dentro. Estas son transcripciones de la salida real del programa, no capturas de Eclipse.')
h('Comprobante y consulta de caja')
demo=(ROOT/'docs'/'evidencias'/'salida-demo.txt').read_text(encoding='utf-8')
inicio=demo.index('COMPROBANTE |')
fin=demo.index('\n\n1.',inicio)
extracto=demo[inicio:fin]
caja_inicio=demo.index('ID 1 | ABC1234 | 2 hora(s)')
caja_fin=demo.index('\n\n1.',caja_inicio)
extracto+='\n\n'+demo[caja_inicio:caja_fin]
code(extracto)
h('Contenido de vehiculos.txt')
code((ROOT/'docs'/'ejemplos'/'vehiculos.txt').read_text(encoding='utf-8').rstrip())
h('Contenido de caja.txt')
code((ROOT/'docs'/'ejemplos'/'caja.txt').read_text(encoding='utf-8').rstrip())
p('La visita 1 conserva la salida y genera un cobro de USD 1,00; la visita 2 mantiene la salida vacía. Después de terminar y volver a iniciar el proceso, se comprobó que XYZ5678 seguía activo y el total de caja permanecía en USD 1,00.')
h('Dónde encontrar las evidencias')
table(['Archivo','Contenido'],[
 ['entrada-demo.txt','Secuencia de entradas utilizada para la demostración.'],
 ['salida-demo.txt','Salida íntegra de la consola, incluido el menú.'],
 ['pruebas-java.txt','30 resultados de lógica y persistencia.'],
 ['pruebas-consola.txt','7 resultados del menú mediante procesos Java.']
],[.35,.65])
p('Los TXT de ejemplo están en docs/ejemplos. El programa crea sus propios archivos de trabajo en la carpeta de ejecución, sin cargar automáticamente esos ejemplos.','SmallCustom')

# 9. Eclipse y Git
page(); title('05 · Entrega','Ejecución en Eclipse y commits')
h('Importar y ejecutar')
p('1. Descomprimir el ZIP y abrir Eclipse con un JDK 17 configurado.<br/>2. Elegir <b>File &gt; Import &gt; General &gt; Existing Projects into Workspace</b>.<br/>3. Seleccionar como raíz la carpeta ParqueaderoJava y finalizar.<br/>4. Abrir Main.java y usar <b>Run As &gt; Java Application</b>.<br/>5. Escribir en Console; pulsar F5 para visualizar los TXT creados.')
p('El asistente de importación permite incorporar proyectos existentes, y el lanzamiento Java ejecuta su método main (Eclipse Foundation, s. f.-a, s. f.-b). El archivo ParqueaderoJava.launch fija el directorio de trabajo. Para probar, ejecutar PruebasParqueadero.java de la misma forma.')
h('Historial real por funciones importantes')
table(['Commit','Cambio registrado'],[
 ['0b33ea1','Inicialización del repositorio remoto.'],
 ['e673a50','Proyecto Eclipse y modelo Vehiculo con validaciones.'],
 ['f1a7755','calcularHoras, calcularTotal y comprobante Cobro.'],
 ['cbf2fdb','Carga del historial y escritura de ambos TXT.'],
 ['4eef92b','registrarEntrada y listarActivos, sin duplicados.'],
 ['0a01e67','registrarSalida y consultarTotalCaja.'],
 ['5f6ca56','Menú de consola, scripts y configuración Eclipse.'],
 ['946a81e','Pruebas y evidencias de ejecución.']
],[.2,.8])
p('Estos identificadores corresponden a commits publicados en GitHub. Un noveno commit incorpora este informe y las guías; su identificador se consulta con git log. La solución se desarrolló con asistencia de Codex. El código puede revisarse con git show &lt;hash&gt;. Git registra versiones de los cambios confirmados (Chacon &amp; Straub, 2014).')
h('Repositorio publicado')
p('El repositorio público es <link href="https://github.com/sisaa5436-arch/ParqueaderoJava." color="#087e8b">https://github.com/sisaa5436-arch/ParqueaderoJava.</link><br/>El punto al final forma parte de su nombre. La rama main conserva las etapas de implementación y sus pruebas. El historial se respalda también en ParqueaderoJava.bundle.')
code('git clone https://github.com/sisaa5436-arch/ParqueaderoJava..git ParqueaderoJava\ncd ParqueaderoJava\ngit log --oneline --reverse')
p('Los identificadores remotos difieren de los commits de la primera entrega local porque las etapas se publicaron mediante la integración de GitHub. La versión actual del ZIP y del bundle utiliza el historial publicado.','SmallCustom')

# 10. Conclusiones y referencias
page(); title('06 · Cierre','Conclusiones y referencias')
h('Conclusiones')
p('La solución implementa las operaciones de ingreso y salida, calcula el precio por cada hora iniciada y mantiene los datos en los dos archivos solicitados. La separación en clases permite ubicar con claridad las reglas del negocio, el cálculo del importe y la persistencia. Los resultados de 30 casos de lógica/archivos y 7 escenarios del menú respaldan el funcionamiento para las condiciones evaluadas.')
p('El historial de visitas permite recuperar el estado al reiniciar y reconstruir caja sin duplicar cobros. Las validaciones rechazan placas activas repetidas, salidas anteriores y datos malformados. El código y los commits ya se encuentran publicados. La revisión y ejecución en Eclipse permiten al estudiante comprobar la instalación en su equipo y preparar la explicación de los métodos.')
h('Limitaciones y mejoras posibles')
p('El alcance es académico y de una sola instancia. Se reescribe el historial completo en cada cambio; no hay bloqueo entre procesos. La tarifa es fija: modificarla recalcularía la caja histórica. Una ampliación podría guardar la tarifa aplicada por visita, incorporar control de capacidad e implementar persistencia transaccional para uso concurrente.')
h('Referencias')
refs=[
 'Chacon, S., &amp; Straub, B. (2014). <i>Pro Git</i> (2.ª ed.). Apress. https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository',
 'Eclipse Foundation. (s. f.-a). <i>Importing existing projects</i>. Eclipse Help. https://help.eclipse.org/latest/topic/org.eclipse.platform.doc.user/tasks/tasks-importproject.htm',
 'Eclipse Foundation. (s. f.-b). <i>Launching a Java program</i>. Eclipse Help. https://help.eclipse.org/latest/topic/org.eclipse.jdt.doc.user/tasks/task-launching_java_program.htm',
 'Oracle. (s. f.-a). <i>BigDecimal (Java SE 17 &amp; JDK 17)</i>. https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/math/BigDecimal.html',
 'Oracle. (s. f.-b). <i>Duration (Java SE 17 &amp; JDK 17)</i>. https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/time/Duration.html'
]
for ref in refs: p(ref,'RefCustom')
p('Fuentes oficiales consultadas el 18 de octubre de 2026. La consigna se tomó de la fotografía proporcionada por el estudiante. Los diagramas, el código y los registros de prueba corresponden a esta entrega.','SmallCustom')

doc=SimpleDocTemplate(str(DESTINO),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=54,bottomMargin=55,
                      title='Deber 1: Sistema de control de un parqueadero',author='Andrés Sisa',
                      subject='Java, Eclipse, archivos de texto y pruebas')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(DESTINO)
