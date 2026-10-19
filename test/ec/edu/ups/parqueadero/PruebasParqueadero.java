package ec.edu.ups.parqueadero;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;

/** Pruebas reproducibles sin JUnit. Ejecutar como Java Application. */
public final class PruebasParqueadero {
    private static final LocalDateTime BASE = LocalDateTime.of(2026, 10, 18, 8, 0);
    private static final Tarifa TARIFA = new Tarifa();
    private static final List<Path> TEMPORALES = new ArrayList<>();
    private static int aprobadas;

    @FunctionalInterface
    private interface Caso { void ejecutar() throws Exception; }

    public static void main(String[] args) throws Exception {
        System.out.println("PRUEBAS PARQUEADERO | Java " + System.getProperty("java.version"));
        try {
            probar("T01", "Duración cero = USD 0.00", () -> importe("0.00", BASE, BASE));
            probar("T02", "Un segundo = USD 0.50", () -> importe("0.50", BASE, BASE.plusSeconds(1)));
            probar("T03", "59 min 59 s = USD 0.50", () -> importe("0.50", BASE, BASE.plusSeconds(3599)));
            probar("T04", "Una hora exacta = USD 0.50", () -> importe("0.50", BASE, BASE.plusHours(1)));
            probar("T05", "Una hora y un segundo = USD 1.00", () -> importe("1.00", BASE, BASE.plusSeconds(3601)));
            probar("T06", "Dos horas exactas = USD 1.00", () -> importe("1.00", BASE, BASE.plusHours(2)));
            probar("T07", "24 horas = USD 12.00", () -> importe("12.00", BASE, BASE.plusDays(1)));
            probar("T08", "Cruce de medianoche = USD 0.50", () -> {
                LocalDateTime entrada = BASE.withHour(23).withMinute(50);
                importe("0.50", entrada, entrada.plusMinutes(20));
            });
            probar("T09", "Fracción de nanosegundo inicia hora", () -> importe("1.00", BASE, BASE.plusHours(1).plusNanos(1)));
            probar("T10", "Rechaza duración negativa", () -> falla(IllegalArgumentException.class,
                    () -> TARIFA.calcularTotal(BASE, BASE.minusSeconds(1))));
            probar("T11", "Normaliza placa y rechaza símbolos", () -> {
                igual("ABC1234", Vehiculo.normalizarPlaca(" abc-1234 "));
                for (String placa : new String[] {"", "123456", "ABCDEF", "AB;1234", "A1", "AB C1234"}) {
                    falla(IllegalArgumentException.class, () -> Vehiculo.normalizarPlaca(placa));
                }
            });
            probar("T12", "Crea ambos archivos con cabeceras", () -> {
                Path dir = temporal();
                Parqueadero p = new Parqueadero(dir);
                igual(0, p.listarActivos().size());
                igual(ArchivoParqueadero.CABECERA_VEHICULOS, Files.readAllLines(dir.resolve("vehiculos.txt")).get(0));
                igual(ArchivoParqueadero.CABECERA_CAJA, Files.readAllLines(dir.resolve("caja.txt")).get(0));
            });
            probar("T13", "Entrada persiste tras reiniciar", () -> {
                Path dir = temporal();
                new Parqueadero(dir).registrarEntrada("ABC-1234", BASE);
                Parqueadero nuevo = new Parqueadero(dir);
                igual(1, nuevo.listarActivos().size());
                igual(BASE, nuevo.listarActivos().get(0).getEntrada());
            });
            probar("T14", "Impide entrada duplicada normalizada", () -> {
                Path dir = temporal();
                Parqueadero p = new Parqueadero(dir);
                p.registrarEntrada("ABC-1234", BASE);
                String antes = Files.readString(dir.resolve("vehiculos.txt"));
                falla(IllegalArgumentException.class, () -> p.registrarEntrada("abc1234", BASE.plusMinutes(1)));
                igual(antes, Files.readString(dir.resolve("vehiculos.txt")));
            });
            probar("T15", "Salida cobra y retira solo la placa indicada", () -> {
                Parqueadero p = new Parqueadero(temporal());
                p.registrarEntrada("ABC1234", BASE);
                p.registrarEntrada("XYZ5678", BASE);
                igual(new BigDecimal("1.00"), p.registrarSalida("ABC1234", BASE.plusMinutes(61)).getTotal());
                igual("XYZ5678", p.listarActivos().get(0).getPlaca());
                igual(1, p.listarActivos().size());
                igual(new BigDecimal("1.00"), p.consultarTotalCaja());
            });
            probar("T16", "Impide salida desconocida", () -> {
                Parqueadero p = new Parqueadero(temporal());
                falla(IllegalArgumentException.class, () -> p.registrarSalida("ABC1234", BASE));
                igual(new BigDecimal("0.00"), p.consultarTotalCaja());
            });
            probar("T17", "Salida anterior no altera estado", () -> {
                Parqueadero p = new Parqueadero(temporal());
                p.registrarEntrada("ABC1234", BASE);
                falla(IllegalArgumentException.class, () -> p.registrarSalida("ABC1234", BASE.minusMinutes(1)));
                igual(1, p.listarActivos().size());
                igual(0, p.listarCobros().size());
            });
            probar("T18", "Impide cobrar dos veces la misma salida", () -> {
                Parqueadero p = conSalida(temporal());
                falla(IllegalArgumentException.class, () -> p.registrarSalida("ABC1234", BASE.plusHours(2)));
                igual(1, p.listarCobros().size());
                igual(new BigDecimal("0.50"), p.consultarTotalCaja());
            });
            probar("T19", "Permite reingreso con otro identificador", () -> {
                Parqueadero p = conSalida(temporal());
                Vehiculo segunda = p.registrarEntrada("ABC1234", BASE.plusHours(2));
                igual(2L, segunda.getId());
                igual(2, p.getHistorial().size());
                igual(1, p.listarActivos().size());
            });
            probar("T20", "Reinicio conserva caja sin duplicarla", () -> {
                Path dir = temporal();
                conSalida(dir);
                new Parqueadero(dir);
                Parqueadero p = new Parqueadero(dir);
                igual(new BigDecimal("0.50"), p.consultarTotalCaja());
                igual(2, Files.readAllLines(dir.resolve("caja.txt")).size());
            });
            probar("T21", "Reconstruye caja eliminada desde historial", () -> {
                Path dir = temporal();
                conSalida(dir);
                String original = Files.readString(dir.resolve("caja.txt"));
                Files.delete(dir.resolve("caja.txt"));
                new Parqueadero(dir);
                igual(original, Files.readString(dir.resolve("caja.txt")));
            });
            probar("T22", "Historial malformado se rechaza sin borrarlo", () -> {
                Path dir = temporal();
                String contenido = ArchivoParqueadero.CABECERA_VEHICULOS + "\nregistro;inválido\n";
                Files.writeString(dir.resolve("vehiculos.txt"), contenido);
                falla(IOException.class, () -> new Parqueadero(dir));
                igual(contenido, Files.readString(dir.resolve("vehiculos.txt")));
            });
            probar("T23", "Fallo de caja avisa y permite recuperarla", () -> {
                Path dir = temporal();
                Parqueadero p = new Parqueadero(dir);
                p.registrarEntrada("ABC1234", BASE);
                Files.delete(dir.resolve("caja.txt"));
                Files.createDirectory(dir.resolve("caja.txt"));
                p.registrarSalida("ABC1234", BASE.plusMinutes(10));
                verdadero(!p.getAvisoPersistencia().isEmpty(), "Debe avisar el fallo de caja.");
                igual(0, p.listarActivos().size());
                Files.delete(dir.resolve("caja.txt"));
                Parqueadero reparado = new Parqueadero(dir);
                igual(new BigDecimal("0.50"), reparado.consultarTotalCaja());
                igual("", reparado.getAvisoPersistencia());
            });
            probar("T24", "Fallo al guardar historial no cambia memoria", () -> {
                Path dir = temporal();
                Parqueadero p = new Parqueadero(dir);
                Files.delete(dir.resolve("vehiculos.txt"));
                Files.createDirectory(dir.resolve("vehiculos.txt"));
                falla(IOException.class, () -> p.registrarEntrada("ABC1234", BASE));
                igual(0, p.listarActivos().size());
            });
            probar("T25", "No borra caja si falta un historial con cobros", () -> {
                Path dir = temporal();
                conSalida(dir);
                String caja = Files.readString(dir.resolve("caja.txt"));
                Files.delete(dir.resolve("vehiculos.txt"));
                falla(IOException.class, () -> new Parqueadero(dir));
                igual(caja, Files.readString(dir.resolve("caja.txt")));
            });
            probar("T26", "Impide reingreso anterior a una salida previa", () -> {
                Parqueadero p = conSalida(temporal());
                falla(IllegalArgumentException.class, () -> p.registrarEntrada("ABC1234", BASE.plusMinutes(5)));
                igual(1, p.getHistorial().size());
            });
            probar("T27", "Rechaza identificadores repetidos en archivo", () -> {
                Path dir = temporal();
                Files.writeString(dir.resolve("vehiculos.txt"), ArchivoParqueadero.CABECERA_VEHICULOS
                        + "\n1;ABC1234;2026-10-18T08:00;\n1;XYZ5678;2026-10-18T08:00;\n");
                falla(IOException.class, () -> new Parqueadero(dir));
            });
            probar("T28", "Rechaza visitas activas duplicadas en archivo", () -> {
                Path dir = temporal();
                Files.writeString(dir.resolve("vehiculos.txt"), ArchivoParqueadero.CABECERA_VEHICULOS
                        + "\n1;ABC1234;2026-10-18T08:00;\n2;abc-1234;2026-10-18T09:00;\n");
                falla(IOException.class, () -> new Parqueadero(dir));
            });
            probar("T29", "No expone listas modificables", () -> {
                Parqueadero p = new Parqueadero(temporal());
                p.registrarEntrada("ABC1234", BASE);
                falla(UnsupportedOperationException.class, () -> p.getHistorial().clear());
                falla(UnsupportedOperationException.class, () -> p.listarActivos().clear());
            });
            probar("T30", "Suma tres cobros con exactitud decimal", () -> {
                Parqueadero p = new Parqueadero(temporal());
                for (int i = 0; i < 3; i++) {
                    String placa = "ABC123" + i;
                    p.registrarEntrada(placa, BASE);
                    p.registrarSalida(placa, BASE.plusMinutes(20));
                }
                igual(new BigDecimal("1.50"), p.consultarTotalCaja());
            });
            System.out.println("RESULTADO: " + aprobadas + "/30 pruebas aprobadas.");
        } finally {
            for (Path dir : TEMPORALES) {
                try (Stream<Path> rutas = Files.walk(dir)) {
                    for (Path ruta : rutas.sorted(Comparator.reverseOrder()).toList()) {
                        Files.deleteIfExists(ruta);
                    }
                }
            }
        }
    }

