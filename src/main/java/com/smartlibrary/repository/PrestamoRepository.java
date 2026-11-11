package com.smartlibrary.repository;

import com.smartlibrary.model.Prestamo;
import java.util.List;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PrestamoRepository extends JpaRepository<Prestamo, Long> {

    /** R5: ¿el libro ya tiene un préstamo activo (sin fecha de devolución)? */
    boolean existsByLibroIdAndFechaDevolucionIsNull(Long libroId);

    /** Consulta de préstamos cargando estudiante y libro en una sola consulta. */
    @EntityGraph(attributePaths = {"estudiante", "libro"})
    List<Prestamo> findAllByOrderByFechaPrestamoDescIdDesc();

    @EntityGraph(attributePaths = {"estudiante", "libro"})
    List<Prestamo> findByEstudianteIdOrderByFechaPrestamoDescIdDesc(Long estudianteId);
}
