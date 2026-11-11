package com.smartlibrary.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import java.time.LocalDate;

/**
 * Entidad de dominio: préstamo de un libro a un estudiante (R2).
 * Asociaciones (no composiciones): Estudiante y Libro existen sin el préstamo.
 */
@Entity
public class Prestamo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private LocalDate fechaPrestamo;

    /** [0..1]: null mientras el préstamo está activo. */
    private LocalDate fechaDevolucion;

    @ManyToOne(optional = false, fetch = FetchType.LAZY)
    @JoinColumn(name = "estudiante_id")
    private Estudiante estudiante;

    @ManyToOne(optional = false, fetch = FetchType.LAZY)
    @JoinColumn(name = "libro_id")
    private Libro libro;

    protected Prestamo() {
        // requerido por JPA
    }

    public Prestamo(Estudiante estudiante, Libro libro, LocalDate fechaPrestamo) {
        this.estudiante = estudiante;
        this.libro = libro;
        this.fechaPrestamo = fechaPrestamo;
    }

    public boolean estaActivo() {
        return fechaDevolucion == null;
    }

    public Long getId() { return id; }
    public LocalDate getFechaPrestamo() { return fechaPrestamo; }
    public LocalDate getFechaDevolucion() { return fechaDevolucion; }
    public void setFechaDevolucion(LocalDate fechaDevolucion) { this.fechaDevolucion = fechaDevolucion; }
    public Estudiante getEstudiante() { return estudiante; }
    public Libro getLibro() { return libro; }
}
