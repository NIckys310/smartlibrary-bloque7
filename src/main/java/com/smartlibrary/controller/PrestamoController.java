package com.smartlibrary.controller;

import com.smartlibrary.dto.PrestamoRequest;
import com.smartlibrary.dto.PrestamoResponse;
import com.smartlibrary.service.PrestamoService;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

/** Capa de presentación: traduce HTTP ↔ casos de uso. No contiene reglas de negocio. */
@RestController
@RequestMapping("/api/prestamos")
public class PrestamoController {

    private final PrestamoService prestamoService;

    public PrestamoController(PrestamoService prestamoService) {
        this.prestamoService = prestamoService;
    }

    @PostMapping
    public ResponseEntity<PrestamoResponse> registrar(@Valid @RequestBody PrestamoRequest request) {
        PrestamoResponse creado = prestamoService.registrarPrestamo(request);
        URI ubicacion = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(creado.id()).toUri();
        return ResponseEntity.created(ubicacion).body(creado);
    }

    @GetMapping
    public List<PrestamoResponse> consultar(@RequestParam(required = false) Long estudianteId) {
        return prestamoService.consultarPrestamos(estudianteId);
    }

    @GetMapping("/{id}")
    public PrestamoResponse consultarPorId(@PathVariable Long id) {
        return prestamoService.consultarPrestamo(id);
    }
}
