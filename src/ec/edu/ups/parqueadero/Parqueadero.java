package ec.edu.ups.parqueadero;

import java.io.IOException;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Reglas del negocio. Se usa una sola instancia de la aplicación a la vez. */
public final class Parqueadero {
    private final ArchivoParqueadero archivos;
    private final Tarifa tarifa = new Tarifa();
    private List<Vehiculo> visitas;
    private String avisoPersistencia = "";

    public Parqueadero(Path directorio) throws IOException {
        archivos = new ArchivoParqueadero(directorio);
        visitas = archivos.cargarVehiculos();
        actualizarCaja();
    }

    public Vehiculo registrarEntrada(String placa, LocalDateTime entrada) throws IOException {
        String normalizada = Vehiculo.normalizarPlaca(placa);
        Objects.requireNonNull(entrada, "Falta la fecha de entrada.");
        long ultimoId = 0;
        for (Vehiculo visita : visitas) {
            ultimoId = Math.max(ultimoId, visita.getId());
            if (visita.getPlaca().equals(normalizada)) {
                if (visita.estaDentro()) {
                    throw new IllegalArgumentException("El vehículo ya está dentro del parqueadero.");
                }
                if (entrada.isBefore(visita.getSalida())) {
                    throw new IllegalArgumentException("La entrada se superpone con una visita anterior.");
                }
            }
        }
        Vehiculo nuevo = new Vehiculo(Math.addExact(ultimoId, 1), normalizada, entrada, null);
        List<Vehiculo> nuevas = new ArrayList<>(visitas);
        nuevas.add(nuevo);
        guardarCambios(nuevas);
        return nuevo;
    }

    public List<Vehiculo> listarActivos() {
        List<Vehiculo> activos = new ArrayList<>();
        for (Vehiculo visita : visitas) {
            if (visita.estaDentro()) {
                activos.add(visita);
            }
        }
        return List.copyOf(activos);
    }

    public List<Vehiculo> getHistorial() { return List.copyOf(visitas); }
    public Path getDirectorio() { return archivos.getDirectorio(); }
    public String getAvisoPersistencia() { return avisoPersistencia; }

    private void guardarCambios(List<Vehiculo> nuevas) throws IOException {
        // Primero se confirma el historial. Si falla, el estado en memoria no cambia.
        archivos.guardarVehiculos(nuevas);
        visitas = nuevas;
        actualizarCaja();
    }

    public void actualizarCaja() {
        avisoPersistencia = "";
        try {
            // Reconstruir evita agregar dos veces el mismo cobro al reiniciar.
            archivos.guardarCaja(visitas, tarifa);
        } catch (IOException error) {
            avisoPersistencia = "El historial está guardado, pero caja.txt no pudo actualizarse: "
                    + error.getMessage() + ". Corrija el acceso y consulte la caja o reinicie.";
        }
    }
}
