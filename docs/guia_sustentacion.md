# Guía para explicar el deber

1. **¿Por qué varias clases?** Main recoge datos, Parqueadero aplica las reglas,
   ArchivoParqueadero guarda información, Vehiculo representa una visita,
   Tarifa calcula el precio y Cobro reúne los datos del comprobante.
2. **¿Hora o fracción?** Una hora iniciada se cobra completa: 61 minutos equivalen
   a dos horas cobradas. No se redondea al entero más cercano.
3. **¿Por qué no solo minutos?** Perder segundos puede cobrar de menos cuando
   la salida supera una hora exacta por pocos segundos.
4. **¿Por qué BigDecimal?** Representa dinero decimal con exactitud. Se crea
   desde la cadena "0.50" y se multiplica por horas enteras.
5. **¿Cómo saber si está dentro?** La visita tiene salida nula. Al salir se crea
   una copia con fecha de salida, se guarda y se devuelve el cobro.
6. **¿Cómo evitar duplicados?** Se normaliza la placa, se comprueba si ya está
   dentro y cada visita tiene un ID. Una visita cerrada no vuelve a cobrar.
7. **¿Para qué dos TXT?** Vehiculos conserva entradas y salidas; caja registra
   los importes de las visitas cerradas. Se recuperan al iniciar.
8. **¿Qué ocurre al reiniciar?** Se lee el historial y se genera caja de nuevo:
   cada visita cerrada produce una sola fila, sin duplicar los cobros.
9. **¿Caja negra y blanca?** La primera compara entradas y salidas sin consultar
   el código. La segunda elige casos para recorrer decisiones internas como
   la condición de fracciones o los errores de archivos.
10. **¿Qué es un commit?** Una versión confirmada de cambios relacionados.
    Existe localmente; `git push` lo publica en el repositorio remoto.

Antes de entregar, abre el proyecto en tu Eclipse, ejecuta la demostración y
verifica que puedes explicar cada método con tus palabras.
