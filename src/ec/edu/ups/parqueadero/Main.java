package ec.edu.ups.parqueadero;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.format.ResolverStyle;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Scanner;

/** Interfaz de consola ejecutable en Eclipse: Run As > Java Application. */
public final class Main {
    private static final DateTimeFormatter FECHA = DateTimeFormatter
            .ofPattern("uuuu-MM-dd HH:mm:ss").withResolverStyle(ResolverStyle.STRICT);

    private Main() { }

    public static void main(String[] args) {
        Path directorio = args.length == 0 ? Path.of(".") : Path.of(args[0]);
        try (Scanner teclado = new Scanner(System.in)) {
            Parqueadero parqueadero = new Parqueadero(directorio);
            System.out.println("PARQUEADERO - DEBER 1");
            System.out.println("Tarifa: USD 0.50 por hora o fracción.");
            System.out.println("Archivos: " + parqueadero.getDirectorio());
            mostrarAviso(parqueadero);
            while (true) {
                System.out.println("\n1. Registrar entrada\n2. Registrar salida"
                        + "\n3. Ver vehículos dentro\n4. Consultar caja\n5. Ver historial\n0. Salir");
                System.out.print("Opción: ");
                if (!teclado.hasNextLine()) {
                    System.out.println("\nFin de la entrada de consola.");
                    return;
                }
                String opcion = teclado.nextLine().trim();
                try {
                    switch (opcion) {
                        case "1": {
                            String placa = leer(teclado, "Placa: ");
                            LocalDateTime entrada = leerFecha(teclado, "Entrada");
                            Vehiculo visita = parqueadero.registrarEntrada(placa, entrada);
                            System.out.println("ENTRADA REGISTRADA | ID " + visita.getId()
                                    + " | " + visita.getPlaca() + " | " + FECHA.format(visita.getEntrada()));
                            break;
                        }
                        case "2": {
                            String placa = leer(teclado, "Placa: ");
                            LocalDateTime salida = leerFecha(teclado, "Salida");
                            Cobro cobro = parqueadero.registrarSalida(placa, salida);
                            Vehiculo visita = cobro.getVehiculo();
                            System.out.println("COMPROBANTE | ID " + visita.getId() + " | " + visita.getPlaca());
                            System.out.println("Entrada: " + FECHA.format(visita.getEntrada()));
                            System.out.println("Salida:  " + FECHA.format(visita.getSalida()));
                            System.out.println("Horas cobradas: " + cobro.getHorasCobradas());
                            System.out.println("TOTAL A PAGAR: USD " + cobro.getTotal().toPlainString());
                            break;
                        }
                        case "3":
                            mostrarVisitas(parqueadero.listarActivos());
                            break;
                        case "4":
                            parqueadero.actualizarCaja();
                            for (Cobro cobro : parqueadero.listarCobros()) {
                                System.out.println("ID " + cobro.getVehiculo().getId() + " | "
                                        + cobro.getVehiculo().getPlaca() + " | " + cobro.getHorasCobradas()
                                        + " hora(s) | USD " + cobro.getTotal().toPlainString());
                            }
                            System.out.println("Cobros registrados: " + parqueadero.listarCobros().size());
                            System.out.println("TOTAL CAJA: USD " + parqueadero.consultarTotalCaja().toPlainString());
                            break;
                        case "5":
                            mostrarVisitas(parqueadero.getHistorial());
                            break;
                        case "0":
                            System.out.println("Programa finalizado. Los registros permanecen guardados.");
                            return;
                        default:
                            System.out.println("Opción inválida. Seleccione del 0 al 5.");
                    }
                    mostrarAviso(parqueadero);
                } catch (IllegalArgumentException error) {
                    System.out.println("ERROR: " + error.getMessage());
                } catch (IOException error) {
                    System.out.println("ERROR: No se guardó la operación. " + error.getMessage());
                } catch (NoSuchElementException error) {
                    System.out.println("\nEntrada incompleta: operación cancelada.");
                    return;
                }
            }
        } catch (IOException error) {
            System.err.println("No se pudo abrir el parqueadero: " + error.getMessage());
            System.exit(1);
        }
    }

    private static String leer(Scanner teclado, String mensaje) {
        System.out.print(mensaje);
        if (!teclado.hasNextLine()) {
            throw new NoSuchElementException();
        }
        return teclado.nextLine().trim();
    }

    private static LocalDateTime leerFecha(Scanner teclado, String etiqueta) {
        String texto = leer(teclado, etiqueta + " (aaaa-MM-dd HH:mm:ss; Enter = ahora): ");
        if (texto.isEmpty()) {
            return LocalDateTime.now().truncatedTo(ChronoUnit.SECONDS);
        }
        try {
            return LocalDateTime.parse(texto, FECHA);
        } catch (DateTimeParseException error) {
            throw new IllegalArgumentException("Fecha inválida. Ejemplo: 2026-10-18 08:00:00.");
        }
    }

    private static void mostrarVisitas(List<Vehiculo> visitas) {
        if (visitas.isEmpty()) {
            System.out.println("No hay vehículos para mostrar.");
        }
        for (Vehiculo visita : visitas) {
            System.out.println("ID " + visita.getId() + " | " + visita.getPlaca()
                    + " | Entrada: " + FECHA.format(visita.getEntrada())
                    + " | Salida: " + (visita.estaDentro() ? "DENTRO" : FECHA.format(visita.getSalida())));
        }
    }

    private static void mostrarAviso(Parqueadero parqueadero) {
        if (!parqueadero.getAvisoPersistencia().isEmpty()) {
            System.out.println("AVISO: " + parqueadero.getAvisoPersistencia());
        }
    }
}
