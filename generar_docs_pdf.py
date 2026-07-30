from io import BytesIO
from xhtml2pdf import pisa

html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  @page { size: A4; margin: 2cm; }
  body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #333; line-height: 1.5; }
  h1 { color: #1a73e8; font-size: 22pt; border-bottom: 3px solid #1a73e8; padding-bottom: 8px; margin-top: 0; }
  h2 { color: #0d47a1; font-size: 16pt; margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
  h3 { color: #1565c0; font-size: 13pt; margin-top: 20px; }
  .subtitle { color: #666; font-size: 12pt; margin-top: -10px; margin-bottom: 30px; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 10pt; }
  th { background: #1a73e8; color: white; padding: 8px 10px; text-align: left; }
  td { padding: 6px 10px; border-bottom: 1px solid #ddd; }
  tr:nth-child(even) td { background: #f5f8ff; }
  code { background: #eef; padding: 1px 5px; border-radius: 3px; font-size: 9pt; font-family: monospace; }
  pre { background: #f4f4f4; border-left: 3px solid #1a73e8; padding: 10px 14px; font-size: 8.5pt; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-family: monospace; line-height: 1.4; }
  .file-ref { background: #e8f0fe; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 9pt; }
  ul { margin: 6px 0; padding-left: 22px; }
  li { margin: 3px 0; }
  .summary-box { background: #e8f5e9; border: 1px solid #a5d6a7; padding: 12px 16px; border-radius: 6px; margin: 15px 0; }
  .page-break { page-break-before: always; }
  .footer { text-align: center; color: #999; font-size: 8pt; margin-top: 40px; border-top: 1px solid #ddd; padding-top: 10px; }
</style>
</head>
<body>

<h1>Documentación Técnica de Librerías JavaScript</h1>
<p class="subtitle">Sistema de Recursos Humanos — Gestor de Turnos y Vacaciones</p>
<p>Documento generado el <strong>28/07/2026</strong></p>

<h2>Índice</h2>
<ol>
  <li><a href="#fc">FullCalendar (v6.1.9)</a></li>
  <li><a href="#jqui">jQuery UI (v1.13.2)</a></li>
  <li><a href="#hk">Hotkeys-js (v3.13.7)</a></li>
  <li><a href="#drv">Driver.js (v1.3.1)</a></li>
</ol>

<!-- ============================================================ -->
<div class="page-break"></div>
<h2 id="fc">1. FullCalendar (v6.1.9)</h2>

<h3>1.1 Importación</h3>
<table>
  <tr><th>Archivo</th><th>Línea</th><th>Detalle</th></tr>
  <tr>
    <td><span class="file-ref">PlantillaGeneral.html</span></td>
    <td>163</td>
    <td><code>&lt;script src="...fullcalendar@6.1.9/index.global.min.js"&gt;</code></td>
  </tr>
</table>
<p>Se carga vía CDN (jsDelivr) en la plantilla base. Está disponible en toda página que extienda <code>PlantillaGeneral.html</code>.</p>

<h3>1.2 Inicialización y Configuración</h3>
<table>
  <tr><th>Archivo</th><th>Líneas</th><th>Detalle</th></tr>
  <tr>
    <td><span class="file-ref">calendario.html</span></td>
    <td>34-77</td>
    <td>Inicialización con opciones: <code>locale: 'es'</code>, <code>initialView: 'dayGridMonth'</code>, toolbar con vistas month/week/day/list, eventos vía AJAX, <code>eventClick</code> con SweetAlert, <code>height: 'auto'</code>.</td>
  </tr>
</table>

<h3>1.3 Opciones de FullCalendar</h3>
<table>
  <tr><th>Opción</th><th>Valor</th><th>Descripción</th></tr>
  <tr><td><code>locale</code></td><td><code>'es'</code></td><td>Idioma español</td></tr>
  <tr><td><code>initialView</code></td><td><code>'dayGridMonth'</code></td><td>Vista mensual por defecto</td></tr>
  <tr><td><code>headerToolbar.left</code></td><td><code>'prev,next today'</code></td><td>Botones de navegación</td></tr>
  <tr><td><code>headerToolbar.center</code></td><td><code>'title'</code></td><td>Título del calendario</td></tr>
  <tr><td><code>headerToolbar.right</code></td><td><code>'dayGridMonth,timeGridWeek,timeGridDay,listWeek'</code></td><td>Selectores de vista</td></tr>
  <tr><td><code>events</code></td><td>Función asíncrona</td><td>Obtiene eventos desde la API <span class="file-ref">Vacaciones:api_calendar_events</span></td></tr>
  <tr><td><code>eventClick</code></td><td>Callback</td><td>Muestra detalles del evento con SweetAlert2</td></tr>
  <tr><td><code>height</code></td><td><code>'auto'</code></td><td>Ajusta altura automáticamente</td></tr>
</table>

<h3>1.4 API de Datos — <span class="file-ref">views.py:1044-1071</span></h3>
<p>Endpoint: <code>Vacaciones:api_calendar_events</code> — Devuelve JSON con todos los turnos y permisos.</p>

<p><strong>Turnos (líneas 1047-1057):</strong></p>
<pre>{
  id: "turno-{id}",
  title: "{empleado} - {turno}",
  start: "YYYY-MM-DD", end: "YYYY-MM-DD",
  color: "#28a745" | "#ffc107" | "#6f42c1",
  type: "turno"
}</pre>

<p><strong>Permisos (líneas 1059-1069):</strong></p>
<pre>{
  id: "permiso-{id}",
  title: "{empleado} - {tipo}",
  start: "YYYY-MM-DD", end: "YYYY-MM-DD",
  color: "#28a745" | "#ffc107" | "#dc3545" | "#6c757d",
  type: "permiso"
}</pre>

<h3>1.5 Vistas del Calendario</h3>
<ul>
  <li><code>dayGridMonth</code> — Mes en cuadrícula</li>
  <li><code>timeGridWeek</code> — Semana con franjas horarias</li>
  <li><code>timeGridDay</code> — Día con franjas horarias</li>
  <li><code>listWeek</code> — Lista semanal</li>
</ul>

<h3>1.6 Leyenda de Colores</h3>
<table>
  <tr><th>Color</th><th>Turno</th><th>Permiso</th></tr>
  <tr><td style="background:#28a745; color:white;"> Verde</td><td>Mañana</td><td>Aprobado</td></tr>
  <tr><td style="background:#ffc107;"> Amarillo</td><td>Tarde</td><td>Pendiente</td></tr>
  <tr><td style="background:#6f42c1; color:white;"> Púrpura</td><td>Noche</td><td>—</td></tr>
  <tr><td style="background:#dc3545; color:white;"> Rojo</td><td>—</td><td>Rechazado</td></tr>
  <tr><td style="background:#6c757d; color:white;"> Gris</td><td>—</td><td>Cancelado</td></tr>
</table>

<h3>1.7 Vista del Calendario</h3>
<table>
  <tr><th>Archivo</th><th>Línea</th><th>Función</th></tr>
  <tr><td><span class="file-ref">views.py</span></td><td>906-908</td><td><code>def calendario(request)</code> — renderiza <span class="file-ref">calendario.html</span></td></tr>
  <tr><td><span class="file-ref">Vacios/urls.py</span></td><td>35</td><td><code>path('calendario/', views.calendario, name='calendario')</code></td></tr>
  <tr><td><span class="file-ref">Vacios/urls.py</span></td><td>40</td><td><code>path('api/calendar-events/', views.api_calendar_events)</code></td></tr>
</table>

<div class="summary-box">
<strong>Resumen:</strong> FullCalendar muestra en una interfaz visual todos los turnos y solicitudes de permiso. Los datos se obtienen desde <code>api_calendar_events</code> que consulta las tablas <code>TurnoGuardia</code> y <code>SolicitudPermiso</code>. Al hacer clic en un evento se abre un SweetAlert con los detalles.
</div>


<!-- ============================================================ -->
<div class="page-break"></div>
<h2 id="jqui">2. jQuery UI (v1.13.2)</h2>

<h3>2.1 Importación</h3>
<table>
  <tr><th>Archivo</th><th>Línea</th><th>Detalle</th></tr>
  <tr>
    <td><span class="file-ref">PlantillaGeneral.html</span></td>
    <td>139</td>
    <td><code>&lt;script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"&gt;</code></td>
  </tr>
  <tr>
    <td><span class="file-ref">PlantillaGeneral.html</span></td>
    <td>140</td>
    <td><code>&lt;script src="...jqueryui-touch-punch/0.2.3/jquery.ui.touch-punch.min.js"&gt;</code> — soporte táctil</td>
  </tr>
  <tr>
    <td><span class="file-ref">turnos.html</span></td>
    <td>166</td>
    <td>Importación redundante (ya cargado desde la base)</td>
  </tr>
</table>

<h3>2.2 Funcionalidad Implementada</h3>
<p>jQuery UI se usa exclusivamente para la función de <strong>arrastrar y soltar (drag & drop)</strong> de turnos en la tabla de <span class="file-ref">turnos.html</span>.</p>

<h3>2.3 Draggable — <span class="file-ref">turnos.html:403-432</span></h3>
<pre>$('#tbodyTurnos tr').draggable({
    handle: '.drag-handle',       // Solo arrastrar desde el icono de agarre
    helper: function() { ... },   // Clon estilizado como feedback visual
    cursor: 'grabbing',
    cursorAt: { top: 20, left: 20 },
    zIndex: 9999,
    revert: 'invalid',            // Vuelve si no se suelta en zona válida
    opacity: 0.9,
    start: function() { $(this).css('opacity', '0.5'); },
    stop:  function() { $(this).css('opacity', '1'); }
});</pre>

<h3>2.4 Droppable — <span class="file-ref">turnos.html:435-471</span></h3>
<pre>$('#tbodyTurnos tr').droppable({
    accept: '#tbodyTurnos tr',    // Solo acepta filas de la misma tabla
    hoverClass: 'bg-primary ...',
    tolerance: 'pointer',
    drop: function(event, ui) {
        // Obtiene sourceId y targetId
        // Muestra SweetAlert de confirmación
        // Si confirma, llama a intercambiarTurnos(id1, id2)
    }
});</pre>

<h3>2.5 Intercambio de Turnos — <span class="file-ref">turnos.html:474-507</span></h3>
<pre>function intercambiarTurnos(id1, id2) {
    $.ajax({
        url: "{% url 'Vacaciones:turno_intercambiar' %}",
        type: 'POST',
        data: { turno_id_1: id1, turno_id_2: id2, motivo: 'Intercambio...' },
        success: function() { ... location.reload(); },
        error: function() { ... }
    });
}</pre>

<h3>2.6 Flujo completo</h3>
<ol>
  <li>El usuario arrastra una fila por el icono <code>grip-vertical</code></li>
  <li>Un clon semitransparente sigue al cursor</li>
  <li>Al soltar sobre otra fila, se muestra confirmación con SweetAlert2</li>
  <li>Si acepta, se envía POST a <code>turno_intercambiar</code> con ambos IDs</li>
  <li>La vista intercambia los empleados de ambos turnos y crea un registro de <code>Sustitucion</code></li>
  <li>La página se recarga para reflejar los cambios</li>
</ol>

<h3>2.7 Soporte Táctil</h3>
<p>Touch Punch (línea 140) traduce eventos táctiles a mouse events, permitiendo drag & drop en dispositivos móviles y tablets.</p>

<h3>2.8 Reinicialización en DataTables</h3>
<p>En <span class="file-ref">turnos.html:190-192</span>, el <code>drawCallback</code> de DataTable llama a <code>setupDragAndDropSwap()</code> tras cada paginación/búsqueda, que destruye y recrea las instancias de draggable/droppable (líneas 395-400).</p>

<div class="summary-box">
<strong>Resumen:</strong> jQuery UI se usa únicamente para el drag & drop visual de turnos. Permite intercambiar la asignación de un turno entre dos empleados arrastrando filas. Touch Punch añade soporte para pantallas táctiles.
</div>


<!-- ============================================================ -->
<div class="page-break"></div>
<h2 id="hk">3. Hotkeys-js (v3.13.7)</h2>

<h3>3.1 Importación</h3>
<table>
  <tr><th>Archivo</th><th>Línea</th><th>Detalle</th></tr>
  <tr>
    <td><span class="file-ref">PlantillaGeneral.html</span></td>
    <td>164</td>
    <td><code>&lt;script src="...hotkeys-js@3.13.7/dist/hotkeys.min.js"&gt;</code></td>
  </tr>
</table>
<p>Se carga vía CDN en la plantilla base, disponible en todas las páginas.</p>

<h3>3.2 Atajo de Teclado Definido</h3>
<table>
  <tr><th>Archivo</th><th>Línea</th><th>Atajo</th><th>Función</th></tr>
  <tr>
    <td><span class="file-ref">permisos.html</span></td>
    <td>541-544</td>
    <td><code>ctrl+shift+a</code></td>
    <td><code>aprobarMasivo()</code></td>
  </tr>
</table>

<h3>3.3 Código de Implementación — <span class="file-ref">permisos.html:541-544</span></h3>
<pre>hotkeys('ctrl+shift+a', function (event, handler) {
    event.preventDefault();
    aprobarMasivo();
});</pre>

<h3>3.4 Función <code>aprobarMasivo()</code> — <span class="file-ref">permisos.html:487-534</span></h3>
<ol>
  <li>Recolecta los checkboxes seleccionados (<code>.permiso-checkbox:checked</code>)</li>
  <li>Si no hay ninguno manual, toma todos los pendientes de la página</li>
  <li>Llama a <code>confirmAprobarMasivo(elements)</code></li>
  <li>Muestra SweetAlert de confirmación: "¿Aprobar N permisos?"</li>
  <li>Envía POST con JSON <code>{ ids: [...] }</code> al endpoint <code>Vacaciones:permiso_aprobar_masivo</code></li>
  <li>En éxito: recarga la página; en error: muestra alerta</li>
</ol>

<h3>3.5 Vista de Aprobación Masiva — <span class="file-ref">views.py:484-526</span></h3>
<pre>@csrf_exempt
def permiso_aprobar_masivo(request):
    ids = data.get('ids', [])
    for permiso_id in ids:
        permiso = SolicitudPermiso.objects.get(id=permiso_id)
        if permiso.estado == 'pendiente':
            permiso.estado = 'aprobado'
            permiso.save()
            if permiso.tipo == 'vacaciones':
                emp.dias_vacaciones_pendientes -= permiso.dias_solicitados
                emp.save()
    return JsonResponse({'message': f'{aprobados} permiso(s) aprobado(s)'})</pre>

<h3>3.6 Indicador Visual — <span class="file-ref">permisos.html:97</span></h3>
<pre>&lt;small&gt;Atajo: &lt;strong&gt;Ctrl+Shift+A&lt;/strong&gt; para aprobar todos los pendientes.&lt;/small&gt;</pre>
<p>Se muestra en el footer de la tarjeta de permisos para informar al usuario.</p>

<div class="summary-box">
<strong>Resumen:</strong> Hotkeys-js registra un solo atajo <code>Ctrl+Shift+A</code> en la página de permisos. Activa la función de aprobación masiva, que cambia el estado de múltiples solicitudes pendientes a "aprobado" y descuenta los días de vacaciones correspondientes.
</div>


<!-- ============================================================ -->
<div class="page-break"></div>
<h2 id="drv">4. Driver.js (v1.3.1)</h2>

<h3>4.1 Importación</h3>
<table>
  <tr><th>Tipo</th><th>Archivo</th><th>Línea</th><th>Detalle</th></tr>
  <tr>
    <td>CSS</td>
    <td><span class="file-ref">PlantillaGeneral.html</span></td>
    <td>28</td>
    <td><code>&lt;link rel="stylesheet" href="...driver.js@1.3.1/dist/driver.css"&gt;</code></td>
  </tr>
  <tr>
    <td>JS</td>
    <td><span class="file-ref">PlantillaGeneral.html</span></td>
    <td>165</td>
    <td><code>&lt;script src="...driver.js@1.3.1/dist/driver.js.iife.js"&gt;</code></td>
  </tr>
</table>
<p>Se carga vía CDN (jsDelivr) en la plantilla base. El objeto global expuesto es <code>window.driver.js.driver</code>.</p>

<h3>4.2 Tutorial del Dashboard — <span class="file-ref">dashboard.html</span></h3>
<p><strong>Disparo (líneas 133-154):</strong></p>
<pre>const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('tutorial') === '1') {
    Swal.fire({ title: '¿Deseas iniciar un tutorial de la página?' })
        .then((result) => {
            if (result.isConfirmed) { setTimeout(iniciarTutorial, 300); }
        });
}</pre>

<p><strong>Función <code>iniciarTutorial()</code> (líneas 157-244):</strong></p>
<pre>const driver = window.driver?.js?.driver;
const driverObj = driver({
    showProgress: true, animate: true,
    steps: [ /* 8 pasos */ ]
});
driverObj.drive();</pre>

<h3>4.3 Pasos del Tour (Dashboard)</h3>
<table>
  <tr><th>#</th><th>Elemento</th><th>Título</th><th>Descripción</th></tr>
  <tr><td>1</td><td><code>#nav-dashboard</code></td><td>📊 Dashboard</td><td>Panel principal con resumen general y gráficos</td></tr>
  <tr><td>2</td><td><code>#nav-empleados</code></td><td>👥 Empleados</td><td>Lista, edición, QR y creación de empleados</td></tr>
  <tr><td>3</td><td><code>#nav-departamentos</code></td><td>🏢 Departamentos</td><td>Gestión de departamentos y organización</td></tr>
  <tr><td>4</td><td><code>#nav-permisos</code></td><td>📋 Permisos / Vacaciones</td><td>Solicitudes, aprobación/rechazo y masiva</td></tr>
  <tr><td>5</td><td><code>#nav-turnos</code></td><td>🕐 Turnos de Guardia</td><td>Asignación e intercambio drag & drop</td></tr>
  <tr><td>6</td><td><code>#nav-sustituciones</code></td><td>🔄 Sustituciones</td><td>Sustitución de turnos entre empleados</td></tr>
  <tr><td>7</td><td><code>#nav-calendario</code></td><td>📅 Calendario</td><td>Vista interactiva de turnos y permisos</td></tr>
  <tr><td>8</td><td><code>#nav-reportes</code></td><td>📄 Reportes</td><td>Exportación PDF y envío por correo</td></tr>
</table>

<h3>4.4 IDs de Navegación — <span class="file-ref">PlantillaGeneral.html:80-87</span></h3>
<pre>&lt;li id="nav-dashboard"&gt;...&lt;/li&gt;
&lt;li id="nav-empleados"&gt;...&lt;/li&gt;
&lt;li id="nav-departamentos"&gt;...&lt;/li&gt;
&lt;li id="nav-permisos"&gt;...&lt;/li&gt;
&lt;li id="nav-turnos"&gt;...&lt;/li&gt;
&lt;li id="nav-sustituciones"&gt;...&lt;/li&gt;
&lt;li id="nav-calendario"&gt;...&lt;/li&gt;
&lt;li id="nav-reportes"&gt;...&lt;/li&gt;</pre>

<h3>4.5 Tutorial del Calendario — <span class="file-ref">calendario.html:79-109</span></h3>
<table>
  <tr><th>#</th><th>Elemento</th><th>Título</th><th>Descripción</th></tr>
  <tr><td>1</td><td><code>#calendar</code></td><td>Calendario</td><td>Visualización de turnos y permisos</td></tr>
  <tr><td>2</td><td><code>#calendar-legend</code></td><td>Leyenda</td><td>Identificación por colores</td></tr>
</table>

<h3>4.6 Activación del Tutorial</h3>
<table>
  <tr><th>Mecanismo</th><th>Archivo</th><th>Línea</th><th>Detalle</th></tr>
  <tr>
    <td>Login</td>
    <td><span class="file-ref">login.html</span></td>
    <td>118</td>
    <td><code>&lt;input type="hidden" name="next" value="...?tutorial=1"&gt;</code></td>
  </tr>
  <tr>
    <td>Registro</td>
    <td><span class="file-ref">views.py</span></td>
    <td>60</td>
    <td><code>redirect: '/dashboard/?tutorial=1'</code></td>
  </tr>
  <tr>
    <td>Dashboard</td>
    <td><span class="file-ref">dashboard.html</span></td>
    <td>134-154</td>
    <td>Detecta <code>?tutorial=1</code> y pregunta al usuario</td>
  </tr>
</table>

<div class="summary-box">
<strong>Resumen:</strong> Driver.js implementa un tour interactivo que guía al usuario por las 8 secciones del sistema. Se activa automáticamente tras el registro o inicio de sesión. El tour resalta cada ítem del menú de navegación y muestra una descripción de lo que se puede hacer en cada página.
</div>

<div class="footer">
Sistema de Recursos Humanos — Documentación generada automáticamente — 28/07/2026
</div>

</body>
</html>
"""

def generar_pdf(html_content, filename):
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_content.encode('UTF-8')), result, encoding='UTF-8')
    if pdf.err:
        print(f"Error generando PDF: {pdf.err}")
        return False
    with open(filename, 'wb') as f:
        f.write(result.getvalue())
    print(f"PDF generado: {filename}")
    return True

generar_pdf(html, '/home/estebanochoa/django/RecursosHumanos/documentacion_librerias.pdf')
