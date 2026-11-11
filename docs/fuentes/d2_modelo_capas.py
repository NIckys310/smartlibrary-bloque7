"""Entregable 3: diagrama de clases por capas de SmartLibrary (estilo Visual Paradigm)."""
import sys
from vp_uml import Box, edge, m, note, package, render

GAP_ROW = 120   # separación vertical entre paquetes/capas
X0 = 70

# ---------- Presentación ----------
ctrl = Box("PrestamoController", X0, 110, stereotype="RestController", attrs=[
    "-prestamoService : PrestamoService",
], ops=[
    "+registrar(request : PrestamoRequest) : ResponseEntity<PrestamoResponse>",
    "+consultar(estudianteId : Long) : List<PrestamoResponse>",
    "+consultarPorId(id : Long) : PrestamoResponse",
])
manej = Box("ManejadorErrores", ctrl.right + 50, 110, stereotype="RestControllerAdvice", ops=[
    "+noEncontrado(ex) : ProblemDetail  [404]",
    "+noDisponible(ex) : ProblemDetail  [409]",
    "+concurrencia(ex) : ProblemDetail  [409]",
    "+datosInvalidos(ex) : ProblemDetail  [400]",
    "+jsonInvalido(ex) : ProblemDetail  [400]",
])
p_ctrl = package("controller  (Presentación)", [ctrl, manej])

# ---------- Negocio ----------
svc = Box("PrestamoService", X0, p_ctrl.bottom + GAP_ROW, stereotype="Service", attrs=[
    "-estudianteRepository : EstudianteRepository",
    "-libroRepository : LibroRepository",
    "-prestamoRepository : PrestamoRepository",
    "-clock : Clock",
], ops=[
    "+registrarPrestamo(request : PrestamoRequest) : PrestamoResponse  {transactional}",
    "+consultarPrestamos(estudianteId : Long) : List<PrestamoResponse>",
    "+consultarPrestamo(id : Long) : PrestamoResponse",
])
p_svc = package("service  (Negocio)", [svc])

# ---------- Datos ----------
y_rep = p_svc.bottom + GAP_ROW
r_est = Box("EstudianteRepository", X0, y_rep, stereotype="interface", ops=[
    "+findById(id : Long) : Optional<Estudiante>  {heredada}",
])
r_lib = Box("LibroRepository", r_est.right + 30, y_rep, stereotype="interface", ops=[
    "+findById(id : Long) : Optional<Libro>  {heredada}",
])
r_pre = Box("PrestamoRepository", r_lib.right + 30, y_rep, stereotype="interface", ops=[
    "+existsByLibroIdAndFechaDevolucionIsNull(libroId : Long) : boolean",
    "+findAllByOrderByFechaPrestamoDescIdDesc() : List<Prestamo>",
    "+findByEstudianteIdOrderBy...(estudianteId : Long) : List<Prestamo>",
    "+findById(id : Long) : Optional<Prestamo>  {heredada}",
    "+save(prestamo : Prestamo) : Prestamo  {heredada}",
])
for r in (r_est, r_lib):
    r.y = y_rep
jpa = Box("JpaRepository<T, ID>", r_pre.right + 60, y_rep, stereotype="interface", ops=[
    "+findById(id : ID) : Optional<T>",
    "+save(entity : T) : T",
    "+findAll() : List<T>",
    "+count() : long",
])
y_gen = max(r_pre.bottom, jpa.bottom) + 30
p_rep = package("repository  (Datos)", [r_est, r_lib, r_pre, jpa], extra_h=30)

