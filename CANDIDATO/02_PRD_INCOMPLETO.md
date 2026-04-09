# PRD — Sistema Inteligente de Tickets
## NovaTech Solutions

**Versión:** 1.0
**Autor:** [NOMBRE DEL CANDIDATO]
**Fecha:** 6 de abril de 2026
**Estado:** Definido — MVP en construcción

---

## 1. Resumen Ejecutivo

NovaTech Solutions (200 empleados, oficinas en Monterrey y Guadalajara) necesita un sistema de gestión de tickets de soporte interno que utilice inteligencia artificial para clasificar, priorizar y resolver automáticamente solicitudes comunes de TI.

**Objetivo principal:** Reducir la carga operativa del equipo de TI automatizando la resolución de tickets repetitivos, mientras se asegura que los casos críticos o sensibles reciban atención humana inmediata.

**Meta cuantificable:** Alcanzar un 30-50% de resolución automática sin intervención humana en los primeros 3 meses.

---

## 2. Problema

### Situación Actual
El equipo de TI (4 personas) recibe entre **50-80 tickets semanales** vía correo electrónico a `soporte@novatech.com`, sin ningún sistema de gestión formal. Marcos Solís, líder del equipo con 8 años de experiencia, funciona como **single point of failure**: recibe todos los correos, prioriza mentalmente y responde manualmente.

### Flujo actual
1. Empleado envía email a soporte@novatech.com
2. Marcos lee el correo y decide prioridad mentalmente
3. Marcos resuelve o delega (sin tracking)
4. Intenta registrar en un Google Sheet "cuando se acuerda"
5. No hay SLAs, métricas, ni historial de conversaciones

### Problemas específicos
- **Sin priorización:** Tickets críticos (servidor caído) quedan enterrados entre resets de contraseña
- **Trabajo repetitivo:** ~40-50% de tickets son resolubles con instructivos (contraseñas, VPN, software conocido)
- **Single point of failure:** Cuando Marcos está de vacaciones, Ana García toma el control pero no tiene acceso completo ni conoce todas las soluciones. Los tickets se acumulan
- **Sin métricas:** Marcos dice que resuelve en 4 horas promedio; los usuarios reportan más de 1 día. No hay forma de medir
- **Picos de demanda:** Los lunes llegan 25-30 tickets. Tras actualizaciones de software, se triplica a ~150/semana
- **Oficina Guadalajara desatendida:** Ventas y administración se quejan de tiempos de respuesta lentos
- **Intento fallido previo:** Freshdesk se implementó hace 2 años y se canceló a los 3 meses porque requería que la gente entrara a otra plataforma y Marcos lo consideró "doble trabajo"

### Impacto cuantificable
- ~30 horas/semana de Marcos en tickets repetitivos que podrían automatizarse
- Riesgo operativo: si Marcos se va, no hay base de conocimiento accesible (aunque tiene una wiki personal en Notion con ~200 artículos que nadie más conoce)
- Tickets críticos con tiempo de respuesta impredecible

---

## 3. Usuarios y Roles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| Empleado (solicitante) | 200 empleados en Monterrey y Guadalajara. Envían tickets vía email. No técnicos en su mayoría. | Enviar tickets, ver estado de sus tickets, recibir respuestas |
| Agente de TI (Marcos y equipo) | Marcos Solís (líder, 8 años), Ana García (2 años), Luis Ramírez (1 año), Sofía Torres (6 meses, medio tiempo) | Ver todos los tickets, resolver, escalar, asignar, acceder a base de conocimiento |
| Recursos Humanos | 10 personas. Reciben tickets sensibles (acoso, discapacidad) | Ver SOLO tickets marcados como sensibles/RRHH. Acceso exclusivo y confidencial |
| Gerente de Operaciones (Ricardo) | Supervisa el sistema, revisa métricas | Dashboard de métricas, configuración del sistema, reportes |
| Directora General (Patricia Vega) | Quiere reportes mensuales para toma de decisiones | Reportes/dashboard ejecutivo de solo lectura |
| Jefes de departamento | Aprueban solicitudes de permisos y software no estándar | Aprobar/rechazar tickets que requieren autorización |

---

## 4. Canales de Entrada

