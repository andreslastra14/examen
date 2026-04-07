"""
Motor de IA: chat con RAG sobre KB, clasificación local, extracción de tickets
y auto-aprendizaje desde conversaciones.
"""
import json
import os
import re

import streamlit as st

from knowledge_base import search_kb, format_for_context

SENSITIVE_KW = [
    "acoso", "hostigamiento", "discriminación", "denuncia", "abuso",
    "embarazo", "despido injustificado", "amenaza", "violencia",
    "sexual", "intimidación", "mobbing", "represalia", "rrhh confidencial",
]

CATEGORIES = [
    "🔑 Reset de Contraseñas", "🌐 VPN / Conectividad", "💻 Software",
    "🔐 Permisos de Acceso", "🖱️ Hardware", "🖨️ Impresoras",
    "🖥️ Servidor/Infraestructura", "📦 Otros",
]


def is_sensitive(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in SENSITIVE_KW)


def _client():
    key = os.environ.get("OPENAI_API_KEY") or st.session_state.get("api_key", "")
    if not key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=key)
    except Exception:
        return None


# ── Clasificación local por keywords ─────────────────────────────────

def classify_local(text: str) -> dict:
    t = text.lower()
    if any(k in t for k in ["servidor caído", "producción caída", "brecha", "ransomware", "hackearon"]):
        return {"categoria": "🖥️ Servidor/Infraestructura", "prioridad": "🔴 Crítica",
                "confianza": 95, "auto_resolvable": False}
    if any(k in t for k in ["contraseña", "password", "clave", "no puedo entrar", "bloqueado", "login"]):
        return {"categoria": "🔑 Reset de Contraseñas", "prioridad": "🟢 Baja",
                "confianza": 90, "auto_resolvable": True, "kb_key": "contraseña"}
    if any(k in t for k in ["vpn", "conectividad", "red", "internet", "wifi", "timeout", "conexión"]):
        return {"categoria": "🌐 VPN / Conectividad", "prioridad": "🟡 Media",
                "confianza": 85, "auto_resolvable": True, "kb_key": "vpn"}
    if any(k in t for k in ["instalar", "software", "programa", "aplicación", "app", "actualizar"]):
        return {"categoria": "💻 Software", "prioridad": "🟡 Media",
                "confianza": 80, "auto_resolvable": True, "kb_key": "software"}
    if any(k in t for k in ["impresora", "imprimir", "impresión", "escáner", "scanner"]):
        return {"categoria": "🖨️ Impresoras", "prioridad": "🟢 Baja",
                "confianza": 80, "auto_resolvable": True, "kb_key": "impresora"}
    if any(k in t for k in ["permiso", "acceso", "carpeta", "drive", "folder", "compartir"]):
        return {"categoria": "🔐 Permisos de Acceso", "prioridad": "🟡 Media",
                "confianza": 80, "auto_resolvable": True, "kb_key": "permisos"}
    if any(k in t for k in ["mouse", "teclado", "monitor", "pantalla", "hardware", "cable", "cargador"]):
        return {"categoria": "🖱️ Hardware", "prioridad": "🟢 Baja",
                "confianza": 85, "auto_resolvable": True, "kb_key": "hardware"}
    return {"categoria": "📦 Otros", "prioridad": "🟡 Media", "confianza": 50, "auto_resolvable": False}


# ── Chat con RAG ──────────────────────────────────────────────────────

_SYSTEM = """Eres **Nova**, asistente de soporte TI de NovaTech Solutions (México, 200 empleados).

Tu misión: resolver problemas técnicos de forma rápida, empática y clara.

Reglas:
- Responde siempre en **español**
- Usa formato Markdown (negrita, listas, código)
- Sé conciso: máx. 250 palabras visibles
- Si puedes resolver con la KB, da pasos numerados
- Si necesitas más info, haz UNA sola pregunta
- Si el problema requiere un humano, dilo claramente

Al **final** de cada respuesta, incluye exactamente este bloque (sin excepción):
```json
{{"generar_ticket": <true|false>, "categoria": "<categoria>", "prioridad": "<🔴 Crítica|🟠 Alta|🟡 Media|🟢 Baja>", "asunto_sugerido": "<texto corto>"}}
```
Genera ticket=true solo si: el problema no se pudo resolver en el chat, necesita seguimiento humano, o es un incidente crítico.

{kb_context}"""


def chat_response(history: list[dict], user_text: str) -> str:
    relevant = search_kb(user_text)
    kb_ctx = format_for_context(relevant)
    system = _SYSTEM.format(kb_context=kb_ctx)

    cl = _client()
    if not cl:
        return _fallback(user_text, relevant)

    messages = [{"role": "system", "content": system}]
    for m in history[-12:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_text})

    try:
        resp = cl.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.25,
            max_tokens=700,
        )
        return resp.choices[0].message.content
    except Exception:
        return _fallback(user_text, relevant)


def _fallback(text: str, articles: list[dict]) -> str:
    if articles:
        a = articles[0]
        cat = a["categoria"]
        cl_data = classify_local(text)
        pri = cl_data.get("prioridad", "🟡 Media")
        needs_ticket = not cl_data.get("auto_resolvable", False)
        ticket_json = json.dumps({
            "generar_ticket": needs_ticket,
            "categoria": cat,
            "prioridad": pri,
            "asunto_sugerido": a["titulo"],
        }, ensure_ascii=False)
        return (
            f"Encontré información relevante:\n\n"
            f"**{a['titulo']}**\n\n{a['body']}\n\n"
            f"---\n*¿Esto resolvió tu problema? Si no, puedo crear un ticket.*\n\n"
            f"```json\n{ticket_json}\n```"
        )

    ticket_json = json.dumps({
        "generar_ticket": True,
        "categoria": "📦 Otros",
        "prioridad": "🟡 Media",
        "asunto_sugerido": text[:60],
    }, ensure_ascii=False)
    return (
        "No encontré información específica en nuestra KB para tu consulta.\n\n"
        "Puedo crear un ticket para que un agente de TI te ayude. "
        "¿Te parece bien?\n\n"
        f"```json\n{ticket_json}\n```"
    )


# ── Extracción de ticket desde respuesta ──────────────────────────────

def extract_ticket_decision(response: str) -> dict | None:
    match = re.search(r"```json\s*(\{[^`]+\})\s*```", response, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except Exception:
        return None


def clean_response(response: str) -> str:
    """Elimina el bloque JSON de la respuesta visible al usuario."""
    return re.sub(r"```json\s*\{[^`]+\}\s*```", "", response, flags=re.DOTALL).strip()


# ── Auto-aprendizaje ──────────────────────────────────────────────────

def extract_learning(messages: list[dict]) -> dict | None:
    """
    Analiza una conversación y extrae un artículo KB si es útil.
    Requiere API key.
    """
    cl = _client()
    if not cl or len(messages) < 4:
        return None

    history = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)

    try:
        resp = cl.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": (
                    "Analiza esta conversación de soporte TI y extrae conocimiento reutilizable.\n"
                    "Responde en JSON:\n"
                    '{"vale_guardar": true/false, '
                    '"titulo": "...", "categoria": "...", '
                    '"tags": ["..."], "contenido": "markdown con problema y solución"}\n'
                    "vale_guardar=true solo si hay solución clara y reutilizable."
                )},
                {"role": "user", "content": history},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return None
