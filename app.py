import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Config ---
st.set_page_config(
    page_title="NovaTech - Sistema de Tickets con IA",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Base de conocimiento (simulando wiki de Marcos exportada) ---
KNOWLEDGE_BASE = {
    "contraseña": {
        "titulo": "Reset de Contraseña - Google Workspace",
        "solucion": """**Pasos para restablecer tu contraseña de Google Workspace:**

1. Ve a [accounts.google.com](https://accounts.google.com)
2. Haz clic en **"¿Olvidaste tu contraseña?"**
3. Ingresa tu correo corporativo (@novatech.com)
4. Selecciona el método de recuperación (teléfono o correo alternativo)
5. Sigue las instrucciones en pantalla
6. Crea una nueva contraseña (mínimo 8 caracteres, incluye mayúsculas y números)

**Si no funciona:** Es posible que tu cuenta esté bloqueada. En ese caso, un agente de TI desbloqueará tu cuenta manualmente.

⏱️ Tiempo estimado: 5 minutos"""
    },
    "vpn": {
        "titulo": "Configuración y Troubleshooting de VPN",
        "solucion": """**Si no puedes conectarte a la VPN:**

1. **Verifica tu conexión a internet** — abre cualquier página web
2. **Reinicia el cliente VPN** — ciérralo completamente y vuelve a abrir
3. **Verifica credenciales** — usa tu usuario y contraseña de Google Workspace
4. **Windows:** Ve a Configuración → Red e Internet → VPN → Verifica que el perfil de NovaTech esté configurado
5. **Mac:** Ve a Preferencias del Sistema → Red → VPN
6. **Si sigue sin funcionar:** Reinicia tu computadora e intenta de nuevo

**Datos de conexión:**
- Servidor: vpn.novatech.com
- Tipo: IKEv2
- Autenticación: Credenciales corporativas

⏱️ Tiempo estimado: 10 minutos"""
    },
    "software": {
        "titulo": "Instalación de Software Aprobado",
        "solucion": """**Software que puedes instalar sin aprobación:**
Chrome, Slack, Zoom, VS Code, Postman, Figma, Office 365, Notion, Docker.

**Pasos:**
1. Descarga el software desde su sitio oficial
2. Ejecuta el instalador con permisos de administrador
3. Si te pide permisos elevados, contacta a TI

**Si necesitas software que NO está en la lista:**
Se requiere aprobación de la Directora General (Patricia Vega). Envía un correo a soporte@novatech.com indicando:
- Nombre del software
- Para qué lo necesitas
- Si tiene costo

⏱️ Tiempo de aprobación: 1-3 días hábiles"""
    },
    "impresora": {
        "titulo": "Problemas Comunes de Impresora",
        "solucion": """**Troubleshooting básico:**

1. **Verifica que la impresora esté encendida** y conectada a la red
2. **Reinicia la cola de impresión:**
   - Windows: Servicios → Print Spooler → Reiniciar
   - Mac: Preferencias → Impresoras → Eliminar y volver a agregar
3. **Verifica el papel y tóner** — las impresoras de cada piso tienen suministros en el gabinete
4. **Reinstala el driver** — descarga desde la intranet

**Si nada funciona:** Es probable que sea un problema de hardware. Un técnico revisará la impresora.

⏱️ Tiempo estimado: 15 minutos"""
    }
}

# Keywords para detección de contenido sensible RRHH
SENSITIVE_KEYWORDS = [
    "acoso", "hostigamiento", "discriminación", "denuncia", "abuso",
    "discapacidad", "adaptación", "embarazo", "despido injustificado",
    "amenaza", "violencia", "sexual", "intimidación", "mobbing",
    "represalia", "confidencial rrhh", "recursos humanos confidencial"
]

# --- Funciones de IA ---
def detect_sensitive_content(text: str) -> bool:
    """Detecta contenido sensible de RRHH por keywords.
    NUNCA se envía a API externa."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in SENSITIVE_KEYWORDS)

def classify_ticket_local(subject: str, body: str) -> dict:
    """Clasificación por keywords cuando no hay API key."""
    text = f"{subject} {body}".lower()

    # Detección de prioridad crítica
    critical_kw = ["servidor caído", "servidor de producción", "se cayó", "brecha de seguridad", "hackearon", "ransomware"]
    if any(kw in text for kw in critical_kw):
        return {"categoria": "🖥️ Servidor/Infraestructura", "prioridad": "🔴 Crítica", "confianza": 95, "auto_resolvable": False}

    # Categorización
    if any(kw in text for kw in ["contraseña", "password", "clave", "no puedo entrar", "acceso bloqueado", "login"]):
        return {"categoria": "🔑 Reset de Contraseñas", "prioridad": "🟢 Baja", "confianza": 90, "auto_resolvable": True, "kb_key": "contraseña"}
    elif any(kw in text for kw in ["vpn", "conectividad", "red", "internet", "wifi", "conexión"]):
        return {"categoria": "🌐 VPN / Conectividad", "prioridad": "🟡 Media", "confianza": 85, "auto_resolvable": True, "kb_key": "vpn"}
    elif any(kw in text for kw in ["instalar", "software", "programa", "aplicación", "actualizar", "app"]):
        return {"categoria": "💻 Software", "prioridad": "🟡 Media", "confianza": 80, "auto_resolvable": True, "kb_key": "software"}
    elif any(kw in text for kw in ["permiso", "acceso", "carpeta", "compartir", "drive", "folder"]):
        return {"categoria": "🔐 Permisos de Acceso", "prioridad": "🟡 Media", "confianza": 80, "auto_resolvable": False}
    elif any(kw in text for kw in ["mouse", "teclado", "monitor", "pantalla", "hardware", "cable", "cargador"]):
        return {"categoria": "🖱️ Hardware", "prioridad": "🟢 Baja", "confianza": 85, "auto_resolvable": False}
    elif any(kw in text for kw in ["impresora", "imprimir", "impresión", "escáner", "scanner"]):
        return {"categoria": "🖨️ Impresoras", "prioridad": "🟢 Baja", "confianza": 80, "auto_resolvable": True, "kb_key": "impresora"}

    return {"categoria": "📦 Otros", "prioridad": "🟡 Media", "confianza": 50, "auto_resolvable": False}

def classify_ticket_ai(subject: str, body: str) -> dict:
    """Clasificación con OpenAI si hay API key."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", st.session_state.get("api_key", "")))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """Eres un sistema de clasificación de tickets de soporte TI para NovaTech Solutions (200 empleados, México).

Clasifica el ticket en formato JSON con estos campos:
- categoria: una de ["🔑 Reset de Contraseñas", "🌐 VPN / Conectividad", "💻 Software", "🔐 Permisos de Acceso", "🖱️ Hardware", "🖨️ Impresoras", "🖥️ Servidor/Infraestructura", "📦 Otros"]
- prioridad: una de ["🔴 Crítica", "🟠 Alta", "🟡 Media", "🟢 Baja"]
- confianza: número 0-100
- auto_resolvable: boolean (true si se puede resolver con un instructivo)
- kb_key: si auto_resolvable, una de ["contraseña", "vpn", "software", "impresora"], null si no
- razonamiento: explicación breve en español

Criterios de prioridad:
- Crítica: servidor caído, brecha seguridad, sistema de producción inoperable
- Alta: empleado no puede trabajar, bloqueo total
- Media: puede trabajar parcialmente
- Baja: solicitudes, preguntas, resets"""},
                {"role": "user", "content": f"Asunto: {subject}\n\nContenido: {body}"}
            ],
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        st.warning(f"IA no disponible, usando clasificación local: {e}")
        return classify_ticket_local(subject, body)

