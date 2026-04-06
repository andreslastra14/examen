# 🎫 NovaTech - Sistema Inteligente de Tickets con IA

Sistema de gestión de tickets de soporte interno que utiliza IA para clasificar, priorizar y resolver automáticamente solicitudes comunes de TI.

## 🚀 Demo en vivo

**[Link a Streamlit Cloud aquí]**

## 📋 ¿Qué hace?

1. **Recepción de tickets** — Simula emails entrantes a soporte@novatech.com
2. **Clasificación automática por IA** — Categoriza y prioriza tickets usando GPT-4o-mini (o keywords como fallback)
3. **Resolución automática** — Resuelve tickets comunes (contraseñas, VPN, software, impresoras) con base de conocimiento
4. **Detección de contenido sensible** — Identifica tickets de RRHH y los rutea de forma confidencial
5. **Escalamiento inteligente** — Tickets complejos van a agentes humanos con contexto
6. **Dashboard de métricas** — Visualización para dirección (categorías, prioridades, oficinas, departamentos)

## 🛠️ Stack

| Componente | Tecnología |
|-----------|-----------|
| Frontend + Backend | Python + Streamlit |
| IA / LLM | OpenAI GPT-4o-mini (opcional, funciona sin API key con clasificación local) |
| Visualización | Plotly |
| Base de conocimiento | Basada en wiki de Marcos (~200 artículos Notion exportados) |

## ⚡ Cómo ejecutar

```bash
# 1. Clonar el repo
git clone https://github.com/[tu-usuario]/novatech-tickets-ia.git
cd novatech-tickets-ia

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional) Configurar OpenAI para clasificación con IA
export OPENAI_API_KEY=tu-api-key

# 4. Ejecutar
streamlit run app.py
```

## 🎮 Demo rápida

1. Ejecuta la app
2. Haz clic en **"🎮 Cargar datos demo"** en el sidebar
3. Explora el **Dashboard** para ver métricas
4. Crea un **Nuevo Ticket** para ver la clasificación en acción
5. Prueba un ticket sensible (ej: "necesito reportar acoso") para ver el routing a RRHH

## 📐 Decisiones de diseño

- **Sin API key requerida:** El sistema funciona con clasificación por keywords. Con API key, usa GPT-4o-mini para mayor precisión (~$15-30/mes para el volumen de NovaTech).
- **Detección de RRHH local:** Los tickets sensibles NUNCA se envían a APIs externas. Se detectan localmente por keywords antes de cualquier llamada a OpenAI.
- **Email como canal principal:** Lección de Freshdesk: la herramienta debe adaptarse al usuario, no al revés.
- **Base de conocimiento de Marcos:** La wiki existente en Notion (~200 artículos) se exporta a Markdown y se usa como fuente de respuestas automáticas.

## 📊 Métricas objetivo

| KPI | Meta |
|-----|------|
| Resolución automática | 30-50% |
| Tiempo de primera respuesta (IA) | < 5 min |
| Clasificación correcta | > 85% |
| Presupuesto mensual | < $500 USD |

## 🗺️ Roadmap

- [ ] Integración real con Gmail API (recepción automática de emails)
- [ ] RAG completo con wiki de Marcos exportada
- [ ] Notificaciones Slack para tickets críticos
- [ ] Flujos de aprobación automatizados
- [ ] Reportes mensuales automáticos para Patricia

---

**Construido para:** Evaluación Práctica — Analista de Automatización, Ternova Group
**Herramientas usadas:** Claude Code (arquitectura + código), Streamlit (frontend), OpenAI (clasificación IA)