| Canal | Prioridad | Justificación |
|-------|-----------|---------------|
| **Email** (soporte@novatech.com) | Principal | Es como trabaja la gente hoy. Lección de Freshdesk: la herramienta debe adaptarse al usuario, no al revés. El 100% de empleados ya usa Gmail. |
| **Slack** | Secundario (futuro) | Solo ~80 personas lo usan activamente (desarrollo, QA, diseño). Ventas y admin no lo abren. Se puede integrar en Fase 2 para los equipos que sí lo usan. |
| **Formulario web** | No para MVP | Requiere cambio de comportamiento. Podría ser útil en Fase 2 para tickets que necesitan información estructurada. |

**Decisión:** El MVP recibe tickets SOLO por email para maximizar adopción y minimizar fricción. El sistema procesa los correos por detrás — el usuario no necesita cambiar nada de su flujo actual.

---

## 5. Taxonomía de Tickets

### 5.1 Categorías

| Categoría | % Aproximado | Automatizable |
|-----------|-------------|---------------|
| 🔑 Reset de contraseñas | 25% | ✅ Sí — instructivo paso a paso |
| 🌐 VPN / Conectividad | 20% | ✅ Parcial — troubleshooting guiado |
| 💻 Instalación/Problemas de software | 15% | ✅ Parcial — si está en lista aprobada |
| 🔐 Permisos de acceso (carpetas/sistemas) | 15% | ⚠️ Requiere aprobación de jefe directo |
| 🖱️ Hardware (mouse, teclado, monitor) | 10% | ❌ Requiere intervención física |
| 🖨️ Impresoras | 5% | ✅ Parcial — troubleshooting básico |
| 🖥️ Servidor/Infraestructura | 5% | ❌ Siempre escalamiento humano |
| 🚨 Temas sensibles (RRHH) | 2-3% | ❌ NUNCA — routing directo a RRHH |
| 📦 Otros/Misceláneos | ~3% | ⚠️ Caso por caso |

**Criterio:** Basado en datos reales proporcionados por Ricardo y el historial informal de Marcos. La wiki de Marcos (~200 artículos en Notion) servirá como base de conocimiento para las respuestas automatizadas.

### 5.2 Niveles de Prioridad

| Prioridad | Criterio | Tiempo de Respuesta | Ejemplo |
|-----------|----------|---------------------|---------|
| 🔴 Crítica | Servidor caído, brecha de seguridad, sistema de producción inoperable | 15 minutos | "Se cayó el servidor de producción" |
| 🟠 Alta | Empleado no puede trabajar, bloqueo total | 1 hora | "No puedo acceder a ningún sistema" |
| 🟡 Media | Puede trabajar parcialmente, funcionalidad degradada | 4 horas | "La VPN se desconecta cada 30 min" |
| 🟢 Baja | Solicitudes, preguntas, mejoras | 24 horas | "¿Cómo reseteo mi contraseña?" |

---

## 6. Flujo del Sistema

### 6.1 Flujo Principal

```
Email a soporte@novatech.com
        ↓
[1] Recepción automática del ticket
        ↓
[2] Detección de contenido sensible (RRHH)
    → SI es sensible → Routing directo a RRHH (ver 6.3)
    → NO es sensible ↓
        ↓
[3] Clasificación por IA (categoría + prioridad)
        ↓
[4] ¿Es automatizable?
    → SI → Generar respuesta automática de la base de conocimiento
           → Enviar al usuario con nota: "Si no resuelve, responde a este correo y un humano te atenderá"
    → NO → Escalar a agente humano (ver 6.2)
        ↓
[5] Registro en base de datos (tracking completo)
        ↓
[6] Métricas y reportes automáticos
```

### 6.2 Flujo de Escalamiento

1. La IA no puede resolver → Ticket se asigna al agente disponible según especialidad
2. Si requiere aprobación (permisos, software no aprobado) → Notifica al jefe directo para autorización
3. Si es prioridad 🔴 Crítica → Notificación inmediata a Marcos + Ricardo por email/Slack
4. Si el usuario responde "no funcionó" → Se reabre el ticket y escala a humano automáticamente
5. Si Marcos no está disponible → Ana García recibe el ticket con contexto completo + acceso a la wiki