    private static Path temporal() throws IOException {
        Path dir = Files.createTempDirectory("prueba-parqueadero-");
        TEMPORALES.add(dir);
        return dir;
    }

    private static Parqueadero conSalida(Path dir) throws IOException {
        Parqueadero p = new Parqueadero(dir);
        p.registrarEntrada("ABC1234", BASE);
        p.registrarSalida("ABC1234", BASE.plusMinutes(10));
        return p;
    }

    private static void probar(String id, String descripcion, Caso caso) throws Exception {
        try {
            caso.ejecutar();
            aprobadas++;
            System.out.println("[OK] " + id + " " + descripcion);
        } catch (Exception | AssertionError error) {
            System.out.println("[FALLO] " + id + " " + descripcion);
            throw error;
        }
    }

    private static void importe(String esperado, LocalDateTime entrada, LocalDateTime salida) {
        igual(new BigDecimal(esperado), TARIFA.calcularTotal(entrada, salida));
    }

    private static void igual(Object esperado, Object actual) {
        verdadero(esperado.equals(actual), "Esperado: " + esperado + "; recibido: " + actual);
    }

    private static void verdadero(boolean condicion, String mensaje) {
        if (!condicion) { throw new AssertionError(mensaje); }
    }

    private static void falla(Class<? extends Throwable> tipo, Caso caso) throws Exception {
        try {
            caso.ejecutar();
        } catch (Throwable error) {
            if (tipo.isInstance(error)) { return; }
            throw new AssertionError("Excepción inesperada: " + error, error);
        }
        throw new AssertionError("Se esperaba " + tipo.getSimpleName());
    }
}
