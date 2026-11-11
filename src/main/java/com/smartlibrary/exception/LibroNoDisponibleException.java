package com.smartlibrary.exception;

/** Se traduce a 409 Conflict: el libro ya tiene un préstamo activo. */
public class LibroNoDisponibleException extends RuntimeException {

    public LibroNoDisponibleException(Long libroId) {
        super("El libro con id " + libroId + " no está disponible");
    }
}
