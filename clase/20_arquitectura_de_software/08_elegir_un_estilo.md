---
title: "Elegir un estilo"
---

# Elegir un estilo

## Tensión

Un compañero del curso, orgulloso de su proyecto, te escribe un mensaje:

> *"¿Qué arquitectura usarías para X?"*

Tienes dos formas de responder:

1. *"Event-driven. Es lo que se usa ahora."* — te tomó 2 segundos, suena profesional, y probablemente acabas de dar un mal consejo.
2. *"Depende. ¿Cuántas personas en el equipo? ¿Qué problema real están resolviendo? ¿Qué característica les va a doler perder? ¿Cuál es el budget operativo?"* — te va a tomar 15 minutos, va a sonar *menos* decidido, y probablemente vas a dar un consejo útil.

**¿Por qué las dos respuestas se ven tan distintas?**

---

## El patrón de razonamiento

La primera respuesta **no usa contexto**. Trata al estilo como **default**.

La segunda respuesta **pide contexto**. Trata al estilo como **conclusión** — resultado de preguntas que todavía no se hicieron.

Esa es la diferencia entre recomendar y razonar. Cualquier sistema puede defenderse con *"es lo que se usa"*. Solo los sistemas pensados tienen un **por qué** que no se desmorona cuando alguien lo examina.

El patrón: **pide el contexto antes de dar el estilo**. Si te presionan por una respuesta rápida, di que la estás dando rápida — y qué preguntas están sin responder.

---

## "Changing fashions" — el por qué del cuidado

El libro hace una observación honesta: los estilos arquitectónicos **van y vienen** como modas.

- **1970s** — monolitos
- **1980s** — cliente-servidor
- **1990s–2000s** — SOA orquestada con ESBs
- **2010s** — microservicios ("todo es un microservicio")
- **2020s** — modular monolith + microservicios cuidadosos + event-driven donde aplica

Cada onda llega con **promesas exageradas**. Cada onda deja **heridos**: sistemas construidos en la cresta que fueron rechazados al año siguiente cuando el consenso cambió.

### Conexión con la Ley 2 (*"Why > how"*)

Si construyes un sistema porque *"es lo que se usa"*, tu **por qué** es:

> *"porque en 2025 todos hablaban de esto"*

Eso no sobrevive al 2026. Lo que sobrevive es:

> *"porque este equipo de 8 personas, atendiendo este dominio, con esta presión de latencia, tenía este problema específico — y este estilo era la respuesta justificable."*

**El by why sobrevive a las modas. El how no.**

---

## El proceso de decisión — no un flowchart

Este módulo **no** te da un flowchart que tome tus inputs y saque un estilo. Tal flowchart sería mentira — la Ley 3 (*las decisiones viven en un espectro, no son binarias*) lo garantiza.

Te da un **proceso**: una secuencia de preguntas que tu equipo se hace a sí mismo, cuya respuesta define el estilo.

### Paso 1 — ¿Qué características priorizas?

Vuelve a la lección 03. Elige **3 a 7 características arquitectónicas** para este sistema.

- Si priorizas **time-to-market + simplicidad operativa** → apuntas a monolítico modular.
- Si priorizas **escalabilidad independiente + aislamiento de fallos + autonomía de equipos** → apuntas a microservicios.
- Si priorizas **desacople + modificabilidad + tolerancia de consumidores variables** → apuntas a event-driven.
- Si priorizas **extensibilidad de terceros** → apuntas a microkernel.
- Si priorizas **modularidad técnica con testabilidad** → apuntas a layered.

**Pero**: nombrar las características no basta. Los pasos 2 y 3 verifican si tu contexto soporta el estilo que apuntan.

### Paso 2 — ¿Qué forma tiene tu dominio?

Pregúntate:

- ¿El dominio es **coherente** (todo cambia junto) o **fragmentable** (partes cambian a ritmos distintos)?
- ¿Los **casos de uso** cruzan varias entidades o cada uno vive en una entidad?
- ¿Los datos son **relacionales profundos** (joins necesarios) o **documentos aislados** (cada documento se trata solo)?
- ¿Hay **interacción síncrona** crítica (usuario espera) o casi todo es asíncrono?

