"""
Markdown-based knowledge base (estilo Obsidian).
Cada artículo es un .md con frontmatter YAML.
El sistema aprende automáticamente de las conversaciones.
"""
import re
from datetime import datetime
from pathlib import Path

KB_DIR = Path(__file__).parent / "knowledge"

_INITIAL: dict[str, dict] = {
    "contraseña": {
        "titulo": "Reset de Contraseña - Google Workspace",
        "categoria": "🔑 Reset de Contraseñas",
        "tags": ["contraseña", "password", "acceso", "correo", "login", "bloqueado"],
        "body": """## Pasos para restablecer tu contraseña

1. Ve a **accounts.google.com**
2. Clic en "¿Olvidaste tu contraseña?"
3. Ingresa tu correo corporativo `@novatech.com`
4. Selecciona el método de recuperación (teléfono o correo alternativo)
5. Crea una nueva contraseña (mín. 8 caracteres, incluye mayúsculas y números)

> **Si no te llega el código:** La cuenta puede estar bloqueada.
> Un agente de TI la desbloqueará manualmente — escribe a soporte@novatech.com

⏱️ Tiempo estimado: **5 minutos**""",
    },
    "vpn": {
        "titulo": "Configuración y Troubleshooting de VPN",
        "categoria": "🌐 VPN / Conectividad",
        "tags": ["vpn", "conectividad", "red", "internet", "wifi", "timeout", "home office"],
        "body": """## Si no puedes conectarte a la VPN

1. **Verifica tu internet** — abre cualquier página web
2. **Reinicia el cliente VPN** — ciérralo completamente y vuelve a abrir
3. **Credenciales** — usa tu usuario/contraseña de Google Workspace
4. **Windows:** Configuración → Red e Internet → VPN → Perfil NovaTech
5. **Mac:** Preferencias del Sistema → Red → VPN
6. Si persiste: reinicia tu equipo e intenta de nuevo

**Datos de conexión:**
| Campo | Valor |
|-------|-------|
| Servidor | vpn.novatech.com |
| Tipo | IKEv2 |
| Auth | Credenciales corporativas |

⏱️ Tiempo estimado: **10 minutos**""",
    },
    "software": {
        "titulo": "Instalación de Software Aprobado",
        "categoria": "💻 Software",
        "tags": ["software", "instalar", "programa", "aplicación", "app", "aprobación"],
        "body": """## Software que puedes instalar sin aprobación

Chrome · Slack · Zoom · VS Code · Postman · Figma · Office 365 · Notion · Docker

**Pasos:**
1. Descarga desde el sitio oficial del software
2. Ejecuta el instalador (clic derecho → "Ejecutar como administrador" si pide)
3. Si solicita permisos elevados, contacta a TI primero

## Software que requiere aprobación

Envía solicitud a **soporte@novatech.com** con:
- Nombre del software
- Para qué lo usarás
- Si tiene costo (incluye precio)

⏱️ Aprobación: **1-3 días hábiles**""",
    },
    "impresora": {
        "titulo": "Problemas Comunes de Impresora",
        "categoria": "🖨️ Impresoras",
        "tags": ["impresora", "imprimir", "impresión", "escáner", "scanner", "papel", "tóner"],
        "body": """## Troubleshooting básico

1. **Verifica que esté encendida** y conectada a la red WiFi
2. **Reinicia la cola de impresión:**
   - *Windows:* Win+R → `services.msc` → "Print Spooler" → Reiniciar
   - *Mac:* Preferencias del Sistema → Impresoras → Eliminar y volver a agregar
3. **Verifica papel y tóner** — suministros en gabinete de cada piso
4. **Reinstala el driver** — disponible en la intranet IT

> Si nada funciona, probablemente sea hardware. Crea un ticket para visita técnica.

⏱️ Tiempo estimado: **15 minutos**""",
    },
    "permisos": {
        "titulo": "Solicitud de Permisos de Acceso",
        "categoria": "🔐 Permisos de Acceso",
        "tags": ["permiso", "acceso", "carpeta", "drive", "compartir", "folder", "proyecto"],
        "body": """## Cómo solicitar acceso a recursos compartidos

**Google Drive / Carpetas:**
1. Identifica el correo del propietario del recurso (tu jefe directo)
2. Pide que te comparta directamente desde Drive
3. Si no tienes contacto, envía ticket con: nombre de la carpeta + nombre de tu jefe

**Permisos de sistemas internos:**
- Requiere aprobación del director del área
- El proceso toma 1-2 días hábiles

> Para accesos de emergencia, escala directamente a Marcos Solís.

⏱️ Tiempo estimado: **1-2 días hábiles**""",
    },
    "hardware": {
        "titulo": "Problemas de Hardware - Diagnóstico Básico",
        "categoria": "🖱️ Hardware",
        "tags": ["mouse", "teclado", "monitor", "pantalla", "hardware", "cable", "cargador", "dispositivo"],
        "body": """## Diagnóstico rápido de hardware

**Mouse / Teclado inalámbrico:**
- Cambia las baterías (aunque parezca que duran)
- Prueba el receptor USB en otro puerto
- Acerca el receptor al dispositivo

**Monitor / Pantalla:**
- Verifica que el cable (HDMI/DisplayPort) esté bien conectado
- Prueba con otro cable
- Detectar pantalla: clic derecho escritorio → "Configuración de pantalla" → Detectar

**Laptop no carga:**
- Prueba con otro tomacorriente
- Verifica que el conector no esté doblado
- Si es recurrente, solicita revisión técnica

> Para reemplazo de hardware, se requiere aprobación de tu director.

⏱️ Visita técnica: **mismo día si es urgente**""",
    },
}


