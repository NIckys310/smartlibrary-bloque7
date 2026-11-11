package com.smartlibrary.controller;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.smartlibrary.repository.LibroRepository;
import com.smartlibrary.repository.PrestamoRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.transaction.annotation.Transactional;

/**
 * Escenarios de la Actividad 6 contra la API completa (Controller → Service → Repository → H2).
 * Datos iniciales (data.sql): estudiantes 1–3; libros 1, 2 y 4 disponibles; libro 3 prestado;
 * 2 préstamos (uno activo, uno histórico). Cada prueba se revierte al terminar.
 */
@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class PrestamoControllerTest {

    @Autowired private MockMvc mvc;
    @Autowired private PrestamoRepository prestamoRepository;
    @Autowired private LibroRepository libroRepository;

    private ResultActions prestar(String json) throws Exception {
        return mvc.perform(post("/api/prestamos").contentType(MediaType.APPLICATION_JSON).content(json));
    }

    @Test
    @DisplayName("Préstamo de libro disponible → 201 Created y préstamo registrado")
    void prestamoExitoso() throws Exception {
        long antes = prestamoRepository.count();

        prestar("{\"estudianteId\": 1, \"libroId\": 1}")
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", org.hamcrest.Matchers.matchesPattern(".*/api/prestamos/\\d+")))
                .andExpect(jsonPath("$.estudianteId").value(1))
                .andExpect(jsonPath("$.libroTitulo").value("Clean Code"))
                .andExpect(jsonPath("$.activo").value(true));

        assertThat(prestamoRepository.count()).isEqualTo(antes + 1);
        assertThat(libroRepository.findById(1L).orElseThrow().isDisponible()).isFalse(); // R3
    }

    @Test
    @DisplayName("Libro ya prestado → 409 Conflict; sin nuevo préstamo")
    void libroYaPrestado() throws Exception {
        long antes = prestamoRepository.count();

        prestar("{\"estudianteId\": 1, \"libroId\": 3}")
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.title").value("Libro no disponible"));

        assertThat(prestamoRepository.count()).isEqualTo(antes);
    }

    @Test
    @DisplayName("Prestar dos veces el mismo libro → la segunda vez 409")
    void segundoPrestamoDelMismoLibro() throws Exception {
        prestar("{\"estudianteId\": 1, \"libroId\": 2}").andExpect(status().isCreated());
        prestar("{\"estudianteId\": 3, \"libroId\": 2}").andExpect(status().isConflict());
    }

    @Test
    @DisplayName("Estudiante inexistente → 404 Not Found")
    void estudianteInexistente() throws Exception {
        long antes = prestamoRepository.count();

        prestar("{\"estudianteId\": 999, \"libroId\": 1}")
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Estudiante con id 999 no existe"));

        assertThat(prestamoRepository.count()).isEqualTo(antes);
        assertThat(libroRepository.findById(1L).orElseThrow().isDisponible()).isTrue();
    }

    @Test
    @DisplayName("Libro inexistente → 404 Not Found")
    void libroInexistente() throws Exception {
        prestar("{\"estudianteId\": 1, \"libroId\": 999}")
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Libro con id 999 no existe"));
    }

    @Test
    @DisplayName("Solicitud inválida → 400 Bad Request; sin préstamo (R4)")
    void solicitudInvalida() throws Exception {
        long antes = prestamoRepository.count();

        prestar("{\"estudianteId\": 1}").andExpect(status().isBadRequest());
        prestar("no es json").andExpect(status().isBadRequest());

        assertThat(prestamoRepository.count()).isEqualTo(antes);
    }

    @Test
    @DisplayName("Consulta de préstamos → 200 OK con registros")
    void consultaDePrestamos() throws Exception {
        mvc.perform(get("/api/prestamos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].libroTitulo").value("Cien años de soledad"))
                .andExpect(jsonPath("$[0].activo").value(true))
                .andExpect(jsonPath("$[1].activo").value(false));
    }

    @Test
    @DisplayName("Consulta filtrada por estudiante y por id")
    void consultaFiltrada() throws Exception {
        mvc.perform(get("/api/prestamos").param("estudianteId", "2"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].estudianteNombre").value("Luis Gómez"));
        mvc.perform(get("/api/prestamos/999")).andExpect(status().isNotFound());
    }
}
