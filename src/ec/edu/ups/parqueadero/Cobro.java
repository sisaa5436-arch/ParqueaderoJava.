package ec.edu.ups.parqueadero;

import java.math.BigDecimal;

/** Comprobante calculado a partir de una visita que ya terminó. */
public final class Cobro {
    private final Vehiculo vehiculo;
    private final long horasCobradas;
    private final BigDecimal total;

    public Cobro(Vehiculo vehiculo, Tarifa tarifa) {
        if (vehiculo.estaDentro()) {
            throw new IllegalArgumentException("No se puede cobrar una visita sin salida.");
        }
        this.vehiculo = vehiculo;
        this.horasCobradas = tarifa.calcularHoras(vehiculo.getEntrada(), vehiculo.getSalida());
        this.total = tarifa.calcularTotal(vehiculo.getEntrada(), vehiculo.getSalida());
    }

    public Vehiculo getVehiculo() { return vehiculo; }
    public long getHorasCobradas() { return horasCobradas; }
    public BigDecimal getTotal() { return total; }
}