# ---------- Dominio ----------
y_mod = p_rep.bottom + GAP_ROW
est = Box("Estudiante", X0, y_mod, stereotype="Entity", attrs=[
    "-id : Long", "-nombre : String", "-correo : String  {unique}",
], ops=["+getId() : Long", "+getNombre() : String", "+getCorreo() : String"])
pre = Box("Prestamo", est.right + 150, y_mod, stereotype="Entity", attrs=[
    "-id : Long",
    "-fechaPrestamo : LocalDate",
    "-fechaDevolucion : LocalDate [0..1]",
    "-estudiante : Estudiante",
    "-libro : Libro",
], ops=[
    "+Prestamo(estudiante, libro, fechaPrestamo)",
    "+estaActivo() : boolean",
    "+getEstudiante() : Estudiante",
    "+getLibro() : Libro",
])
lib = Box("Libro", pre.right + 150, y_mod, stereotype="Entity", attrs=[
    "-id : Long", "-titulo : String", "-disponible : boolean = true", "-version : Long  {optimista}",
], ops=["+marcarPrestado() : void", "+marcarDevuelto() : void", "+isDisponible() : boolean",
        "+getTitulo() : String"])
p_mod = package("model  (Dominio)", [est, pre, lib])

# ---------- Columna derecha: dto y exception ----------
x_der = max(p_ctrl.right, p_svc.right, p_rep.right, p_mod.right) + 110
req = Box("PrestamoRequest", x_der, ctrl.y, stereotype="record", attrs=[
    "+estudianteId : Long  {NotNull, Positive}",
    "+libroId : Long  {NotNull, Positive}",
])
res = Box("PrestamoResponse", x_der, req.bottom + 30, stereotype="record", attrs=[
    "+id : Long", "+estudianteId : Long", "+estudianteNombre : String", "+libroId : Long",
    "+libroTitulo : String", "+fechaPrestamo : LocalDate", "+fechaDevolucion : LocalDate",
    "+activo : boolean",
], ops=[m("+desde(prestamo : Prestamo) : PrestamoResponse", static=True)])
res.w = req.w = max(res.w, req.w)
p_dto = package("dto", [req, res])

rte = Box("RuntimeException", x_der, p_rep.y + 30, stereotype="built-in", min_w=170)
e404 = Box("RecursoNoEncontradoException", x_der, rte.bottom + 70, ops=["+RecursoNoEncontradoException(recurso, id)"])
e409 = Box("LibroNoDisponibleException", e404.right + 30, e404.y, ops=["+LibroNoDisponibleException(libroId)"])
rte.x = (e404.x + e409.right) / 2 - rte.w / 2
p_exc = package("exception", [rte, e404, e409])


def L(x, y, t, a="start"):
    return (x, y, t, a)


edges = []
# Controller → Service (asociación dirigida: referencia inyectada)
xa = ctrl.x + 230
edges.append(edge([(xa, ctrl.bottom), (xa, svc.y)], "association",
                  labels=[L(xa + 6, p_svc.y - 28, "-prestamoService"), L(xa + 6, svc.y - 8, "1")]))
# Service → Repositories (asociaciones dirigidas)
y_bus = p_svc.bottom + GAP_ROW / 2
for r, nombre in ((r_est, "-estudianteRepository"), (r_lib, "-libroRepository"), (r_pre, "-prestamoRepository")):
    edges.append(edge([(svc.cx, svc.bottom), (svc.cx, y_bus), (r.cx, y_bus), (r.cx, r.y)], "association",
                      labels=[L(r.cx + 6, p_rep.y - 28, nombre), L(r.cx + 6, r.y - 8, "1")]))
# Repositories → JpaRepository (generalización entre interfaces)
for r, bind in ((r_est, "<Estudiante, Long>"), (r_lib, "<Libro, Long>"), (r_pre, "<Prestamo, Long>")):
    edges.append(edge([(r.cx, r.bottom), (r.cx, y_gen), (jpa.cx, y_gen), (jpa.cx, jpa.bottom)], "generalization"))
    edges.append(edge([(r.cx, r.bottom), (r.cx, r.bottom)], "link", labels=[L(r.cx + 6, r.bottom + 16, "«bind» " + bind)]))
