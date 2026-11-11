# Evidencias de pruebas manuales (curl)

API ejecutada con `java -jar target/smartlibrary-1.0.0.jar` y datos iniciales de `data.sql`.

### 1. Préstamo de libro disponible → 201 Created
```http
POST /api/prestamos {"estudianteId":1,"libroId":1}
```
```text
HTTP/1.1 201 
Location: http://127.0.0.1:8081/api/prestamos/3
Content-Type: application/json

{"id":3,"estudianteId":1,"estudianteNombre":"Ana Torres","libroId":1,"libroTitulo":"Clean Code","fechaPrestamo":"2026-11-11","fechaDevolucion":null,"activo":true}

```

### 2. Libro ya prestado → 409 Conflict
```http
POST /api/prestamos {"estudianteId":3,"libroId":1}
```
```text
HTTP/1.1 409 
Content-Type: application/problem+json

{"type":"about:blank","title":"Libro no disponible","status":409,"detail":"El libro con id 1 no está disponible","instance":"/api/prestamos"}

```

### 3. Estudiante inexistente → 404 Not Found
```http
POST /api/prestamos {"estudianteId":999,"libroId":2}
```
```text
HTTP/1.1 404 
Content-Type: application/problem+json

{"type":"about:blank","title":"Recurso no encontrado","status":404,"detail":"Estudiante con id 999 no existe","instance":"/api/prestamos"}

```

### 4. Libro inexistente → 404 Not Found
```http
POST /api/prestamos {"estudianteId":1,"libroId":999}
```
```text
HTTP/1.1 404 
Content-Type: application/problem+json

{"type":"about:blank","title":"Recurso no encontrado","status":404,"detail":"Libro con id 999 no existe","instance":"/api/prestamos"}

```

### 5. Solicitud inválida → 400 Bad Request (R4)
```http
POST /api/prestamos {"estudianteId":1}
```
```text
HTTP/1.1 400 
Content-Type: application/problem+json

{"type":"about:blank","title":"Solicitud inválida","status":400,"detail":"libroId es obligatorio","instance":"/api/prestamos"}

```

### 6. Consulta de préstamos → 200 OK
```http
GET /api/prestamos
```
```text
HTTP/1.1 200 
Content-Type: application/json

[{"id":3,"estudianteId":1,"estudianteNombre":"Ana Torres","libroId":1,"libroTitulo":"Clean Code","fechaPrestamo":"2026-11-11","fechaDevolucion":null,"activo":true},{"id":1,"estudianteId":2,"estudianteNombre":"Luis Gómez","libroId":3,"libroTitulo":"Cien años de soledad","fechaPrestamo":"2026-11-06","fechaDevolucion":null,"activo":true},{"id":2,"estudianteId":1,"estudianteNombre":"Ana Torres","libroId":4,"libroTitulo":"Patrones de Diseño","fechaPrestamo":"2026-10-12","fechaDevolucion":"2026-10-26","activo":false}]

```

