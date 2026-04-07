"""
SQLite persistence layer — tickets, conversations, messages.
"""
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "novatech.db"


def _conn():
    c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tickets (
            id          TEXT PRIMARY KEY,
            fecha       TEXT NOT NULL,
            remitente   TEXT DEFAULT '',
            departamento TEXT DEFAULT '',
            oficina     TEXT DEFAULT '',
            asunto      TEXT DEFAULT '',
            cuerpo      TEXT DEFAULT '',
            categoria   TEXT DEFAULT '',
            prioridad   TEXT DEFAULT '',
            confianza   INTEGER DEFAULT 0,
            estado      TEXT DEFAULT '⏳ En cola',
            auto_resolvable INTEGER DEFAULT 0,
            sensible    INTEGER DEFAULT 0,
            origen      TEXT DEFAULT 'manual',
            conversation_id TEXT,
            kb_key      TEXT,
            respuesta_auto TEXT
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id          TEXT PRIMARY KEY,
            departamento TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            resolved    INTEGER DEFAULT 0,
            ticket_id   TEXT,
            resolution  TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role            TEXT NOT NULL,
            content         TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );
        """)


# ── Tickets ───────────────────────────────────────────────────────────

def save_ticket(t: dict) -> str:
    tid = t.get("id") or f"TK-{str(uuid.uuid4())[:6].upper()}"
    with _conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO tickets
            (id,fecha,remitente,departamento,oficina,asunto,cuerpo,
             categoria,prioridad,confianza,estado,auto_resolvable,
             sensible,origen,conversation_id,kb_key,respuesta_auto)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            tid,
            t.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M")),
            t.get("remitente", ""),
            t.get("departamento", ""),
            t.get("oficina", ""),
            t.get("asunto", ""),
            t.get("cuerpo", ""),
            t.get("categoria", ""),
            t.get("prioridad", ""),
            int(t.get("confianza", 0)),
            t.get("estado", "⏳ En cola"),
            1 if t.get("auto_resolvable") else 0,
            1 if t.get("sensible") else 0,
            t.get("origen", "manual"),
            t.get("conversation_id"),
            t.get("kb_key"),
            t.get("respuesta_auto"),
        ))
    return tid


def get_tickets(estado=None, prioridad=None, categoria=None,
                oficina=None, search=None) -> list[dict]:
    q = "SELECT * FROM tickets WHERE 1=1"
    p: list = []

    def _in(field, vals):
        nonlocal q, p
        if vals:
            q += f" AND {field} IN ({','.join(['?']*len(vals))})"
            p.extend(vals)

    _in("estado", estado)
    _in("prioridad", prioridad)
    _in("categoria", categoria)
    _in("oficina", oficina)

    if search:
        q += " AND (asunto LIKE ? OR cuerpo LIKE ? OR remitente LIKE ?)"
        p += [f"%{search}%"] * 3

    q += " ORDER BY fecha DESC"
    with _conn() as c:
        return [dict(r) for r in c.execute(q, p).fetchall()]


def update_ticket_status(ticket_id: str, estado: str):
    with _conn() as c:
        c.execute("UPDATE tickets SET estado=? WHERE id=?", (estado, ticket_id))


# ── Conversations & Messages ──────────────────────────────────────────

def start_conversation(departamento: str = "") -> str:
    cid = str(uuid.uuid4())
    with _conn() as c:
        c.execute(
            "INSERT INTO conversations (id, departamento, created_at) VALUES (?,?,?)",
            (cid, departamento, datetime.now().isoformat()),
        )
    return cid


def add_message(conv_id: str, role: str, content: str):
    with _conn() as c:
        c.execute(
            "INSERT INTO messages (conversation_id,role,content,created_at) VALUES (?,?,?,?)",
            (conv_id, role, content, datetime.now().isoformat()),
        )


def get_messages(conv_id: str) -> list[dict]:
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id",
            (conv_id,),
        ).fetchall()]


def resolve_conversation(conv_id: str, ticket_id: str = None, resolution: str = ""):
    with _conn() as c:
        c.execute(
            "UPDATE conversations SET resolved=1, ticket_id=?, resolution=? WHERE id=?",
            (ticket_id, resolution, conv_id),
        )


# ── Analytics ─────────────────────────────────────────────────────────

def get_stats() -> dict:
    with _conn() as c:
        total     = c.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        auto      = c.execute("SELECT COUNT(*) FROM tickets WHERE auto_resolvable=1").fetchone()[0]
        criticos  = c.execute("SELECT COUNT(*) FROM tickets WHERE prioridad LIKE '%Crítica%'").fetchone()[0]
        sensibles = c.execute("SELECT COUNT(*) FROM tickets WHERE sensible=1").fetchone()[0]
        chat_orig = c.execute("SELECT COUNT(*) FROM tickets WHERE origen='chat'").fetchone()[0]

        by_cat = [dict(r) for r in c.execute(
            "SELECT categoria, COUNT(*) cnt FROM tickets WHERE sensible=0 GROUP BY categoria ORDER BY cnt DESC"
        ).fetchall()]
        by_estado = [dict(r) for r in c.execute(
            "SELECT estado, COUNT(*) cnt FROM tickets GROUP BY estado"
        ).fetchall()]
        by_dept = [dict(r) for r in c.execute(
            "SELECT departamento, COUNT(*) cnt FROM tickets WHERE sensible=0 "
            "AND departamento != '' GROUP BY departamento ORDER BY cnt DESC LIMIT 8"
        ).fetchall()]

    return dict(total=total, auto=auto, criticos=criticos,
                sensibles=sensibles, chat_orig=chat_orig,
                by_cat=by_cat, by_estado=by_estado, by_dept=by_dept)


# ── Demo data ─────────────────────────────────────────────────────────

def load_demo_data():
    if get_tickets():
        return  # ya existen datos

    now = datetime.now
    demos = [
        {"id": "TK-001",
         "fecha": (now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
         "remitente": "carlos.ruiz@novatech.com", "departamento": "Ventas", "oficina": "Guadalajara",
         "asunto": "No puedo entrar a mi correo",
         "cuerpo": "Desde ayer no puedo acceder. Creo que olvidé mi contraseña y no llega el código.",
         "categoria": "🔑 Reset de Contraseñas", "prioridad": "🟢 Baja",
         "confianza": 92, "estado": "✅ Resuelto (Auto)", "auto_resolvable": True,
         "kb_key": "contraseña", "origen": "demo"},
        {"id": "TK-002",
         "fecha": (now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
         "remitente": "ana.lopez@novatech.com", "departamento": "Administración", "oficina": "Guadalajara",
         "asunto": "La VPN no conecta desde casa",
         "cuerpo": "Intento conectarme a la VPN desde home office y me da error de timeout.",
         "categoria": "🌐 VPN / Conectividad", "prioridad": "🟡 Media",
         "confianza": 88, "estado": "✅ Resuelto (Auto)", "auto_resolvable": True,
         "kb_key": "vpn", "origen": "demo"},
        {"id": "TK-003",
         "fecha": (now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
         "remitente": "roberto.diaz@novatech.com", "departamento": "Desarrollo", "oficina": "Monterrey",
         "asunto": "Se cayó el servidor de staging",
         "cuerpo": "El servidor no responde hace 30 minutos. Tenemos entrega con cliente mañana.",
         "categoria": "🖥️ Servidor/Infraestructura", "prioridad": "🔴 Crítica",
         "confianza": 96, "estado": "⏳ Escalado a Marcos", "auto_resolvable": False, "origen": "demo"},
        {"id": "TK-004",
         "fecha": (now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
         "remitente": "laura.martinez@novatech.com", "departamento": "Diseño", "oficina": "Monterrey",
         "asunto": "Necesito acceso a carpeta del proyecto Alfa",
         "cuerpo": "Me cambiaron de proyecto y necesito acceso al Drive del proyecto Alfa.",
         "categoria": "🔐 Permisos de Acceso", "prioridad": "🟡 Media",
         "confianza": 85, "estado": "⏳ Esperando aprobación", "auto_resolvable": False, "origen": "demo"},
        {"id": "TK-005",
         "fecha": (now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
         "remitente": "maria.garcia@novatech.com", "departamento": "QA", "oficina": "Monterrey",
         "asunto": "Quiero instalar Postman",
         "cuerpo": "Necesito Postman para testing de APIs. ¿Me pueden ayudar con la instalación?",
         "categoria": "💻 Software", "prioridad": "🟢 Baja",
         "confianza": 90, "estado": "✅ Resuelto (Auto)", "auto_resolvable": True,
         "kb_key": "software", "origen": "demo"},
        {"id": "TK-006",
         "fecha": (now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"),
         "remitente": "pedro.sanchez@novatech.com", "departamento": "Ventas", "oficina": "Guadalajara",
         "asunto": "Mouse inalámbrico no funciona",
         "cuerpo": "El mouse dejó de responder. Ya cambié baterías y sigue sin funcionar.",
         "categoria": "🖱️ Hardware", "prioridad": "🟢 Baja",
         "confianza": 88, "estado": "⏳ En cola", "auto_resolvable": False, "origen": "demo"},
        {"id": "TK-007",
         "fecha": now().strftime("%Y-%m-%d %H:%M"),
         "remitente": "empleado.anonimo@novatech.com", "departamento": "—", "oficina": "—",
         "asunto": "Situación personal delicada",
         "cuerpo": "[CONTENIDO OCULTO POR PRIVACIDAD]",
         "categoria": "🚨 RRHH - CONFIDENCIAL", "prioridad": "🔴 Crítica",
         "confianza": 99, "estado": "🔒 Derivado a RRHH", "auto_resolvable": False,
         "sensible": True, "origen": "demo"},
    ]
    for d in demos:
        save_ticket(d)
