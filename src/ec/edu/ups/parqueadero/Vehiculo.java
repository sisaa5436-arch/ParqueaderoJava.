package ec.edu.ups.parqueadero;

import java.time.LocalDateTime;
import java.util.Locale;
import java.util.Objects;

/** Una visita al parqueadero. La misma placa puede tener varias visitas. */
public final class Vehiculo {
    private final long id;
    private final String placa;
    private final LocalDateTime entrada;
    private final LocalDateTime salida;

    public Vehiculo(long id, String placa, LocalDateTime entrada, LocalDateTime salida) {
        if (id <= 0) {
            throw new IllegalArgumentException("El identificador debe ser positivo.");
        }
        this.id = id;
        this.placa = normalizarPlaca(placa);
        this.entrada = Objects.requireNonNull(entrada, "Falta la fecha de entrada.");
        if (salida != null && salida.isBefore(entrada)) {
            throw new IllegalArgumentException("La salida no puede ser anterior a la entrada.");
        }
        this.salida = salida;
    }

    /** Unifica mayúsculas y guiones para evitar duplicados como ABC-1234/abc1234. */
    public static String normalizarPlaca(String placa) {
        if (placa == null) {
            throw new IllegalArgumentException("Debe ingresar una placa.");
        }
        String valor = placa.trim().toUpperCase(Locale.ROOT).replace("-", "");
        if (!valor.matches("[A-Z0-9]{5,10}")
                || !valor.matches(".*[A-Z].*") || !valor.matches(".*[0-9].*")) {
            throw new IllegalArgumentException(
                    "Placa inválida: use 5 a 10 letras/números, con al menos una letra y un número.");
        }
        return valor;
    }

    public Vehiculo conSalida(LocalDateTime fecha) {
        if (!estaDentro()) {
            throw new IllegalArgumentException("Esta visita ya tiene salida.");
        }
        return new Vehiculo(id, placa, entrada, Objects.requireNonNull(fecha));
    }

    public boolean estaDentro() { return salida == null; }
    public long getId() { return id; }
    public String getPlaca() { return placa; }
    public LocalDateTime getEntrada() { return entrada; }
    public LocalDateTime getSalida() { return salida; }
}