**Flujo de aprobaciones:**
- **Reset de contraseña:** Sin aprobación, solo verificación de identidad
- **Permisos de acceso:** Requiere aprobación del jefe directo (email automático al jefe)
- **Software en lista aprobada** (Chrome, Slack, Zoom, VS Code, Postman, Figma, Office 365, Notion, Docker): Sin aprobación
- **Software NO en lista:** Requiere aprobación de Patricia Vega

### 6.3 Flujo de Tickets Sensibles

1. La IA detecta keywords/patrones de contenido sensible (acoso, discriminación, discapacidad, denuncia, etc.)
2. **El ticket NO se procesa por IA** — sin clasificación, sin lectura de contenido
3. Se rutea directamente al departamento de RRHH con acceso exclusivo
4. Ni Ricardo, ni Marcos, ni ningún agente de TI puede ver estos tickets
5. Se registra solo metadata (fecha, remitente, estado) sin contenido

**Contexto:** El año pasado hubo un caso de acoso que se filtró y causó problemas legales. RRHH exige confidencialidad total. Cumplimiento con Ley Federal de Protección de Datos Personales (México).

---

## 7. Capacidades de IA

### 7.1 Clasificación Automática

- **Modelo:** LLM (Claude/GPT) con prompt engineering para clasificar en las categorías definidas
- **Input:** Asunto + cuerpo del email
- **Output:** Categoría, prioridad, confianza del modelo
- **Si confianza < 70%:** Escalar a humano para revisión
- **Contextualización:** Se le provee la taxonomía de tickets y ejemplos de cada categoría

### 7.2 Resolución Automática

- **Tipos que resuelve la IA sola:** Reset de contraseñas, VPN básica, software aprobado, problemas de impresora comunes
- **Base de conocimiento:** Wiki de Marcos en Notion (~200 artículos), exportada a Markdown y usada como contexto (técnica RAG)
- **Generación de respuestas:** La IA busca en la base de conocimiento el artículo más relevante y genera una respuesta personalizada en español
- **Safeguard:** Cada respuesta incluye: "Si esta solución no funciona, responde a este correo y un agente humano te atenderá"

### 7.3 Detección de Contenido Sensible

- **Método:** Análisis de keywords y patrones semánticos (acoso, hostigamiento, discriminación, denuncia, discapacidad, adaptación, etc.)
- **Acción:** Routing inmediato a RRHH sin procesamiento adicional
- **Principio:** Falsos positivos preferibles a falsos negativos — es mejor escalar de más que filtrar de menos
- **Los datos de estos tickets NUNCA se envían a APIs externas de IA**

---

## 8. Stack Tecnológico

| Componente | Herramienta | Justificación |
|------------|-------------|---------------|
| Frontend / Dashboard | **Streamlit** (Python) | Rápido de construir, interactivo, ideal para MVP. Gratis. |
| Backend / Lógica | **Python** | Lenguaje del equipo, ecosistema rico, integración directa con APIs de IA |
| IA / LLM | **OpenAI GPT-4o-mini** | Bajo costo (~$0.15/1M tokens), buen rendimiento para clasificación. Presupuesto: ~$15-30/mes |
| Base de datos | **Google Sheets** (MVP) → **PostgreSQL** (producción) | MVP: integración nativa con Google Workspace. Producción: escalabilidad |
| Recepción de emails | **Gmail API** + Google Apps Script | Ya usan Google Workspace, integración nativa, sin costo adicional |
| Notificaciones | **Gmail API** (respuestas) + **Slack Webhook** (alertas críticas) | Canales que ya usan |
| Base de conocimiento | **Wiki de Marcos exportada** (Notion → Markdown) | ~200 artículos existentes, cero costo de creación de contenido |
| Hosting | **Streamlit Cloud** / **Vercel** | Gratuito para MVP |

**Costo mensual estimado:** ~$30-50 USD (muy dentro del presupuesto de $500)

**Restricción de privacidad:** Los tickets sensibles de RRHH nunca se envían a la API de OpenAI. Se detectan localmente por keywords antes de cualquier llamada a API externa.

---

## 9. MVP vs. Versión Completa

### MVP (Entregable hoy — 2 horas)

1. ✅ Interfaz web donde se pueden crear/ver tickets
2. ✅ Clasificación automática por IA (categoría + prioridad)
3. ✅ Respuesta automática para tickets de contraseña, VPN y software
4. ✅ Escalamiento a humano para tickets complejos
5. ✅ Detección de contenido sensible → routing a RRHH
6. ✅ Dashboard básico con métricas

