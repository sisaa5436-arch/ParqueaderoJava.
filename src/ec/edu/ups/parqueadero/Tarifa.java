package ec.edu.ups.parqueadero;

import java.math.BigDecimal;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Objects;

/** Calcula el precio por cada hora iniciada, sin usar double para el dinero. */
public final class Tarifa {
    public static final BigDecimal PRECIO_HORA = new BigDecimal("0.50");

    public long calcularHoras(LocalDateTime entrada, LocalDateTime salida) {
        Objects.requireNonNull(entrada, "Falta la entrada.");
        Objects.requireNonNull(salida, "Falta la salida.");
        Duration tiempo = Duration.between(entrada, salida);
        if (tiempo.isNegative()) {
            throw new IllegalArgumentException("La salida no puede ser anterior a la entrada.");
        }
        long segundos = tiempo.getSeconds();
        long horas = segundos / 3600;
        // Cualquier resto, incluso menor a un segundo, inicia otra hora.
        if (segundos % 3600 != 0 || tiempo.getNano() != 0) {
            horas++;
        }
        return horas; // Supuesto explícito: duración cero no genera cobro.
    }

    public BigDecimal calcularTotal(LocalDateTime entrada, LocalDateTime salida) {
        return PRECIO_HORA.multiply(BigDecimal.valueOf(calcularHoras(entrada, salida)));
    }
}