def classify_ticket(subject: str, body: str) -> dict:
    """Clasifica un ticket usando IA si está disponible, o keywords si no."""
    api_key = os.environ.get("OPENAI_API_KEY", st.session_state.get("api_key", ""))
    if api_key:
        return classify_ticket_ai(subject, body)
    return classify_ticket_local(subject, body)

# --- Session State Init ---
if "tickets" not in st.session_state:
    st.session_state.tickets = []

if "demo_loaded" not in st.session_state:
    st.session_state.demo_loaded = False

def load_demo_data():
    """Carga tickets de ejemplo para demostración."""
    demo_tickets = [
        {"id": "TK-001", "fecha": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "remitente": "carlos.ruiz@novatech.com", "departamento": "Ventas", "oficina": "Guadalajara", "asunto": "No puedo entrar a mi correo", "cuerpo": "Hola, desde ayer no puedo acceder a mi correo, creo que se me olvidó la contraseña y ya intenté recuperarla pero no me llega el código.", "clasificacion": {"categoria": "🔑 Reset de Contraseñas", "prioridad": "🟢 Baja", "confianza": 92, "auto_resolvable": True, "kb_key": "contraseña"}, "estado": "✅ Resuelto (Auto)", "respuesta_auto": True},
        {"id": "TK-002", "fecha": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "remitente": "ana.lopez@novatech.com", "departamento": "Administración", "oficina": "Guadalajara", "asunto": "La VPN no conecta desde casa", "cuerpo": "Estoy intentando conectarme a la VPN desde home office pero me da error de timeout. Ya reinicié mi computadora.", "clasificacion": {"categoria": "🌐 VPN / Conectividad", "prioridad": "🟡 Media", "confianza": 88, "auto_resolvable": True, "kb_key": "vpn"}, "estado": "✅ Resuelto (Auto)", "respuesta_auto": True},
        {"id": "TK-003", "fecha": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), "remitente": "roberto.diaz@novatech.com", "departamento": "Desarrollo", "oficina": "Monterrey", "asunto": "Se cayó el servidor de staging", "cuerpo": "El servidor de staging no responde desde hace 30 minutos. No podemos deployar. Esto es urgente porque tenemos entrega con cliente mañana.", "clasificacion": {"categoria": "🖥️ Servidor/Infraestructura", "prioridad": "🔴 Crítica", "confianza": 96, "auto_resolvable": False}, "estado": "⏳ Escalado a Marcos", "respuesta_auto": False},
        {"id": "TK-004", "fecha": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), "remitente": "laura.martinez@novatech.com", "departamento": "Diseño", "oficina": "Monterrey", "asunto": "Necesito acceso a la carpeta de assets del proyecto Alfa", "cuerpo": "Hola, me cambiaron de proyecto y necesito acceso a la carpeta compartida de Google Drive del proyecto Alfa. Mi jefe es Pedro Sánchez.", "clasificacion": {"categoria": "🔐 Permisos de Acceso", "prioridad": "🟡 Media", "confianza": 85, "auto_resolvable": False}, "estado": "⏳ Esperando aprobación de jefe", "respuesta_auto": False},
        {"id": "TK-005", "fecha": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), "remitente": "maria.garcia@novatech.com", "departamento": "QA", "oficina": "Monterrey", "asunto": "Quiero instalar Postman", "cuerpo": "Necesito instalar Postman para testing de APIs. ¿Me pueden ayudar?", "clasificacion": {"categoria": "💻 Software", "prioridad": "🟢 Baja", "confianza": 90, "auto_resolvable": True, "kb_key": "software"}, "estado": "✅ Resuelto (Auto)", "respuesta_auto": True},
        {"id": "TK-006", "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "remitente": "empleado.anonimo@novatech.com", "departamento": "—", "oficina": "—", "asunto": "Situación personal delicada", "cuerpo": "Necesito reportar una situación de hostigamiento con mi supervisor. Es urgente y confidencial.", "clasificacion": {"categoria": "🚨 RRHH - CONFIDENCIAL", "prioridad": "🔴 Crítica", "confianza": 99, "auto_resolvable": False}, "estado": "🔒 Derivado a RRHH", "respuesta_auto": False, "sensible": True},
    ]
    st.session_state.tickets = demo_tickets
    st.session_state.demo_loaded = True

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("NovaTech Tickets")
    st.caption("Sistema Inteligente de Soporte con IA")
    st.divider()

    menu = st.radio("Navegación", ["📝 Nuevo Ticket", "📋 Todos los Tickets", "📊 Dashboard", "⚙️ Configuración"], label_visibility="collapsed")

    st.divider()
    if not st.session_state.demo_loaded:
        if st.button("🎮 Cargar datos demo", use_container_width=True):
            load_demo_data()
            st.rerun()
    else:
        st.success(f"✅ {len(st.session_state.tickets)} tickets cargados")

    st.divider()
    st.caption("MVP — Evaluación Ternova 2026")

