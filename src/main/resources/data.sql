-- Datos iniciales de prueba (los estudiantes y libros ya están registrados).
INSERT INTO estudiante (nombre, correo) VALUES ('Ana Torres', 'ana.torres@example.com');
INSERT INTO estudiante (nombre, correo) VALUES ('Luis Gómez', 'luis.gomez@example.com');
INSERT INTO estudiante (nombre, correo) VALUES ('María Pérez', 'maria.perez@example.com');

INSERT INTO libro (titulo, disponible, version) VALUES ('Clean Code', TRUE, 0);
INSERT INTO libro (titulo, disponible, version) VALUES ('Diseño de Software', TRUE, 0);
INSERT INTO libro (titulo, disponible, version) VALUES ('Cien años de soledad', FALSE, 0);
INSERT INTO libro (titulo, disponible, version) VALUES ('Patrones de Diseño', TRUE, 0);

-- Préstamo activo (libro 3) y uno histórico ya devuelto (libro 4): R5.
INSERT INTO prestamo (fecha_prestamo, fecha_devolucion, estudiante_id, libro_id) VALUES (DATEADD('DAY', -5, CURRENT_DATE), NULL, 2, 3);
INSERT INTO prestamo (fecha_prestamo, fecha_devolucion, estudiante_id, libro_id) VALUES (DATEADD('DAY', -30, CURRENT_DATE), DATEADD('DAY', -16, CURRENT_DATE), 1, 4);
