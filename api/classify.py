from http.server import BaseHTTPRequestHandler
import json
import os

SENSITIVE_KEYWORDS = [
    "acoso", "hostigamiento", "discriminación", "denuncia", "abuso",
    "discapacidad", "adaptación", "embarazo", "despido injustificado",
    "amenaza", "violencia", "sexual", "intimidación", "mobbing",
    "represalia", "confidencial rrhh", "recursos humanos confidencial"
]

def detect_sensitive(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in SENSITIVE_KEYWORDS)

def classify_local(subject, body):
    text = f"{subject} {body}".lower()
    critical_kw = ["servidor caído", "servidor de producción", "se cayó", "brecha de seguridad", "hackearon", "ransomware"]
    if any(kw in text for kw in critical_kw):
        return {"categoria": "Servidor/Infraestructura", "prioridad": "Crítica", "confianza": 95, "auto_resolvable": False, "emoji_cat": "🖥️", "emoji_pri": "🔴"}
    if any(kw in text for kw in ["contraseña", "password", "clave", "no puedo entrar", "acceso bloqueado", "login"]):
        return {"categoria": "Reset de Contraseñas", "prioridad": "Baja", "confianza": 90, "auto_resolvable": True, "kb_key": "password", "emoji_cat": "🔑", "emoji_pri": "🟢"}
    if any(kw in text for kw in ["vpn", "conectividad", "red", "internet", "wifi", "conexión"]):
        return {"categoria": "VPN / Conectividad", "prioridad": "Media", "confianza": 85, "auto_resolvable": True, "kb_key": "vpn", "emoji_cat": "🌐", "emoji_pri": "🟡"}
    if any(kw in text for kw in ["instalar", "software", "programa", "aplicación", "actualizar", "app"]):
        return {"categoria": "Software", "prioridad": "Media", "confianza": 80, "auto_resolvable": True, "kb_key": "software", "emoji_cat": "💻", "emoji_pri": "🟡"}
    if any(kw in text for kw in ["permiso", "acceso", "carpeta", "compartir", "drive", "folder"]):
        return {"categoria": "Permisos de Acceso", "prioridad": "Media", "confianza": 80, "auto_resolvable": False, "emoji_cat": "🔐", "emoji_pri": "🟡"}
    if any(kw in text for kw in ["mouse", "teclado", "monitor", "pantalla", "hardware", "cable"]):
        return {"categoria": "Hardware", "prioridad": "Baja", "confianza": 85, "auto_resolvable": False, "emoji_cat": "🖱️", "emoji_pri": "🟢"}
    if any(kw in text for kw in ["impresora", "imprimir", "impresión", "escáner"]):
        return {"categoria": "Impresoras", "prioridad": "Baja", "confianza": 80, "auto_resolvable": True, "kb_key": "printer", "emoji_cat": "🖨️", "emoji_pri": "🟢"}
    return {"categoria": "Otros", "prioridad": "Media", "confianza": 50, "auto_resolvable": False, "emoji_cat": "📦", "emoji_pri": "🟡"}

def classify_with_ai(subject, body):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return classify_local(subject, body)
    try:
        import urllib.request
        data = json.dumps({
            "model": "gpt-4o-mini",
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": 'Clasifica este ticket de soporte TI en JSON: {"categoria": "Reset de Contraseñas|VPN / Conectividad|Software|Permisos de Acceso|Hardware|Impresoras|Servidor/Infraestructura|Otros", "prioridad": "Crítica|Alta|Media|Baja", "confianza": 0-100, "auto_resolvable": bool, "kb_key": "password|vpn|software|printer|null"}'},
                {"role": "user", "content": f"Asunto: {subject}\nContenido: {body}"}
            ]
        }).encode()
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        resp = urllib.request.urlopen(req)
        result = json.loads(json.loads(resp.read())["choices"][0]["message"]["content"])
        emoji_cat_map = {"Reset de Contraseñas": "🔑", "VPN / Conectividad": "🌐", "Software": "💻", "Permisos de Acceso": "🔐", "Hardware": "🖱️", "Impresoras": "🖨️", "Servidor/Infraestructura": "🖥️", "Otros": "📦"}
        emoji_pri_map = {"Crítica": "🔴", "Alta": "🟠", "Media": "🟡", "Baja": "🟢"}
        result["emoji_cat"] = emoji_cat_map.get(result.get("categoria", ""), "📦")
        result["emoji_pri"] = emoji_pri_map.get(result.get("prioridad", ""), "🟡")
        return result
    except:
        return classify_local(subject, body)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        subject = body.get("subject", "")
        content = body.get("body", "")
        is_sensitive = detect_sensitive(f"{subject} {content}")
        if is_sensitive:
            result = {"categoria": "RRHH - CONFIDENCIAL", "prioridad": "Crítica", "confianza": 99, "auto_resolvable": False, "sensible": True, "emoji_cat": "🚨", "emoji_pri": "🔴"}
        else:
            result = classify_with_ai(subject, content)
            result["sensible"] = False
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