# --- Páginas ---
if menu == "📝 Nuevo Ticket":
    st.header("📝 Crear Nuevo Ticket")
    st.info("Simula un email entrante a soporte@novatech.com")

    col1, col2 = st.columns(2)
    with col1:
        remitente = st.text_input("De (email)", placeholder="nombre@novatech.com")
        departamento = st.selectbox("Departamento", ["Desarrollo", "Infraestructura", "Operaciones", "Ventas", "Administración", "RRHH", "Dirección", "QA", "Diseño"])
    with col2:
        oficina = st.selectbox("Oficina", ["Monterrey", "Guadalajara"])
        asunto = st.text_input("Asunto", placeholder="No puedo conectarme a la VPN")

    cuerpo = st.text_area("Descripción del problema", height=150, placeholder="Describe tu problema con el mayor detalle posible...")

    if st.button("🚀 Enviar Ticket", type="primary", use_container_width=True):
        if not remitente or not asunto or not cuerpo:
            st.error("Completa todos los campos")
        else:
            with st.spinner("🤖 La IA está analizando tu ticket..."):
                # 1. Detección de contenido sensible PRIMERO (local, sin API)
                is_sensitive = detect_sensitive_content(f"{asunto} {cuerpo}")

                if is_sensitive:
                    clasificacion = {
                        "categoria": "🚨 RRHH - CONFIDENCIAL",
                        "prioridad": "🔴 Crítica",
                        "confianza": 99,
                        "auto_resolvable": False
                    }
                    estado = "🔒 Derivado a RRHH"
                    st.warning("🔒 **Contenido sensible detectado.** Este ticket ha sido derivado directamente a Recursos Humanos de forma confidencial. Ningún agente de TI tendrá acceso.")
                else:
                    # 2. Clasificación por IA
                    clasificacion = classify_ticket(asunto, cuerpo)

                    if clasificacion.get("auto_resolvable") and clasificacion.get("kb_key"):
                        estado = "✅ Resuelto (Auto)"
                        kb = KNOWLEDGE_BASE.get(clasificacion["kb_key"], {})
                        st.success(f"### ✅ Respuesta automática\n**{kb.get('titulo', '')}**\n\n{kb.get('solucion', '')}")
                        st.info("💡 *Si esta solución no funciona, responde a este correo y un agente humano te atenderá.*")
                    elif clasificacion.get("prioridad") == "🔴 Crítica":
                        estado = "⏳ Escalado a Marcos"
                        st.error("🚨 **TICKET CRÍTICO** — Escalado inmediatamente a Marcos Solís y Ricardo Méndez.")
                    else:
                        estado = "⏳ En cola para agente"
                        st.warning(f"📋 Ticket registrado y asignado a un agente de TI. Prioridad: {clasificacion.get('prioridad', 'Media')}")

                ticket_id = f"TK-{len(st.session_state.tickets) + 1:03d}"
                nuevo_ticket = {
                    "id": ticket_id,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "remitente": remitente,
                    "departamento": departamento,
                    "oficina": oficina,
                    "asunto": asunto,
                    "cuerpo": cuerpo,
                    "clasificacion": clasificacion,
                    "estado": estado,
                    "respuesta_auto": estado == "✅ Resuelto (Auto)",
                    "sensible": is_sensitive if is_sensitive else False
                }
                st.session_state.tickets.append(nuevo_ticket)

                # Mostrar clasificación
                st.divider()
                c1, c2, c3 = st.columns(3)
                c1.metric("Categoría", clasificacion.get("categoria", "—"))
                c2.metric("Prioridad", clasificacion.get("prioridad", "—"))
                c3.metric("Confianza IA", f"{clasificacion.get('confianza', 0)}%")

