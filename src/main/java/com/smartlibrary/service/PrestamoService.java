package com.smartlibrary.service;

import com.smartlibrary.dto.PrestamoRequest;
import com.smartlibrary.dto.PrestamoResponse;
import com.smartlibrary.model.Estudiante;
import com.smartlibrary.model.Libro;
import com.smartlibrary.model.Prestamo;
import com.smartlibrary.repository.EstudianteRepository;
import com.smartlibrary.repository.LibroRepository;
import com.smartlibrary.repository.PrestamoRepository;
import com.smartlibrary.exception.LibroNoDisponibleException;
import com.smartlibrary.exception.RecursoNoEncontradoException;
import java.time.Clock;
import java.time.LocalDate;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Capa de negocio. Controlador GRASP del caso de uso «Registrar préstamo»:
 * coordina repositorios y entidades y aplica las reglas R1–R5.
 */
@Service
public class PrestamoService {

    private final EstudianteRepository estudianteRepository;
    private final LibroRepository libroRepository;
    private final PrestamoRepository prestamoRepository;
    private final Clock clock;

    public PrestamoService(EstudianteRepository estudianteRepository,
                           LibroRepository libroRepository,
                           PrestamoRepository prestamoRepository,
                           Clock clock) {
        this.estudianteRepository = estudianteRepository;
        this.libroRepository = libroRepository;
        this.prestamoRepository = prestamoRepository;
        this.clock = clock;
    }

    /**
     * Una sola transacción: crear el préstamo y cambiar la disponibilidad
     * ocurren juntos o no ocurre ninguno (R3, R4).
     */
    @Transactional
    public PrestamoResponse registrarPrestamo(PrestamoRequest request) {
        Estudiante estudiante = estudianteRepository.findById(request.estudianteId())
                .orElseThrow(() -> new RecursoNoEncontradoException("Estudiante", request.estudianteId()));
        Libro libro = libroRepository.findById(request.libroId())
                .orElseThrow(() -> new RecursoNoEncontradoException("Libro", request.libroId()));

        // R5: como máximo un préstamo activo por libro (defensa además del flag disponible).
        if (prestamoRepository.existsByLibroIdAndFechaDevolucionIsNull(libro.getId())) {
            throw new LibroNoDisponibleException(libro.getId());
        }
        libro.marcarPrestado(); // R1 + R3 (lanza LibroNoDisponibleException)

        Prestamo prestamo = new Prestamo(estudiante, libro, LocalDate.now(clock)); // R2
        return PrestamoResponse.desde(prestamoRepository.save(prestamo));
    }

    @Transactional(readOnly = true)
    public List<PrestamoResponse> consultarPrestamos(Long estudianteId) {
        List<Prestamo> prestamos = estudianteId == null
                ? prestamoRepository.findAllByOrderByFechaPrestamoDescIdDesc()
                : prestamoRepository.findByEstudianteIdOrderByFechaPrestamoDescIdDesc(estudianteId);
        return prestamos.stream().map(PrestamoResponse::desde).toList();
    }

    @Transactional(readOnly = true)
    public PrestamoResponse consultarPrestamo(Long id) {
        return prestamoRepository.findById(id)
                .map(PrestamoResponse::desde)
                .orElseThrow(() -> new RecursoNoEncontradoException("Préstamo", id));
    }
}
