"""
NovaTech · Sistema Inteligente de Soporte
Chat IA + Tickets + Analytics + Base de Conocimiento auto-aprendible
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from database import (init_db, save_ticket, get_tickets, start_conversation,
                      add_message, get_messages, resolve_conversation,
                      get_stats, load_demo_data)
from knowledge_base import init_kb, search_kb, get_all_articles, add_learned_article
from ai_engine import (is_sensitive, chat_response, classify_local,
                       extract_ticket_decision, clean_response, extract_learning)

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="NovaTech · Soporte IA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
init_kb()

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1117 0%, #161b27 60%, #1a2235 100%) !important;
    border-right: 1px solid #21283a !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
section[data-testid="stSidebar"] hr { border-color: #21283a !important; }
section[data-testid="stSidebar"] .stButton button {
    background: #21283a !important;
    border: 1px solid #30394d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #2d3748 !important;
    border-color: #4a5568 !important;
}
.stRadio label { padding: 6px 10px; border-radius: 8px; transition: all .15s; }
.stRadio label:hover { background: rgba(255,255,255,.06) !important; }
.stRadio div[data-testid="stWidgetLabel"] { display: none; }

/* ── Main area ── */
.main .block-container { padding: 1.5rem 2rem 4rem; max-width: 1400px; }

/* ── Page title ── */
.pg-title {
    font-size: 26px; font-weight: 800; color: #0f172a; letter-spacing: -.5px;
    margin-bottom: 2px;
}
.pg-sub { font-size: 14px; color: #64748b; margin-bottom: 28px; }

/* ── KPI card ── */
.kpi { background: #fff; border-radius: 14px; padding: 20px 22px;
       border: 1px solid #e8edf4; box-shadow: 0 1px 4px rgba(0,0,0,.05);
       display: flex; flex-direction: column; gap: 4px; }
.kpi-ico { font-size: 22px; margin-bottom: 4px; }
.kpi-val { font-size: 2rem; font-weight: 800; color: #0f172a; line-height: 1; }
.kpi-lbl { font-size: 12px; font-weight: 600; color: #64748b;
           text-transform: uppercase; letter-spacing: .06em; }
.kpi-del { font-size: 13px; font-weight: 600; }
.kpi-del.pos { color: #16a34a; } .kpi-del.neg { color: #dc2626; }

/* ── Badge ── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 10px; border-radius: 9999px;
    font-size: 11px; font-weight: 600; white-space: nowrap;
}
.b-red    { background: #fee2e2; color: #b91c1c; }
.b-orange { background: #ffedd5; color: #c2410c; }
.b-yellow { background: #fef9c3; color: #92400e; }
.b-green  { background: #dcfce7; color: #15803d; }
.b-blue   { background: #dbeafe; color: #1d4ed8; }
.b-purple { background: #ede9fe; color: #6d28d9; }
.b-gray   { background: #f1f5f9; color: #475569; }

/* ── Ticket row ── */
.tk-row {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 14px 18px; margin-bottom: 10px;
    transition: box-shadow .2s, border-color .2s;
}
.tk-row:hover { box-shadow: 0 4px 16px rgba(0,0,0,.08); border-color: #c7d2de; }
.tk-id { font-size: 11px; color: #94a3b8; font-weight: 600; }
.tk-title { font-size: 15px; font-weight: 600; color: #1e293b; }
.tk-meta { font-size: 12px; color: #64748b; }

/* ── Chat ── */
.chat-wrap { background: #f8fafc; border-radius: 14px;
             border: 1px solid #e2e8f0; padding: 24px; min-height: 400px; }
div[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border-color: #cbd5e1 !important;
}
div[data-testid="stChatMessage"] { padding: 0 !important; }

/* ── KB article ── */
.kb-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 18px 20px; margin-bottom: 12px;
}
.kb-tag {
    display: inline-block; background: #f1f5f9; color: #475569;
    border-radius: 6px; padding: 2px 8px; font-size: 11px; margin: 2px;
}
.kb-src-manual  { color: #3b82f6; }
.kb-src-learned { color: #8b5cf6; }

/* ── Divider ── */
.section-divider { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }

/* ── Alerts ── */
.alert-critical {
    background: #fff1f2; border-left: 4px solid #ef4444;
    border-radius: 8px; padding: 12px 16px; color: #7f1d1d; font-size: 14px;
}
.alert-success {
    background: #f0fdf4; border-left: 4px solid #22c55e;
    border-radius: 8px; padding: 12px 16px; color: #14532d; font-size: 14px;
}
.alert-info {
    background: #eff6ff; border-left: 4px solid #3b82f6;
    border-radius: 8px; padding: 12px 16px; color: #1e3a8a; font-size: 14px;
}

/* ── Form ── */
div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important; border-radius: 12px !important;
    background: #fff !important;
}
div[data-testid="stExpander"] summary { font-weight: 600 !important; }

/* ── Plotly ── */
.js-plotly-plot .plotly { border-radius: 12px; }

/* ── Dataframe ── */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Metric ── */
div[data-testid="stMetric"] {
    background: white; border-radius: 12px; padding: 16px 18px;
    border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────
for k, v in [
    ("conv_id", None), ("chat_msgs", []),
    ("last_ticket", None), ("api_key", ""), ("show_form", False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ──────────────────────────────────────────────────────────

PRIORITY_ORDER = {"🔴 Crítica": 0, "🟠 Alta": 1, "🟡 Media": 2, "🟢 Baja": 3}


def _priority_badge(pri: str) -> str:
    cls = {"🔴 Crítica": "b-red", "🟠 Alta": "b-orange",
           "🟡 Media": "b-yellow", "🟢 Baja": "b-green"}.get(pri, "b-gray")
    return f'<span class="badge {cls}">{pri}</span>'


def _state_badge(estado: str) -> str:
    if "Resuelto" in estado:   return f'<span class="badge b-green">{estado}</span>'
    if "RRHH" in estado:       return f'<span class="badge b-purple">{estado}</span>'
    if "Escalado" in estado:   return f'<span class="badge b-red">{estado}</span>'
    if "aprobación" in estado: return f'<span class="badge b-orange">{estado}</span>'
    return f'<span class="badge b-blue">{estado}</span>'


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 16px 12px;">
        <div style="font-size:20px;font-weight:800;color:#f0f6fc;">⚡ NovaTech</div>
        <div style="font-size:11px;color:#484f58;margin-top:2px;letter-spacing:.04em;">
            SOPORTE INTELIGENTE CON IA
        </div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio("nav", [
        "💬  Chat de Soporte",
        "🎫  Tickets",
        "📊  Dashboard",
        "🧠  Base de Conocimiento",
        "⚙️  Configuración",
    ])

    st.divider()

    stats = get_stats()
    total = stats["total"]
    auto_pct = f"{stats['auto'] / total * 100:.0f}" if total else "0"

    st.markdown(f"""
    <div style="padding:0 12px 8px;">
        <div style="font-size:10px;color:#484f58;text-transform:uppercase;
                    letter-spacing:.08em;margin-bottom:14px;">Estado del sistema</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
            <span style="color:#8b949e;font-size:13px;">Total tickets</span>
            <span style="color:#e6edf3;font-weight:700;font-size:13px;">{total}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
            <span style="color:#8b949e;font-size:13px;">Resueltos por IA</span>
            <span style="color:#3fb950;font-weight:700;font-size:13px;">{stats['auto']} ({auto_pct}%)</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
            <span style="color:#8b949e;font-size:13px;">Críticos</span>
            <span style="color:#f85149;font-weight:700;font-size:13px;">{stats['criticos']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#8b949e;font-size:13px;">Desde chat</span>
            <span style="color:#d2a8ff;font-weight:700;font-size:13px;">{stats['chat_orig']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    ca, cb = st.columns(2)
    with ca:
        if st.button("📥 Demo", use_container_width=True):
            load_demo_data()
            st.rerun()
    with cb:
        if st.button("🗑 Chat", use_container_width=True, help="Reiniciar chat"):
            st.session_state.conv_id = None
            st.session_state.chat_msgs = []
            st.session_state.last_ticket = None
            st.rerun()

    if st.session_state.api_key:
        st.markdown(
            '<div style="margin:12px 12px 0;background:#1a2f1a;border:1px solid #2ea043;'
            'border-radius:8px;padding:8px 12px;font-size:12px;color:#3fb950;">🤖 GPT-4o-mini activo</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="margin:12px 12px 0;background:#1c2333;border:1px solid #30363d;'
            'border-radius:8px;padding:8px 12px;font-size:12px;color:#8b949e;">🔑 Modo local (keywords)</div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════
#  CHAT DE SOPORTE
# ═══════════════════════════════════════════════════════════════════════
if "Chat" in menu:
    st.markdown('<div class="pg-title">💬 Chat de Soporte</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pg-sub">Cuéntame tu problema. Si puedo resolverlo lo hago aquí; '
        'si no, creo el ticket automáticamente.</div>',
        unsafe_allow_html=True,
    )

    # Ticket generado banner
    if st.session_state.last_ticket:
        t = st.session_state.last_ticket
        st.markdown(
            f'<div class="alert-success">🎫 <b>Ticket {t["id"]}</b> creado automáticamente · '
            f'{t.get("categoria","—")} · {t.get("prioridad","—")}</div>',
            unsafe_allow_html=True,
        )

    # Inicializar conversación
    if not st.session_state.conv_id:
        st.session_state.conv_id = start_conversation()

    # Bienvenida
    if not st.session_state.chat_msgs:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px 20px;color:#94a3b8;">
            <div style="font-size:56px;margin-bottom:12px;">⚡</div>
            <div style="font-size:20px;font-weight:700;color:#1e293b;">Hola, soy Nova</div>
            <div style="font-size:14px;margin-top:6px;color:#64748b;">
                Asistente inteligente de TI · NovaTech Solutions
            </div>
            <div style="display:flex;gap:10px;justify-content:center;margin-top:24px;flex-wrap:wrap;">
                <span class="badge b-blue">🔑 Contraseñas</span>
                <span class="badge b-green">🌐 VPN</span>
                <span class="badge b-purple">💻 Software</span>
                <span class="badge b-yellow">🖨️ Impresoras</span>
                <span class="badge b-gray">🖱️ Hardware</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Mensajes del chat
    for msg in st.session_state.chat_msgs:
        avatar = "🧑‍💼" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Escribe tu problema o pregunta..."):

        if is_sensitive(prompt):
            # Contenido sensible → ticket RRHH + respuesta
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            reply = (
                "🔒 **Contenido confidencial detectado.**\n\n"
                "Este caso ha sido derivado **directamente a Recursos Humanos** de forma confidencial. "
                "Ningún agente de TI tendrá acceso al contenido.\n\n"
                "El equipo de RRHH se pondrá en contacto contigo a la brevedad."
            )
            st.session_state.chat_msgs.append({"role": "assistant", "content": reply})
            add_message(st.session_state.conv_id, "user", prompt)
            add_message(st.session_state.conv_id, "assistant", reply)
            tid = save_ticket({
                "remitente": "confidencial@novatech.com",
                "asunto": "Caso confidencial RRHH",
                "cuerpo": "[OCULTO POR PRIVACIDAD]",
                "categoria": "🚨 RRHH - CONFIDENCIAL",
                "prioridad": "🔴 Crítica", "confianza": 99,
                "estado": "🔒 Derivado a RRHH", "sensible": True,
                "origen": "chat", "conversation_id": st.session_state.conv_id,
            })
            st.session_state.last_ticket = {"id": tid, "categoria": "🚨 RRHH", "prioridad": "🔴 Crítica"}
            st.rerun()

        else:
            st.session_state.chat_msgs.append({"role": "user", "content": prompt})
            add_message(st.session_state.conv_id, "user", prompt)

            with st.spinner("Nova está pensando…"):
                raw = chat_response(st.session_state.chat_msgs[:-1], prompt)
                decision = extract_ticket_decision(raw)
                visible = clean_response(raw)

            st.session_state.chat_msgs.append({"role": "assistant", "content": visible})
            add_message(st.session_state.conv_id, "assistant", visible)

            # Auto-ticket
            if decision and decision.get("generar_ticket"):
                cl_data = classify_local(prompt)
                tid = save_ticket({
                    "remitente": "chat@novatech.com",
                    "asunto": decision.get("asunto_sugerido", prompt[:70]),
                    "cuerpo": prompt,
                    "categoria": decision.get("categoria", cl_data.get("categoria")),
                    "prioridad": decision.get("prioridad", cl_data.get("prioridad")),
                    "confianza": cl_data.get("confianza", 70),
                    "estado": "⏳ En cola",
                    "auto_resolvable": False,
                    "origen": "chat",
                    "conversation_id": st.session_state.conv_id,
                })
                st.session_state.last_ticket = {
                    "id": tid,
                    "categoria": decision.get("categoria", ""),
                    "prioridad": decision.get("prioridad", ""),
                }
            else:
                st.session_state.last_ticket = None

            # Auto-aprendizaje al final de conversaciones largas
            if len(st.session_state.chat_msgs) >= 8 and len(st.session_state.chat_msgs) % 8 == 0:
                learning = extract_learning(st.session_state.chat_msgs)
                if learning and learning.get("vale_guardar"):
                    add_learned_article(
                        titulo=learning["titulo"],
                        categoria=learning.get("categoria", "📦 Otros"),
                        tags=learning.get("tags", []),
                        contenido=learning["contenido"],
                        conversation_id=st.session_state.conv_id,
                    )

            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
#  TICKETS
# ═══════════════════════════════════════════════════════════════════════
elif "Tickets" in menu:
    st.markdown('<div class="pg-title">🎫 Gestión de Tickets</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Explora, filtra y ordena todos los tickets de soporte.</div>',
                unsafe_allow_html=True)

    # Toolbar
    col_s, col_btn = st.columns([5, 1])
    with col_s:
        search = st.text_input("", placeholder="🔍  Buscar por asunto, remitente o descripción…",
                               label_visibility="collapsed")
    with col_btn:
        if st.button("＋ Nuevo", type="primary", use_container_width=True):
            st.session_state.show_form = not st.session_state.show_form

    # Formulario nuevo ticket
    if st.session_state.show_form:
        with st.expander("➕ Crear Ticket Manualmente", expanded=True):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                f_remitente = st.text_input("Email", placeholder="usuario@novatech.com")
                f_depto = st.selectbox("Departamento", [
                    "Desarrollo", "Infraestructura", "Operaciones", "Ventas",
                    "Administración", "RRHH", "Dirección", "QA", "Diseño"])
            with fc2:
                f_oficina = st.selectbox("Oficina", ["Monterrey", "Guadalajara"])
                f_asunto = st.text_input("Asunto", placeholder="Describe brevemente el problema")
            with fc3:
                f_prioridad = st.selectbox("Prioridad manual", ["Auto", "🔴 Crítica", "🟠 Alta", "🟡 Media", "🟢 Baja"])
            f_cuerpo = st.text_area("Descripción completa", height=100,
                                    placeholder="Con más detalle…")

            if st.button("✅ Crear Ticket", type="primary"):
                if f_remitente and f_asunto and f_cuerpo:
                    cl_data = classify_local(f"{f_asunto} {f_cuerpo}")
                    pri = f_prioridad if f_prioridad != "Auto" else cl_data.get("prioridad", "🟡 Media")
                    estado = "✅ Resuelto (Auto)" if cl_data.get("auto_resolvable") else "⏳ En cola"
                    tid = save_ticket({
                        "remitente": f_remitente, "departamento": f_depto,
                        "oficina": f_oficina, "asunto": f_asunto, "cuerpo": f_cuerpo,
                        "categoria": cl_data.get("categoria"), "prioridad": pri,
                        "confianza": cl_data.get("confianza", 70), "estado": estado,
                        "auto_resolvable": cl_data.get("auto_resolvable", False),
                        "kb_key": cl_data.get("kb_key"), "origen": "manual",
                    })
                    st.success(f"✅ Ticket **{tid}** creado.")
                    st.session_state.show_form = False
                    st.rerun()
                else:
                    st.error("Completa email, asunto y descripción.")

    # Filtros
    with st.expander("🔽 Filtros y Ordenación", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            f_pri = st.multiselect("Prioridad", ["🔴 Crítica", "🟠 Alta", "🟡 Media", "🟢 Baja"])
        with fc2:
            f_est = st.multiselect("Estado", [
                "✅ Resuelto (Auto)", "⏳ Escalado a Marcos", "⏳ En cola",
                "⏳ Esperando aprobación", "🔒 Derivado a RRHH"])
        with fc3:
            f_cat = st.multiselect("Categoría", [
                "🔑 Reset de Contraseñas", "🌐 VPN / Conectividad", "💻 Software",
                "🔐 Permisos de Acceso", "🖱️ Hardware", "🖨️ Impresoras",
                "🖥️ Servidor/Infraestructura", "📦 Otros"])
        with fc4:
            sort_by = st.selectbox("Ordenar", [
                "Más reciente", "Más antiguo", "Mayor prioridad", "Menor prioridad"])

    tickets = get_tickets(
        estado=f_est or None,
        prioridad=f_pri or None,
        categoria=f_cat or None,
        search=search or None,
    )

    # Ordenar
    if sort_by == "Más antiguo":
        tickets = list(reversed(tickets))
    elif sort_by == "Mayor prioridad":
        tickets.sort(key=lambda t: PRIORITY_ORDER.get(t.get("prioridad", ""), 9))
    elif sort_by == "Menor prioridad":
        tickets.sort(key=lambda t: -PRIORITY_ORDER.get(t.get("prioridad", ""), -1))

    st.markdown(
        f'<div style="color:#64748b;font-size:13px;margin:4px 0 16px;">'
        f'<b>{len(tickets)}</b> tickets encontrados</div>',
        unsafe_allow_html=True,
    )

    if not tickets:
        st.markdown(
            '<div class="alert-info">No hay tickets que coincidan con los filtros. '
            'Usa el chat para crear uno o carga los datos demo.</div>',
            unsafe_allow_html=True,
        )

    for tk in tickets:
        if tk.get("sensible"):
            with st.expander(f"🔒 {tk['id']} — CONFIDENCIAL RRHH — {tk['fecha']}"):
                st.error("Contenido confidencial. Visible solo para RRHH.")
            continue

        pri_badge = _priority_badge(tk.get("prioridad", ""))
        est_badge = _state_badge(tk.get("estado", ""))
        origen_ico = "💬" if tk.get("origen") == "chat" else "📝"

        with st.expander(
            f"{origen_ico} **{tk['id']}**  ·  {tk['asunto']}  ·  {tk['fecha']}",
            expanded=False,
        ):
            r1, r2, r3, r4 = st.columns(4)
            r1.markdown(f"**Remitente**  \n`{tk.get('remitente','—')}`")
            r2.markdown(f"**Departamento**  \n{tk.get('departamento','—')}")
            r3.markdown(f"**Oficina**  \n{tk.get('oficina','—')}")
            r4.markdown(f"**Origen**  \n{origen_ico} {tk.get('origen','manual')}")

            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            r5, r6, r7 = st.columns(3)
            r5.markdown(f"**Categoría**  \n{tk.get('categoria','—')}")
            r6.markdown(f"**Prioridad**  \n{tk.get('prioridad','—')}")
            r7.markdown(f"**Confianza IA**  \n{tk.get('confianza',0)}%")

            st.markdown(f"**Estado:** {tk.get('estado','—')}")
            if tk.get("cuerpo"):
                st.markdown(f"---\n> {tk['cuerpo']}")

# ═══════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
elif "Dashboard" in menu:
    st.markdown('<div class="pg-title">📊 Dashboard Analítico</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Métricas en tiempo real del sistema de soporte.</div>',
                unsafe_allow_html=True)

    stats = get_stats()
    total = stats["total"]

    if total == 0:
        st.markdown(
            '<div class="alert-info">Carga datos demo (barra lateral) o crea tickets para ver métricas.</div>',
            unsafe_allow_html=True,
        )
    else:
        # ── KPIs ──
        k1, k2, k3, k4, k5 = st.columns(5)
        auto_pct = stats["auto"] / total * 100 if total else 0
        escalados = total - stats["auto"] - stats["sensibles"]

        with k1:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-ico">🎫</div>
                <div class="kpi-val">{total}</div>
                <div class="kpi-lbl">Total Tickets</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-ico">🤖</div>
                <div class="kpi-val">{stats['auto']}</div>
                <div class="kpi-lbl">Auto-resueltos</div>
                <div class="kpi-del pos">▲ {auto_pct:.0f}%</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-ico">👷</div>
                <div class="kpi-val">{escalados}</div>
                <div class="kpi-lbl">Escalados</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-ico">🔴</div>
                <div class="kpi-val">{stats['criticos']}</div>
                <div class="kpi-lbl">Críticos</div>
            </div>""", unsafe_allow_html=True)
        with k5:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-ico">💬</div>
                <div class="kpi-val">{stats['chat_orig']}</div>
                <div class="kpi-lbl">Desde Chat</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts row 1 ──
        c1, c2 = st.columns(2)

        with c1:
            if stats["by_cat"]:
                df_cat = pd.DataFrame(stats["by_cat"])
                df_cat.columns = ["Categoría", "Tickets"]
                fig = px.pie(df_cat, names="Categoría", values="Tickets",
                             title="Tickets por Categoría", hole=0.48,
                             color_discrete_sequence=["#3b82f6","#22c55e","#f59e0b",
                                                       "#a855f7","#ef4444","#14b8a6",
                                                       "#6366f1","#94a3b8"])
                fig.update_layout(height=360, margin=dict(t=40, b=10, l=0, r=0),
                                  font=dict(family="Inter"),
                                  legend=dict(orientation="v", x=1, y=0.5))
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            if stats["by_estado"]:
                df_est = pd.DataFrame(stats["by_estado"])
                df_est.columns = ["Estado", "Tickets"]
                color_map = {
                    "✅ Resuelto (Auto)": "#22c55e",
                    "⏳ Escalado a Marcos": "#ef4444",
                    "⏳ En cola": "#3b82f6",
                    "🔒 Derivado a RRHH": "#a855f7",
                    "⏳ Esperando aprobación": "#f59e0b",
                }
                colors = [color_map.get(e, "#94a3b8") for e in df_est["Estado"]]
                fig2 = go.Figure(go.Bar(
                    x=df_est["Estado"], y=df_est["Tickets"],
                    marker_color=colors, text=df_est["Tickets"],
                    textposition="outside",
                ))
                fig2.update_layout(
                    title="Tickets por Estado", height=360,
                    margin=dict(t=40, b=10), showlegend=False,
                    font=dict(family="Inter"),
                    xaxis=dict(tickangle=-15),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#f1f5f9"),
                )
                st.plotly_chart(fig2, use_container_width=True)

        # ── Charts row 2 ──
        if stats["by_dept"]:
            c3, c4 = st.columns([2, 3])
            with c3:
                st.subheader("🔥 Issues Más Comunes")
                df_top = pd.DataFrame(stats["by_cat"])
                if not df_top.empty:
                    df_top.columns = ["Categoría", "Tickets"]
                    df_top["% Total"] = (df_top["Tickets"] / total * 100).round(1).astype(str) + "%"
                    st.dataframe(df_top, use_container_width=True, hide_index=True)

            with c4:
                df_dept = pd.DataFrame(stats["by_dept"])
                df_dept.columns = ["Departamento", "Tickets"]
                fig3 = px.bar(df_dept, x="Tickets", y="Departamento",
                              orientation="h", title="Tickets por Departamento",
                              color="Tickets",
                              color_continuous_scale=["#dbeafe", "#3b82f6", "#1d4ed8"])
                fig3.update_layout(height=320, font=dict(family="Inter"),
                                   coloraxis_showscale=False,
                                   margin=dict(t=40, b=10, l=0, r=0),
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   paper_bgcolor="rgba(0,0,0,0)",
                                   xaxis=dict(gridcolor="#f1f5f9"))
                st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════
#  BASE DE CONOCIMIENTO
# ═══════════════════════════════════════════════════════════════════════
elif "Conocimiento" in menu:
    st.markdown('<div class="pg-title">🧠 Base de Conocimiento</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pg-sub">Artículos de soporte — escritos manualmente y aprendidos '
        'automáticamente de las conversaciones del chat.</div>',
        unsafe_allow_html=True,
    )

    kb_q = st.text_input("", placeholder="🔍  Buscar artículos… (contraseña, VPN, impresora…)",
                          label_visibility="collapsed")

    articles = search_kb(kb_q, top_k=20) if kb_q else get_all_articles()

    learned = sum(1 for a in get_all_articles()
                  if "learned" in a.get("source","") or "conv_" in a.get("source",""))
    manual = len(get_all_articles()) - learned

    m1, m2, m3 = st.columns(3)
    m1.metric("Total artículos", len(get_all_articles()))
    m2.metric("📘 Base manual", manual)
    m3.metric("🤖 Aprendidos por IA", learned)

    st.markdown("<br>", unsafe_allow_html=True)

    if not articles:
        st.info("No hay artículos que coincidan.")

    for a in articles:
        is_learned = "learned" in a.get("source", "") or "conv_" in a.get("source", "")
        src_label = "🤖 Aprendido" if is_learned else "📘 Base"
        src_color = "#7c3aed" if is_learned else "#2563eb"

        with st.expander(f"{src_label}  ·  **{a['titulo']}**  ·  {a['categoria']}"):
            colb, coli = st.columns([3, 1])
            with colb:
                st.markdown(a["body"])
            with coli:
                st.markdown(
                    f'<div style="font-size:12px;color:{src_color};font-weight:600;">{src_label}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Actualizado:** {a.get('updated','—')}")
                st.markdown(f"**Usos:** {a.get('times_used',0)}")
                if a.get("tags"):
                    tags_html = " ".join(f'<span class="kb-tag">{t}</span>' for t in a["tags"])
                    st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════
elif "Config" in menu:
    st.markdown('<div class="pg-title">⚙️ Configuración</div>', unsafe_allow_html=True)

    st.subheader("🤖 API de OpenAI")
    st.caption("Opcional. Sin API key el sistema usa clasificación por keywords (funcional para demo).")

    new_key = st.text_input("OpenAI API Key", type="password",
                             value=st.session_state.get("api_key", ""))
    if new_key != st.session_state.get("api_key", ""):
        st.session_state.api_key = new_key
        st.success("✅ Clave guardada para esta sesión.")

    if st.session_state.api_key:
        st.success("🤖 Modo IA activo — GPT-4o-mini para chat, clasificación y auto-aprendizaje.")
    else:
        st.info("🔑 Modo local activo — keywords para clasificación. Agrega tu API key para IA completa.")

    st.divider()
    st.subheader("📐 Arquitectura del Sistema")
    st.markdown("""
| Componente | Tecnología |
|---|---|
| UI / Frontend | Streamlit |
| Chat IA + RAG | OpenAI GPT-4o-mini (opcional) |
| Base de datos | **SQLite** (`novatech.db`) |
| Base de conocimiento | **Markdown** (estilo Obsidian) en `/knowledge/` |
| Auto-aprendizaje | Conversaciones → nuevos artículos KB |
| Clasificación offline | Keywords (sin dependencia de API) |
| Detección sensible | Local, nunca se envía a APIs externas |

**Flujo de auto-aprendizaje:**
```
Chat → Conversación guardada en SQLite
     → Cada 8 mensajes: GPT extrae problema+solución
     → Nuevo artículo .md creado en /knowledge/
     → Siguiente usuario con el mismo problema recibe mejor respuesta
```
    """)

    st.divider()
    st.subheader("🗃️ Datos")
    ca, cb = st.columns(2)
    with ca:
        if st.button("📥 Cargar datos demo", use_container_width=True):
            load_demo_data()
            st.success("✅ Datos demo cargados.")
    with cb:
        if st.button("🧹 Reset chat", use_container_width=True):
            st.session_state.conv_id = None
            st.session_state.chat_msgs = []
            st.session_state.last_ticket = None
            st.success("Chat reiniciado.")