def _path(key: str) -> Path:
    return KB_DIR / f"{key}.md"


def _write(key: str, titulo: str, categoria: str, tags: list[str],
           body: str, source: str = "manual", times_used: int = 0):
    KB_DIR.mkdir(exist_ok=True)
    tags_str = ", ".join(tags)
    text = (
        f"---\n"
        f"titulo: {titulo}\n"
        f"categoria: {categoria}\n"
        f"tags: {tags_str}\n"
        f"source: {source}\n"
        f"times_used: {times_used}\n"
        f"updated: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"---\n\n"
        f"# {titulo}\n\n"
        f"{body}\n"
    )
    _path(key).write_text(text, encoding="utf-8")


def _parse(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    fm: dict = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
            body = parts[2].strip()
    # strip the repeated h1 title from body display
    body = re.sub(r"^# .+\n\n?", "", body)
    return {
        "key": path.stem,
        "titulo": fm.get("titulo", path.stem),
        "categoria": fm.get("categoria", "📦 Otros"),
        "tags": [t.strip() for t in fm.get("tags", "").split(",") if t.strip()],
        "source": fm.get("source", "manual"),
        "times_used": int(fm.get("times_used", 0) or 0),
        "updated": fm.get("updated", ""),
        "body": body.strip(),
    }


def init_kb():
    KB_DIR.mkdir(exist_ok=True)
    for key, data in _INITIAL.items():
        if not _path(key).exists():
            _write(key, data["titulo"], data["categoria"], data["tags"], data["body"])


def get_all_articles() -> list[dict]:
    KB_DIR.mkdir(exist_ok=True)
    return [_parse(p) for p in sorted(KB_DIR.glob("*.md"))]


def search_kb(query: str, top_k: int = 3) -> list[dict]:
    words = query.lower().split()
    scored = []
    for a in get_all_articles():
        text = " ".join([a["titulo"], " ".join(a["tags"]), a["body"]]).lower()
        score = sum(text.count(w) for w in words)
        if score:
            scored.append((score, a))
    scored.sort(key=lambda x: -x[0])
    return [a for _, a in scored[:top_k]]


def format_for_context(articles: list[dict]) -> str:
    if not articles:
        return ""
    lines = ["## Base de Conocimiento NovaTech\n"]
    for a in articles:
        lines.append(f"### {a['titulo']} ({a['categoria']})\n{a['body']}\n")
    return "\n".join(lines)


def add_learned_article(titulo: str, categoria: str, tags: list[str],
                        contenido: str, conversation_id: str) -> str:
    key = "learned_" + re.sub(r"[^a-z0-9]", "_", titulo.lower())[:35]
    # append if exists
    if _path(key).exists():
        existing = _parse(_path(key))
        merged = existing["body"] + f"\n\n---\n*Actualizado — conv. `{conversation_id[:8]}`*\n\n{contenido}"
        _write(key, existing["titulo"], existing["categoria"], existing["tags"],
               merged, source="learned", times_used=existing["times_used"])
    else:
        _write(key, titulo, categoria, tags, contenido,
               source=f"conv_{conversation_id[:8]}")
    return key


def increment_usage(key: str):
    if _path(key).exists():
        a = _parse(_path(key))
        _write(key, a["titulo"], a["categoria"], a["tags"],
               a["body"], a["source"], a["times_used"] + 1)