elif menu == "📋 Todos los Tickets":
    st.header("📋 Todos los Tickets")

    if not st.session_state.tickets:
        st.info("No hay tickets aún. Crea uno nuevo o carga los datos demo.")
    else:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_estado = st.multiselect("Estado", ["✅ Resuelto (Auto)", "⏳ Escalado a Marcos", "⏳ En cola para agente", "⏳ Esperando aprobación de jefe", "🔒 Derivado a RRHH"], default=None)
        with col2:
            filtro_prioridad = st.multiselect("Prioridad", ["🔴 Crítica", "🟠 Alta", "🟡 Media", "🟢 Baja"], default=None)
        with col3:
            filtro_oficina = st.multiselect("Oficina", ["Monterrey", "Guadalajara"], default=None)

        tickets_filtrados = st.session_state.tickets
        if filtro_estado:
            tickets_filtrados = [t for t in tickets_filtrados if t["estado"] in filtro_estado]
        if filtro_prioridad:
            tickets_filtrados = [t for t in tickets_filtrados if t["clasificacion"].get("prioridad") in filtro_prioridad]
        if filtro_oficina:
            tickets_filtrados = [t for t in tickets_filtrados if t.get("oficina") in filtro_oficina]

        for ticket in reversed(tickets_filtrados):
            if ticket.get("sensible"):
                with st.expander(f"🔒 {ticket['id']} — CONFIDENCIAL — {ticket['fecha']}"):
                    st.error("Este ticket es confidencial y solo es visible para RRHH. Contenido oculto por políticas de privacidad.")
            else:
                prioridad = ticket["clasificacion"].get("prioridad", "")
                with st.expander(f"{prioridad} {ticket['id']} — {ticket['asunto']} — {ticket['estado']}"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**De:** {ticket['remitente']}")
                    c2.write(f"**Depto:** {ticket.get('departamento', '—')}")
                    c3.write(f"**Oficina:** {ticket.get('oficina', '—')}")
                    c4.write(f"**Fecha:** {ticket['fecha']}")
                    st.write(f"**Categoría:** {ticket['clasificacion'].get('categoria', '—')}")
                    st.write(f"**Confianza IA:** {ticket['clasificacion'].get('confianza', 0)}%")
                    st.divider()
                    st.write(ticket.get("cuerpo", ""))

                    if ticket.get("respuesta_auto") and ticket["clasificacion"].get("kb_key"):
                        kb = KNOWLEDGE_BASE.get(ticket["clasificacion"]["kb_key"], {})
                        st.success(f"**Respuesta automática enviada:**\n\n{kb.get('solucion', '')}")

elif menu == "📊 Dashboard":
    st.header("📊 Dashboard de Métricas")

    if not st.session_state.tickets:
        st.info("Carga los datos demo para ver el dashboard con métricas.")
    else:
        tickets = st.session_state.tickets
        total = len(tickets)
        auto_resueltos = sum(1 for t in tickets if t.get("respuesta_auto"))
        sensibles = sum(1 for t in tickets if t.get("sensible"))
        escalados = total - auto_resueltos - sensibles

        # KPIs principales
        st.subheader("Resumen General")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Tickets", total)
        k2.metric("Resueltos por IA", auto_resueltos, f"{auto_resueltos/total*100:.0f}%" if total > 0 else "0%")
        k3.metric("Escalados a Humano", escalados)
        k4.metric("RRHH (Confidencial)", sensibles)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            # Gráfica por categoría
            categorias = [t["clasificacion"].get("categoria", "Otro") for t in tickets]
            df_cat = pd.DataFrame({"Categoría": categorias})
            fig_cat = px.pie(df_cat, names="Categoría", title="Tickets por Categoría", hole=0.4)
            fig_cat.update_layout(height=400)
            st.plotly_chart(fig_cat, use_container_width=True)

        with col2:
            # Gráfica por prioridad
            prioridades = [t["clasificacion"].get("prioridad", "Media") for t in tickets]
            df_pri = pd.DataFrame({"Prioridad": prioridades})
            fig_pri = px.pie(df_pri, names="Prioridad", title="Tickets por Prioridad", hole=0.4,
                           color_discrete_map={"🔴 Crítica": "#e74c3c", "🟠 Alta": "#e67e22", "🟡 Media": "#f1c40f", "🟢 Baja": "#2ecc71"})
            fig_pri.update_layout(height=400)
            st.plotly_chart(fig_pri, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Resolución automática vs manual
            fig_res = go.Figure(data=[go.Bar(
                x=["Resueltos por IA", "Escalados a Humano", "RRHH"],
                y=[auto_resueltos, escalados, sensibles],
                marker_color=["#2ecc71", "#3498db", "#e74c3c"]
            )])
            fig_res.update_layout(title="Resolución: IA vs Humano", height=400)
            st.plotly_chart(fig_res, use_container_width=True)

        with col4:
            # Por oficina
            oficinas = [t.get("oficina", "—") for t in tickets if not t.get("sensible")]
            df_ofi = pd.DataFrame({"Oficina": oficinas})
            fig_ofi = px.pie(df_ofi, names="Oficina", title="Tickets por Oficina", hole=0.4,
                           color_discrete_map={"Monterrey": "#3498db", "Guadalajara": "#9b59b6"})
            fig_ofi.update_layout(height=400)
            st.plotly_chart(fig_ofi, use_container_width=True)

        # Tabla resumen por departamento
        st.subheader("Tickets por Departamento")
        deptos = [t.get("departamento", "—") for t in tickets if not t.get("sensible")]
        df_dep = pd.DataFrame({"Departamento": deptos}).value_counts().reset_index()
        df_dep.columns = ["Departamento", "Tickets"]
        st.dataframe(df_dep, use_container_width=True, hide_index=True)

elif menu == "⚙️ Configuración":
    st.header("⚙️ Configuración")

    st.subheader("API de OpenAI (Opcional)")
    st.caption("Sin API key, el sistema usa clasificación por keywords. Con API key, usa GPT-4o-mini para clasificación más precisa.")

    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get("api_key", ""))
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ API key configurada. La clasificación usará GPT-4o-mini.")
    else:
        st.info("ℹ️ Modo local activo — clasificación por keywords (funcional para demo)")

    st.divider()
    st.subheader("Acerca del Sistema")
    st.markdown("""
    **Sistema Inteligente de Tickets — NovaTech Solutions**

    - **Clasificación automática** de tickets por categoría y prioridad
    - **Resolución automática** para tickets comunes (contraseñas, VPN, software, impresoras)
    - **Detección de contenido sensible** (RRHH) con routing confidencial
    - **Escalamiento inteligente** a agentes humanos para casos complejos
    - **Dashboard de métricas** para dirección

    **Stack:** Python + Streamlit + OpenAI GPT-4o-mini (opcional)

    **Base de conocimiento:** Basada en la wiki de Marcos Solís (~200 artículos en Notion)
    """)