# Prestamo → Estudiante / Libro (asociaciones del dominio, navegables desde Prestamo)
ya = pre.y + 70
edges.append(edge([(pre.x, ya), (est.right, ya)], "association",
                  labels=[L(pre.x - 6, ya - 6, "0..*", "end"), L(est.right + 6, ya - 6, "1"),
                          L(est.right + 6, ya + 14, "-estudiante")]))
edges.append(edge([(pre.right, ya), (lib.x, ya)], "association",
                  labels=[L(pre.right + 6, ya - 6, "0..*"), L(lib.x - 6, ya - 6, "1", "end"),
                          L(lib.x - 6, ya + 14, "-libro", "end")]))
# Dependencias entre paquetes
edges.append(edge([(p_ctrl.right, ctrl.y + 40), (p_dto.x, ctrl.y + 40)], "dependency",
                  labels=[L((p_ctrl.right + p_dto.x) / 2, ctrl.y + 34, "«use»", "middle")]))
y_sd = max(svc.y + 30, p_dto.bottom + 30)
edges.append(edge([(p_svc.right, y_sd), (p_dto.cx, y_sd), (p_dto.cx, p_dto.bottom)], "dependency",
                  labels=[L(p_svc.right + 10, y_sd - 6, "«use»")]))
y_se = svc.bottom - 10
edges.append(edge([(p_svc.right, y_se), (p_exc.cx, y_se), (p_exc.cx, p_exc.y - 20)], "dependency",
                  labels=[L(p_svc.right + 10, y_se - 6, "«throw»")]))
x_far = max(p_dto.right, p_exc.right) + 40
y_top = 18
edges.append(edge([(manej.cx, manej.y), (manej.cx, y_top), (x_far, y_top), (x_far, p_exc.cy), (p_exc.right, p_exc.cy)],
                  "dependency", labels=[L(x_far - 6, p_exc.cy - 6, "«handle»", "end")]))
x_l = 30
edges.append(edge([(p_svc.x, svc.cy), (x_l, svc.cy), (x_l, p_mod.cy), (p_mod.x, p_mod.cy)], "dependency",
                  labels=[L(x_l + 4, (svc.cy + p_mod.cy) / 2, "«use»")]))
edges.append(edge([(r_est.cx - 60, p_rep.bottom), (r_est.cx - 60, p_mod.y - 20)], "dependency",
                  labels=[L(r_est.cx - 54, (p_rep.bottom + p_mod.y) / 2, "«use»")]))
y_me = lib.y + 40
edges.append(edge([(p_mod.right, y_me), (e409.cx, y_me), (e409.cx, p_exc.bottom)], "dependency",
                  labels=[L(p_mod.right + 10, y_me - 6, "«throw»")]))
# Generalización de excepciones
y_eb = rte.bottom + 35
for e in (e404, e409):
    edges.append(edge([(e.cx, e.y), (e.cx, y_eb), (rte.cx, y_eb), (rte.cx, rte.bottom)], "generalization"))

frames = [p_ctrl, p_svc, p_rep, p_mod, p_dto, p_exc]
n1 = note(p_exc.x, p_mod.bottom + 40, [
    "Asociación (→): referencia que se conserva como atributo",
    "(inyección por constructor o @ManyToOne).",
    "Dependencia (- - >): uso puntual (parámetro, retorno, throw).",
    "Dirección de capas: Controller → Service → Repository.",
    "Controller nunca llama a un Repository.",
])
n2 = note(X0, p_mod.bottom + 40, [
    "Los Repository son interfaces: Spring Data genera la implementación",
    "en tiempo de ejecución, por eso no se dibuja ninguna realización propia.",
    "findById() y save() se heredan de JpaRepository.",
])
render("SmartLibrary - Modelo por capas", [ctrl, manej, svc, r_est, r_lib, r_pre, jpa, est, pre, lib,
                                            req, res, rte, e404, e409],
       edges, extras=[n1, n2], frames=frames, path=sys.argv[1])
