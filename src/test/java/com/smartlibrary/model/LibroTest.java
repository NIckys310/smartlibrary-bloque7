package com.smartlibrary.model;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.smartlibrary.exception.LibroNoDisponibleException;
import org.junit.jupiter.api.Test;

/** Prueba unitaria de la regla de disponibilidad en la entidad (sin Spring). */
class LibroTest {

    @Test
    void unLibroDisponibleSePrestaYDejaDeEstarDisponible() {
        Libro libro = new Libro("Clean Code");
        libro.marcarPrestado();
        assertThat(libro.isDisponible()).isFalse();
    }

    @Test
    void unLibroPrestadoNoSePuedeVolverAPrestar() {
        Libro libro = new Libro("Clean Code");
        libro.marcarPrestado();
        assertThatThrownBy(libro::marcarPrestado).isInstanceOf(LibroNoDisponibleException.class);
    }

    @Test
    void alDevolverseVuelveAEstarDisponible() {
        Libro libro = new Libro("Clean Code");
        libro.marcarPrestado();
        libro.marcarDevuelto();
        assertThat(libro.isDisponible()).isTrue();
    }
}
