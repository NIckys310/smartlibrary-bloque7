"""Entregable 1: diagrama inicial de SmartLibrary con observaciones (estilo Visual Paradigm)."""
import sys
from vp_uml import Box, anchor, edge, note, render

gestor = Box("GestorPrestamos", 40, 300, attrs=[
    "-estudiantes : List<Estudiante>",
    "-libros : List<Libro>",
    "-prestamos : List<Prestamo>",
], ops=[
    "+GestorPrestamos()",
    "+registrarPrestamo(e : Estudiante, l : Libro) : Prestamo",
    "+getEstudiantes() : List<Estudiante>",
    "+setEstudiantes(lista) : void",
    "+getLibros() : List<Libro>",
    "+setLibros(lista) : void",
    "+getPrestamos() : List<Prestamo>",
    "+setPrestamos(lista) : void",
])
est = Box("Estudiante", 560, 40, attrs=[
    "-id : Long", "-nombre : String", "-correo : String",
], ops=[
    "+Estudiante(id, nombre, correo)",
    "+getId() : Long / setId(id) : void",
    "+getNombre() : String / setNombre(nombre) : void",
    "+getCorreo() : String / setCorreo(correo) : void",
])
libro = Box("Libro", 560, 0, attrs=[
    "-id : Long", "-titulo : String", "-disponible : boolean",
], ops=[
    "+Libro(id, titulo, disponible)",
    "+getId() : Long / setId(id) : void",
    "+getTitulo() : String / setTitulo(titulo) : void",
    "+isDisponible() : boolean",
    "+setDisponible(valor) : void",
    "+marcarPrestado() : void",
])
libro.y = est.bottom + 60
libro.x = est.x + (est.w - libro.w) / 2
prest = Box("Prestamo", max(est.right, libro.right) + 170, 0, attrs=[
    "-id : Long",
    "-fechaPrestamo : LocalDate",
    "-fechaDevolucion : LocalDate [0..1]",
    "-estudiante : Estudiante",
    "-libro : Libro",
], ops=[
    "+Prestamo(id, fecha, estudiante, libro)",
    "+getId() : Long / setId(id) : void",
    "+getFechaPrestamo() : LocalDate",
    "+setFechaPrestamo(fecha) : void",
    "+getFechaDevolucion() : LocalDate",
    "+setFechaDevolucion(fecha) : void",
    "+getEstudiante() : Estudiante",
    "+setEstudiante(estudiante) : void",
    "+getLibro() : Libro / setLibro(libro) : void",
])
prest.y = (est.y + libro.bottom) / 2 - prest.h / 2
gestor.y = (est.y + libro.bottom) / 2 - gestor.h / 2


def lbl(x, y, t, a="start"):
    return (x, y, t, a)


y_g_est = gestor.y + 22
y_g_lib = gestor.cy
edges = [
    edge([(gestor.right, y_g_est), (est.x - 40, y_g_est), (est.x - 40, est.cy), (est.x, est.cy)], "link",
         labels=[lbl(gestor.right + 6, y_g_est - 5, "1"), lbl(est.x - 6, est.cy - 5, "0..*", "end"),
                 lbl(est.x - 46, (y_g_est + est.cy) / 2, "registra", "end")]),
    edge([(gestor.right, y_g_lib), (libro.x, y_g_lib)], "link",
         labels=[lbl(gestor.right + 6, y_g_lib - 5, "1"), lbl(libro.x - 6, y_g_lib - 5, "0..*", "end"),
                 lbl((gestor.right + libro.x) / 2, y_g_lib + 14, "administra", "middle")]),
    edge([(gestor.cx, gestor.bottom), (gestor.cx, libro.bottom + 70), (prest.cx, libro.bottom + 70),
          (prest.cx, prest.bottom)], "link",
         labels=[lbl(gestor.cx + 6, gestor.bottom + 14, "1"), lbl(prest.cx + 6, prest.bottom + 14, "0..*"),
                 lbl((gestor.cx + prest.cx) / 2, libro.bottom + 64, "gestiona", "middle")]),
    edge([(est.right, est.cy), (prest.x - 50, est.cy), (prest.x - 50, prest.y + 30), (prest.x, prest.y + 30)],
         "link",
         labels=[lbl(est.right + 6, est.cy - 5, "1"), lbl(prest.x - 6, prest.y + 25, "0..*", "end"),
                 lbl(prest.x - 56, (est.cy + prest.y + 30) / 2 + 4, "historial", "end")]),
    edge([(libro.right, libro.cy), (prest.x, libro.cy)], "link",
         labels=[lbl(libro.right + 6, libro.cy - 5, "1"), lbl(prest.x - 6, libro.cy - 5, "0..*", "end"),
                 lbl((libro.right + prest.x) / 2, libro.cy + 14, "historial", "middle")]),
]

# Observaciones del equipo (Actividad 1)
y_obs = libro.bottom + 110
n1 = note(40, y_obs, [
    "(1) GestorPrestamos tiene baja cohesión: guarda las colecciones (datos),",
    "registra préstamos (negocio) y nadie recibe la petición HTTP (presentación).",
    "Se reparte en PrestamoController, PrestamoService y los Repository.",
])
n2 = note(40, n1[1][1] + n1[1][3] + 16, [
    "(2) Las List<> en memoria no persisten: se reemplazan por",
    "EstudianteRepository, LibroRepository y PrestamoRepository (JPA + H2).",
])
n3 = note(n1[1][0] + n1[1][2] + 30, y_obs, [
    "(3) registrarPrestamo no declara qué pasa si el libro no está",
    "disponible (R1) ni si el estudiante/libro no existe (R4):",
    "faltan excepciones que se traduzcan a 409 y 404.",
])
n4 = note(n3[1][0], n3[1][1] + n3[1][3] + 16, [
    "(4) Libro–Prestamo y Estudiante–Prestamo son asociaciones, no",
    "composiciones: el libro y el estudiante existen antes y después",
    "del préstamo; borrar un préstamo no los borra.",
])
n5 = note(n3[1][0] + n3[1][2] + 30, y_obs, [
    "(5) Falta saber si un préstamo está activo",
    "(R5): se añade estaActivo() = fechaDevolucion",
    "es null. setId() público rompe el encapsulamiento:",
    "el id lo genera la base de datos.",
])
extras = [n1, n2, n3, n4, n5,
          anchor((n1[1][0] + 60, n1[1][1]), (gestor.x + 60, gestor.bottom)),
          anchor((n3[1][0] + 80, n3[1][1]), (gestor.right - 40, gestor.bottom)),
          anchor((n5[1][0] + 80, n5[1][1]), (prest.x + 40, prest.bottom))]

render("SmartLibrary - Modelo inicial anotado", [gestor, est, libro, prest], edges,
       extras=extras, path=sys.argv[1])
