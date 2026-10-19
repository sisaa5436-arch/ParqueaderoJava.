# ParqueaderoJava - Deber 1

Aplicación académica en Java 17 para Eclipse, sin librerías externas.
Autor del informe: Andrés Sisa. Desarrollo asistido por Codex.

## Funciones

- Registra entradas y salidas por placa, fecha y hora.
- Cobra USD 0,50 por hora o fracción y muestra el comprobante.
- Consulta vehículos dentro, historial y total acumulado de caja.
- Guarda automáticamente `vehiculos.txt` y `caja.txt` y recupera los datos al iniciar.

## Abrir en Eclipse

1. Descomprime la entrega en una carpeta propia, fuera de otro proyecto.
2. Usa Eclipse IDE for Java Developers con un JDK 17 o superior instalado.
3. Selecciona **File > Import > General > Existing Projects into Workspace**.
4. En **Select root directory**, selecciona la carpeta `ParqueaderoJava`.
5. Marca el proyecto y pulsa **Finish**. No copies el proyecto a otra ubicación
   si deseas conservar la carpeta `.git` y su historial junto al código.
6. Abre `src/ec/edu/ups/parqueadero/Main.java` y usa **Run As > Java Application**.
   También puedes ejecutar `ParqueaderoJava.launch`.
7. Escribe las opciones en **Console**. Pulsa F5 sobre el proyecto para ver los TXT.

Si falta JavaSE-17, configura **Window > Preferences > Java > Installed JREs** y
el entorno **JavaSE-17** con tu JDK. El proyecto usa UTF-8. La configuración de
lanzamiento fija el directorio de trabajo en la carpeta del proyecto.

## Demostración rápida

1. Opción 1: placa `ABC-1234`, entrada `2026-10-18 08:00:00`.
2. Opción 2: placa `ABC-1234`, salida `2026-10-18 09:01:00`.
3. Resultado: **2 horas cobradas, USD 1.00**.
4. Opción 4: consulta caja. Opción 0: cierra.
5. Abre de nuevo y consulta caja: conserva el mismo total.

En las fechas, Enter usa la hora local actual del equipo. También se aceptan
fechas manuales para probar; formato `aaaa-MM-dd HH:mm:ss`. Son datos de prueba,
no clientes reales. Para repetir usa datos vacíos o una placa diferente.
Conserva copias de los archivos antes de sustituirlos.

## Decisiones de implementación

Para duración positiva: horas = redondeo hacia arriba de duración / 1 hora;
total = horas × 0,50. A los 60 minutos cobra 0,50; a los 60 minutos y 1 segundo,
1,00. Duración exactamente cero cobra 0,00: supuesto porque no se indica un
mínimo. Se rechaza una salida anterior a la entrada.

La placa se normaliza a mayúsculas, sin guiones. Se admiten de 5 a 10 caracteres
alfanuméricos, con letras y números; no es una validación oficial de matrículas.
Se permite reingreso tras salir, con otro ID; no visitas superpuestas.

## Archivos

`vehiculos.txt` es el historial completo y la fuente principal:

    id;placa;entrada;salida
    1;ABC1234;2026-10-18T08:00;2026-10-18T09:01
    2;XYZ5678;2026-10-18T09:00;

Una salida vacía significa dentro. Se usa formato ISO de LocalDateTime;
los segundos pueden omitirse cuando son cero.

`caja.txt` contiene una fila por visita finalizada:

    id;placa;entrada;salida;horas_cobradas;total_usd
    1;ABC1234;2026-10-18T08:00;2026-10-18T09:01;2;1.00

Caja se reconstruye desde el historial al iniciar, guardar o consultar caja.
Si falla su escritura tras guardar una salida, aparece un aviso y la salida
permanece registrada. Corrige el acceso y consulta caja otra vez; no repitas el
cobro. Si falla el historial, la operación no cambia la memoria. Un historial
malformado detiene la carga y muestra el error sin borrarlo. Se escribe con
UTF-8 y reemplazo mediante un archivo temporal.

Uso previsto: una sola instancia, tarifa fija y volúmenes académicos. No edites
los TXT mientras el programa está abierto. Cambiar la tarifa del código
recalcularía también el histórico. El comprobante es académico, no fiscal.

## Pruebas

En Eclipse abre `test/ec/edu/ups/parqueadero/PruebasParqueadero.java` y usa
**Run As > Java Application**. Resultado esperado: `30/30 pruebas aprobadas`.
Las pruebas usan carpetas temporales y no modifican tus datos.

- Windows con JDK en PATH: `probar.bat` y `ejecutar.bat`.
- Linux/macOS: `bash probar.sh` y `bash ejecutar.sh`.

Se ejecutaron 30 casos de lógica/persistencia y 7 del menú mediante procesos Java
reales. Evidencias en `docs/evidencias/`. Entorno probado: Java 17.0.20 en Linux.
No se afirma ejecución dentro de Eclipse ni ejecución de los scripts en Windows.

## Commits y GitHub

Repositorio público: https://github.com/sisaa5436-arch/ParqueaderoJava.
El punto final forma parte del nombre. La rama principal es `main`.

Hay 9 commits: inicialización, modelo, tarifa, archivos, entrada, salida, menú,
pruebas y documentación. Los cambios se publicaron con la integración GitHub;
los hashes remotos difieren del historial de la primera entrega local.
El ZIP actualizado y el bundle conservan el historial publicado.
El desarrollo fue asistido por Codex; revisa y comprende el código antes de entregarlo.

Para obtener una copia con su historial:

    git clone https://github.com/sisaa5436-arch/ParqueaderoJava..git
    cd ParqueaderoJava.
    git log --oneline --reverse
    git show <hash-del-commit>

En Windows es preferible elegir una carpeta sin punto final:

    git clone https://github.com/sisaa5436-arch/ParqueaderoJava..git ParqueaderoJava

Configura tu nombre y correo en Git para los cambios que realices después.
El archivo `ParqueaderoJava.bundle` de la entrega permite restaurar una copia:

    git clone ParqueaderoJava.bundle ParqueaderoJava_restaurado

## Entrega y explicación

- Informe PDF con análisis, diseño, construcción, caja negra, caja blanca y fuentes.
- Código e historial publicados en el enlace anterior.
- Métodos para explicar: `calcularHoras`, `registrarEntrada`, `registrarSalida`,
  `guardarVehiculos`, `guardarCaja` y `consultarTotalCaja`.
- Apoyo: `docs/guia_sustentacion.md` y `docs/diagrama_clases.mmd`.
