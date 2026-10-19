package ec.edu.ups.parqueadero;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Persistencia en texto: vehiculos es el historial; caja se deriva de sus salidas. */
public final class ArchivoParqueadero {
    public static final String CABECERA_VEHICULOS = "id;placa;entrada;salida";
    public static final String CABECERA_CAJA = "id;placa;entrada;salida;horas_cobradas;total_usd";
    private final Path directorio;

    public ArchivoParqueadero(Path directorio) throws IOException {
        this.directorio = directorio.toAbsolutePath().normalize();
        Files.createDirectories(this.directorio);
    }

    public Path getDirectorio() { return directorio; }

    public List<Vehiculo> cargarVehiculos() throws IOException {
        Path archivo = directorio.resolve("vehiculos.txt");
        if (!Files.exists(archivo)) {
            Path caja = directorio.resolve("caja.txt");
            if (Files.exists(caja) && Files.readAllLines(caja, StandardCharsets.UTF_8)
                    .stream().anyMatch(linea -> !linea.isBlank() && !linea.equals(CABECERA_CAJA))) {
                throw new IOException("Falta vehiculos.txt, pero existe una caja con datos. Restaure el historial.");
            }
            guardarVehiculos(List.of());
        }
        List<String> lineas = Files.readAllLines(archivo, StandardCharsets.UTF_8);
        if (lineas.isEmpty() || !CABECERA_VEHICULOS.equals(lineas.get(0))) {
            throw new IOException("Cabecera inválida en vehiculos.txt; no se modificaron sus datos.");
        }
        List<Vehiculo> visitas = new ArrayList<>();
        Set<Long> ids = new HashSet<>();
        Map<String, Vehiculo> ultimaVisita = new HashMap<>();
        for (int i = 1; i < lineas.size(); i++) {
            try {
                String[] campos = lineas.get(i).split(";", -1);
                if (campos.length != 4) {
                    throw new IllegalArgumentException("Se esperaban cuatro campos.");
                }
                Vehiculo visita = new Vehiculo(Long.parseLong(campos[0]), campos[1],
                        LocalDateTime.parse(campos[2]),
                        campos[3].isEmpty() ? null : LocalDateTime.parse(campos[3]));
                if (!ids.add(visita.getId())) {
                    throw new IllegalArgumentException("Identificador repetido.");
                }
                Vehiculo anterior = ultimaVisita.put(visita.getPlaca(), visita);
                if (anterior != null && (anterior.estaDentro()
                        || visita.getEntrada().isBefore(anterior.getSalida()))) {
                    throw new IllegalArgumentException("Visitas superpuestas de la misma placa.");
                }
                visitas.add(visita);
            } catch (RuntimeException error) {
                throw new IOException("vehiculos.txt, línea " + (i + 1) + ": " + error.getMessage(), error);
            }
        }
        return visitas;
    }

    public void guardarVehiculos(List<Vehiculo> visitas) throws IOException {
        List<String> lineas = new ArrayList<>();
        lineas.add(CABECERA_VEHICULOS);
        for (Vehiculo visita : visitas) {
            lineas.add(visita.getId() + ";" + visita.getPlaca() + ";" + visita.getEntrada()
                    + ";" + (visita.estaDentro() ? "" : visita.getSalida()));
        }
        escribirAtomico(directorio.resolve("vehiculos.txt"), lineas);
    }

    public void guardarCaja(List<Vehiculo> visitas, Tarifa tarifa) throws IOException {
        List<String> lineas = new ArrayList<>();
        lineas.add(CABECERA_CAJA);
        for (Vehiculo visita : visitas) {
            if (!visita.estaDentro()) {
                Cobro cobro = new Cobro(visita, tarifa);
                lineas.add(visita.getId() + ";" + visita.getPlaca() + ";" + visita.getEntrada()
                        + ";" + visita.getSalida() + ";" + cobro.getHorasCobradas()
                        + ";" + cobro.getTotal().toPlainString());
            }
        }
        escribirAtomico(directorio.resolve("caja.txt"), lineas);
    }

    private void escribirAtomico(Path destino, List<String> lineas) throws IOException {
        Path temporal = Files.createTempFile(directorio, "parqueadero-", ".tmp");
        try {
            Files.write(temporal, lineas, StandardCharsets.UTF_8);
            try {
                Files.move(temporal, destino, StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException error) {
                Files.move(temporal, destino, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temporal);
        }
    }
}