**No incluye en MVP:** Integración real con Gmail API, notificaciones Slack, base de conocimiento RAG completa, flujos de aprobación automatizados.

### Versión Completa (Roadmap futuro)

| Fase | Timeline | Features |
|------|----------|----------|
| Fase 1 (Mes 1) | Post-MVP | Integración Gmail API real, import wiki de Marcos, notificaciones Slack para críticos |
| Fase 2 (Mes 2) | Estabilización | RAG con base de conocimiento, flujos de aprobación automatizados, historial de conversaciones |
| Fase 3 (Mes 3) | Expansión | Canal Slack como entrada, dashboard para Patricia, reportes mensuales automáticos |
| Fase 4 (Mes 4+) | Optimización | Métricas de satisfacción, feedback loop para mejorar IA, SLA tracking automático |

---

## 10. Métricas de Éxito

| KPI | Meta Mes 1 | Meta Mes 3 | Cómo se mide |
|-----|-----------|-----------|--------------|
| % Tickets resueltos automáticamente | 20% | 30-50% | Tickets cerrados sin intervención humana / total |
| Tiempo promedio de primera respuesta | < 5 min (IA) | < 5 min | Timestamp de recepción vs. primera respuesta |
| Tiempo promedio de resolución | < 8 horas | < 4 horas | Timestamp de apertura vs. cierre |
| Tickets correctamente clasificados | 80% | 90% | Auditoría semanal de muestra por Marcos |
| Satisfacción del usuario | Baseline | +20% | Encuesta post-resolución (opcional) |
| Tickets por categoría y departamento | Tracking | Tendencias | Dashboard automático |
| Tasa de rebote (usuario dice "no funcionó") | < 30% | < 15% | Respuestas negativas a resoluciones automáticas |

**Meta de Patricia:** Dashboard mensual con tickets totales, resueltos automáticamente, tiempo promedio, categorías, departamentos, y tendencias.

---

## 11. Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|---------|-------------|------------|
| **Resistencia de Marcos al cambio** | Alto — puede sabotear adopción como con Freshdesk | Alta | Posicionar el sistema como "liberador" de su tiempo, no reemplazo. Involucrar a Marcos en la configuración. Usar SU wiki como base de conocimiento (reconocimiento). |
| **Baja precisión de clasificación IA** | Medio — tickets mal priorizados | Media | Threshold de confianza (70%), escalamiento a humano en caso de duda, feedback loop para mejorar |
| **Tickets sensibles procesados por IA** | Crítico — riesgo legal | Baja | Detección por keywords ANTES de enviar a API. Falsos positivos > falsos negativos. Revisión periódica. |
| **Datos personales en APIs externas** | Alto — incumplimiento legal | Media | No enviar datos de RRHH a APIs. Para tickets normales: no incluir datos personales identificables en el prompt. |
| **Marcos como single point of failure** | Alto — si se va, se pierde conocimiento | Alta | Exportar y democratizar su wiki. Documentar procesos. Capacitar a Ana como backup completo. |
| **Baja adopción por usuarios** | Alto — repite Freshdesk | Media | Los usuarios NO cambian su flujo: siguen mandando email. Todo pasa "por detrás". |
| **Picos de demanda (post-actualizaciones)** | Medio — sistema sobrecargado | Media | La IA escala automáticamente. Alertas cuando volumen supera 2x promedio. |

---

## 12. Preguntas Abiertas

| Pregunta | Por qué importa | A quién preguntar |
|----------|-----------------|-------------------|
| ¿Marcos estaría dispuesto a compartir/exportar su wiki? | Es la pieza clave para RAG y resolución automática | Ricardo → Marcos |
| ¿Qué formato exacto tienen los emails de soporte actuales? | Necesario para parsing confiable | Marcos (muestra de emails) |
| ¿Existe consentimiento de empleados para procesamiento de datos por IA? | Cumplimiento de Ley Federal de Protección de Datos | Equipo legal de NovaTech |
| ¿Qué SaaS/herramientas están aprobadas por seguridad de la empresa? | Determina si podemos usar OpenAI, Streamlit Cloud, etc. | Patricia / Seguridad |
| ¿Cómo se verifica identidad actualmente para resets de contraseña? | Necesario para automatizar de forma segura | Marcos |

---
