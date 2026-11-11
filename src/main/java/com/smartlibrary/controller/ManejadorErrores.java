package com.smartlibrary.controller;

import com.smartlibrary.exception.LibroNoDisponibleException;
import com.smartlibrary.exception.RecursoNoEncontradoException;
import java.util.stream.Collectors;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Traduce excepciones de negocio a códigos HTTP (formato RFC 9457 Problem Details). */
@RestControllerAdvice
public class ManejadorErrores {

    @ExceptionHandler(RecursoNoEncontradoException.class)
    public ProblemDetail noEncontrado(RecursoNoEncontradoException ex) {
        return problema(HttpStatus.NOT_FOUND, "Recurso no encontrado", ex.getMessage());
    }

    @ExceptionHandler(LibroNoDisponibleException.class)
    public ProblemDetail noDisponible(LibroNoDisponibleException ex) {
        return problema(HttpStatus.CONFLICT, "Libro no disponible", ex.getMessage());
    }

    /** Dos préstamos simultáneos del mismo libro: el segundo pierde. */
    @ExceptionHandler(OptimisticLockingFailureException.class)
    public ProblemDetail concurrencia(OptimisticLockingFailureException ex) {
        return problema(HttpStatus.CONFLICT, "Conflicto de concurrencia",
                "El libro fue modificado por otra solicitud; intente de nuevo");
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail datosInvalidos(MethodArgumentNotValidException ex) {
        String detalle = ex.getBindingResult().getFieldErrors().stream()
                .map(e -> e.getDefaultMessage())
                .collect(Collectors.joining("; "));
        return problema(HttpStatus.BAD_REQUEST, "Solicitud inválida", detalle);
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ProblemDetail jsonInvalido(HttpMessageNotReadableException ex) {
        return problema(HttpStatus.BAD_REQUEST, "Solicitud inválida", "El cuerpo JSON no es válido");
    }

    private static ProblemDetail problema(HttpStatus estado, String titulo, String detalle) {
        ProblemDetail problema = ProblemDetail.forStatusAndDetail(estado, detalle);
        problema.setTitle(titulo);
        return problema;
    }
}