Un dominio coherente con interacciones síncronas empuja hacia **monolítico**. Un dominio fragmentado con flujos asíncronos empuja hacia **event-driven**.

### Paso 3 — ¿Qué forma tiene tu equipo?

Pregúntate:

- ¿Cuántos ingenieros?
- ¿Organizados como un equipo único o varios equipos independientes?
- ¿Qué tanta **madurez operativa**: ¿tienes CI/CD maduro? ¿tracing distribuido? ¿on-call? ¿observabilidad seria?
- ¿Cuánta **rotación** hay? ¿cuánto por cuánto dura una decisión antes de que cambie el equipo?
- ¿Qué tanta **experiencia** tiene el equipo con el estilo candidato?

Un equipo de 3 personas sin tracing distribuido con microservicios está firmando **su propio sufrimiento**. Un equipo de 60 personas con 6 sub-equipos independientes en un monolito va a **morir de conflictos de merge**.

#### Por qué el equipo está en la triangulación — Conway's Law

Esto no es casualidad. En 1968 Melvin Conway observó:

> *"Las organizaciones que diseñan sistemas están obligadas a producir diseños que reflejan las estructuras de comunicación de esas organizaciones."*

En palabras más directas: **tu sistema va a parecerse a tu organigrama, te guste o no**. Si tienes 4 equipos que casi no hablan, vas a construir 4 servicios que se hablan mal. Si tienes un solo equipo apretado, vas a construir una sola cosa compacta.

La variante activa de esta observación se llama **Inverse Conway Maneuver** (también conocida como **Team Topologies** después del libro de Skelton & Pais): en vez de luchar contra el efecto, **organiza el equipo primero** en la forma que quieres que tenga la arquitectura.

- ¿Quieres un modular monolith? Ten un equipo único de 5–10 personas que hablen todos los días.
- ¿Quieres microservicios con `auth`, `conversation`, `billing` separados? Ten 3 sub-equipos con ownership claro por dominio **antes** de escribir el primer servicio.

La triangulación no es *"considera al equipo al final"*. Es *"el equipo ya está proyectando la arquitectura que va a existir, haga o no el arquitecto su trabajo"*. Por eso está en los tres ejes, no como footnote.

### La triangulación

```
                   Características
                         ▲
                         │
                         │
                         ○  ← aquí es donde viven los estilos defendibles
                        / \
                       /   \
                      /     \
                     /       \
                    /         \
                   ▼           ▼
               Dominio        Equipo
```

**Los tres ejes tienen que alinearse para que el estilo funcione.**

- **Características sin dominio** → idealismo que no encaja.
- **Dominio sin equipo** → ambición que el equipo no puede operar.
- **Equipo sin características** → sistema técnicamente bonito que no sirve a nadie.
- **Los tres alineados** → un sistema que tiene chance.

---

## Un ejercicio con el chatbot

Vamos a aplicar el proceso al chatbot del curso, como si fueras el arquitecto.

### Paso 1 — características

Supongamos que elegimos (de la lección 03):

- time-to-market (2 meses hasta primera release)
- latencia p95 < 500ms
- modificabilidad (features nuevas cada semana)
- testabilidad
- simplicidad operativa (somos 3 personas)

### Paso 2 — dominio

- El chatbot es **coherente**: casi cada feature toca `auth`, `conversation`, `inference`.
- El **hot path** es síncrono (usuario escribe, espera, recibe).
- El modelo de datos es **medianamente acoplado** — conversaciones enlazan a usuarios, mensajes enlazan a conversaciones.
- Hay un componente asíncrono secundario (analytics), pero es minoritario.

### Paso 3 — equipo

- **3 personas**, todas full-stack.
- Ninguna experiencia operando microservicios en producción.
- CI/CD básico (GitHub Actions, un deploy). Sin tracing distribuido.

