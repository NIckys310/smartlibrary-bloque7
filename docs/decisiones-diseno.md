# Decisiones de diseño (entregable 6)

**1. Tres capas con una sola dirección.** Las dependencias van `PrestamoController → PrestamoService → Repository`. El Controller solo traduce HTTP: recibe el JSON, valida el formato con `@Valid` y devuelve el código de estado. Nunca toca un Repository. Así, cambiar la base de datos (H2 → MongoDB, por ejemplo) no afecta a la capa web, y cambiar la API no afecta a las reglas.

**2. Las reglas viven en el Service y en la entidad.** `PrestamoService` es el **Controlador GRASP** del caso de uso «Registrar préstamo»: coordina la búsqueda del estudiante y del libro, la verificación de disponibilidad, la creación del préstamo y el guardado. La regla de disponibilidad (R1, R3) está en `Libro.marcarPrestado()`, porque el libro es el **Experto en información**: conoce su propio estado. El Service, además, consulta `existsByLibroIdAndFechaDevolucionIsNull` para garantizar R5 (como máximo un préstamo activo por libro), aunque el indicador `disponible` llegara a estar desincronizado.

**3. Transacción única.** `registrarPrestamo` es `@Transactional`: marcar el libro como prestado y guardar el préstamo ocurren juntos o no ocurre ninguno. Si se lanza una excepción, se revierte todo (R4: una solicitud inválida no crea préstamo). Para la concurrencia, `Libro` tiene `@Version` (bloqueo optimista): si dos solicitudes prestan el mismo libro a la vez, la segunda recibe 409.

**4. Asociación frente a dependencia.** Se dibuja **asociación dirigida** cuando una clase conserva la referencia como atributo: los repositorios inyectados en el Service, el Service inyectado en el Controller y `Prestamo → Estudiante/Libro` (`@ManyToOne`). Se dibuja **dependencia** cuando el uso es puntual: DTO como parámetro o retorno, excepciones lanzadas. Entre entidades no hay composición ni agregación: estudiante y libro existen antes y después del préstamo, y borrar un préstamo no los borra.

**5. Interfaces y realización.** Los repositorios son interfaces que **heredan** de `JpaRepository<T, ID>` (generalización entre interfaces). No se dibuja una realización propia porque Spring Data genera la implementación en tiempo de ejecución; dibujar una clase inventada sería describir código que no existe.

**6. DTO separados de las entidades.** `PrestamoRequest` define el contrato de entrada (dos IDs obligatorios y positivos) y `PrestamoResponse` el de salida. Esto evita exponer las entidades JPA (y sus relaciones *lazy*) en el JSON, y permite cambiar la base de datos sin romper el contrato de la API.

**7. Errores explícitos.** `RecursoNoEncontradoException → 404` y `LibroNoDisponibleException → 409` se traducen en un único `@RestControllerAdvice` (`ManejadorErrores`) al formato estándar *Problem Details* (RFC 9457). El Service no conoce HTTP; solo lanza excepciones del dominio.

**8. Trazabilidad.** Cada mensaje del diagrama de secuencia es una operación del diagrama de clases (`registrar`, `registrarPrestamo`, `findById`, `existsByLibroIdAndFechaDevolucionIsNull`, `marcarPrestado`, `save`), y cada regla tiene al menos una prueba automática (ver la tabla del README).
