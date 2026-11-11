package com.smartlibrary.repository;

import com.smartlibrary.model.Estudiante;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EstudianteRepository extends JpaRepository<Estudiante, Long> {
}
