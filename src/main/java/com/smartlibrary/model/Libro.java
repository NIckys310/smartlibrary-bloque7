package com.smartlibrary.model;

import com.smartlibrary.exception.LibroNoDisponibleException;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Version;

/** Entidad de dominio: libro del catálogo. Conoce su propia disponibilidad (Experto en información). */
@Entity
public class Libro {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String titulo;

    @Column(nullable = false)
    private boolean disponible = true;

    /** Bloqueo optimista: evita que dos préstamos simultáneos tomen el mismo libro. */
    @Version
    private Long version;

    protected Libro() {
        // requerido por JPA
    }

    public Libro(String titulo) {
        this.titulo = titulo;
    }

    /** R1 y R3: solo un libro disponible se presta, y al prestarse deja de estarlo. */
    public void marcarPrestado() {
        if (!disponible) {
            throw new LibroNoDisponibleException(id);
        }
        disponible = false;
    }

    public void marcarDevuelto() {
        disponible = true;
    }

    public Long getId() { return id; }
    public String getTitulo() { return titulo; }
    public void setTitulo(String titulo) { this.titulo = titulo; }
    public boolean isDisponible() { return disponible; }
}