### El estilo que la triangulación sugiere

**Modular monolith.** La razón:

- **características** (time-to-market, simplicidad operativa) apuntan a un solo servicio
- **dominio** (coherente, síncrono, acoplado) apunta a un solo servicio
- **equipo** (3 personas, sin madurez en microservicios) no soporta distribución

Con una separación interna en 4 módulos (`auth`, `conversation`, `inference`, `billing`), el sistema queda preparado para *"si algún día duele suficiente, separamos"*.

**¿Es la única respuesta correcta?** No. Un equipo con experiencia fuerte en event-driven podría defender un pipeline de eventos internos. Otro equipo con compliance estricta podría defender separar `billing` desde el día uno. **Defender**, no *asumir*.

---

## Concepto nombrado

**Elegir un estilo** es un proceso de triangulación entre:

1. Las **características arquitectónicas** que priorizas (lección 03)
2. La **forma del dominio** que estás modelando
3. La **forma del equipo** que va a construir y operar

El proceso no da una respuesta única. Da **respuestas defendibles** — y esa defensa se escribe en un **ADR** (lección 04).

Las modas cambian cada década. El proceso sobrevive porque está construido sobre la Ley 2 (*why > how*) y la Ley 3 (*las decisiones viven en un espectro*).

---

## Pregunta del por qué

Vuelve al mensaje del compañero. Contéstate:

- Si fueras tú el que responde, ¿qué **3 preguntas** le harías antes de dar cualquier estilo?
- Si tu compañero insiste en una respuesta rápida, ¿qué le dices?
- Si en 6 meses tu recomendación resulta estar mal, ¿cómo quieres que se vea ese momento? ¿Defendible o arbitrario?

---

:::homework{id="20.3" title="Estilo para el chatbot + ADR completo" due="2026-05-05" points="20"}
Eres el arquitecto del chatbot del curso (equipo: 3 personas, timeline: 2 meses hasta primera release, usuarios: universitarios). Escribe el **ADR que justifica tu elección de estilo**.

### Formato

Usa **exactamente** la plantilla ADR de la lección 04 (7 secciones):

- Title
- Status
- Context (incluye al menos una **característica arquitectónica medible** y **una restricción de equipo**)
- Decision (una oración declarativa nombrando el estilo)
- Consequences (3 pros, 3 contras; al menos 1 contra tiene que vincularse a una característica que estás sacrificando)
- Governance (quién puede cambiarlo, cómo se supersede)
- Notes (los **otros 2 estilos que consideraste y descartaste**, con **una oración** de por qué cada uno)

### Restricciones

- Elige **uno** de los 5 estilos de la lección 06 (layered, modular monolith, pipeline, event-driven, microkernel). O microservicios (lección 07).
- La Decision debe ser **una oración**.
- La Context debe citar **la triangulación** (características / dominio / equipo).
- Descartar microservicios sin justificación **no** es válido — si descartas, defiende con contexto, no con "somos pocos".

### Grading

- **Trade-off explícito (30%)** — ¿Sacrificas algo medible? ¿Lo nombras?
- **Triangulación aplicada (30%)** — ¿Context cita los 3 ejes (características + dominio + equipo)?
- **Alternativas descartadas (20%)** — ¿Las 2 opciones en Notes tienen razón contextual, no genérica?
- **Legibilidad (20%)** — ¿Otro alumno puede leer tu ADR sin conocerte y entender la decisión?

No hay respuesta correcta de qué estilo elegir. El modular monolith es la elección más obvia para este contexto — si la defiendes bien, está bien. Si defiendes otra elección **con triangulación legible**, también está bien.
:::

---

## Cierre

Ya tienes el proceso. La última lección (09) es síntesis: un árbol de decisión en español que condensa todo lo anterior, una heat map de estilos × características, y un re-examen de tu respuesta del primer día (*"Una arquitectura es buena cuando..."*) con el vocabulario que ahora tienes.
