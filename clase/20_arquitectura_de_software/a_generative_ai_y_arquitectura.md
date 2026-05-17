---
title: "Apéndice — IA generativa y arquitectura"
---

# Apéndice — IA generativa y arquitectura

> Esta lección es un **apéndice** — no forma parte del flujo principal de las dos clases. Cubre el capítulo 26 de la 2ª edición de Richards & Ford (nuevo en esa edición) que discute explícitamente el papel de los LLMs en decisiones arquitectónicas. Es especialmente relevante para el ciclo 2026, donde la mitad de los equipos de software están integrando Gen AI en sus sistemas.

---

## Tensión

Dos conversaciones distintas, el mismo equipo:

- **Lunes**: *"Necesitamos meter un LLM en el chatbot para resumir conversaciones largas."* — una decisión sobre **integrar IA en la arquitectura**.
- **Viernes**: *"Le pregunté a GPT si usar microservicios o monolito modular para esto. Me dijo microservicios."* — una decisión sobre **usar IA para decidir la arquitectura**.

Las dos suenan parecido. Las dos mencionan *"IA"* y *"arquitectura"*. Pero requieren pensar **muy distinto**:

- La primera es una **decisión arquitectónica como cualquier otra** (trade-offs, ADR, características). Lo único nuevo es que el componente que integras es un LLM.
- La segunda es un **cambio de proceso**: estás delegando juicio a un modelo que carece del contexto específico de tu equipo, dominio, presupuesto, y presión.

Si confundes las dos, vas a tomar decisiones malas por la razón equivocada.

---

## Parte 1 — Integrar IA generativa **en** una arquitectura

### El patrón de razonamiento

Cuando agregas un LLM como componente (resumir, clasificar, generar texto, asistir al usuario), aplican **todas** las herramientas que aprendiste en el módulo:

- Es una decisión arquitectónica → requiere **ADR** (lección 04).
- Tiene trade-offs → se mide contra **características** (lección 03).
- Tiene **falacias de distribuido** particulares (lección 05).
- Se integra como un **bounded context** o quantum distinto (lección 07).

Lo **nuevo** es un conjunto de consideraciones específicas de LLMs:

#### 1. Reemplazabilidad del modelo

Los modelos cambian cada 6–12 meses: GPT-4 → GPT-4o → Claude 3.5 → Llama 3. Tu arquitectura debe permitir cambiar el modelo **sin rediseño**.

Consecuencia: **abstrae el modelo detrás de una interfaz**. No llames directamente a `openai.ChatCompletion.create()` desde tu código de negocio. Pon un `LLMProvider` adelante y cambia el backend sin tocar el código que lo consume. Es el mismo patrón que *"no llamas directo a Postgres desde tu controller"*.

#### 2. Rails (barandillas)

Un LLM puede devolverte **cualquier cosa**: texto inesperado, JSON malformado, contenido que viola compliance, instrucciones disfrazadas (*prompt injection*). Tu arquitectura necesita rails **en la salida**:

- validación de schema (¿el JSON matchea la forma esperada?)
- filtros de contenido (¿hay PII que no debería fluir?)
- límites de tokens / costo por llamada
- detección de respuestas evasivas o hallucinadas

Sin rails, estás acoplando la correctitud de tu sistema al capricho de un modelo.

#### 3. Evals (evaluaciones)

El modelo funciona hoy. Mañana actualiza, y las respuestas empeoran silenciosamente. Necesitas un **pipeline de evaluación continuo**:

- un set de prompts representativos con respuesta esperada
- métricas (precisión, latencia, costo, toxicidad, adherencia al schema)
- re-ejecución automática cuando cambias modelo, prompt, o tooling
- dashboards (herramientas como Langfuse, Helicone, Phoenix facilitan esto)

Sin evals, **no sabes** si tu sistema está mejor o peor que ayer. La falacia 11 (*"observability is optional"*) es especialmente tóxica con LLMs.

#### 4. Costo y latencia son **primera clase**

- Un modelo cloud típico cuesta ~$0.5–15 por **millón de tokens**. Para un chatbot con 100k usuarios, eso es **cientos a miles de dólares al mes**, altamente variable.
- Latencia típica: 500ms–5s por request. Tu p95 vive ahí.

Si tu ADR para *"integrar LLM para resumir"* no cuantifica **costo por usuario** y **latencia esperada**, no es un ADR — es un anuncio.

### El quantum de un LLM

Piensa el LLM como **un quantum externo** (lección 07). No es tuyo: lo operan otros, cambia en ciclos fuera de tu control, falla de forma no-determinística, y tiene sus propias características operativas (latencia, disponibilidad, cuota).

Consecuencia arquitectónica: trata al LLM con la misma disciplina que tratas a un servicio externo crítico — circuit breakers, timeouts agresivos, fallbacks (¿qué haces si el LLM está caído? ¿respuesta degradada? ¿cache de respuestas pasadas? ¿cola?).

---

## Parte 2 — Usar IA generativa **como asistente** del arquitecto

### El patrón de razonamiento

Le preguntas a un LLM: *"¿Debo usar orquestación o coreografía para este workflow?"*

El LLM te da una respuesta que suena informada. Richards & Ford fueron honestos sobre el resultado: **hoy (2025), esa respuesta raramente es correcta**. No por falta de conocimiento del modelo — **por falta de contexto**.

La cita del libro, condensada:

> *"Los LLMs son excelentes para entender conocimiento, pero hasta ahora les falta la sabiduría para tomar decisiones apropiadas. Esa sabiduría incluye tanto contexto que es más rápido para el arquitecto resolver el problema de negocio él mismo, que enseñarle al LLM todo el problema y su entorno extendido."*

### Por qué esto se conecta con la Ley 1

Toda decisión arquitectónica es un **trade-off** (Ley 1). El trade-off se pesa con contexto específico: tu equipo, tu dominio, tu presupuesto, tu rotación, tu deadline, tu tolerancia al riesgo.

Un LLM tiene **conocimiento general** de trade-offs (sabe los pros y contras de orquestación vs coreografía). Le falta **los pesos de tu contexto**. Y sin pesos, el output es genérico.

Es el **antipatrón "Out of Context"** aplicado al asistente: te da el análisis correcto, en el contexto equivocado.

### Dónde **sí** funciona el LLM como asistente

Es bueno para:

- **Descriptivo**: *"explícame cómo funciona el estilo space-based."* → ok.
- **Generativo acotado**: *"redacta el borrador de la sección Context de un ADR sobre usar caching para reducir latencia p95 de 800ms a 300ms"* → útil como punto de partida.
- **Auditor de omisiones**: *"aquí está mi ADR; ¿qué antipatrones comunes podría estar violando?"* → a veces ayuda.
- **Traductor de diagramas**: herramientas como Thoughtworks Haiven convierten un diagrama a descripción textual o a PlantUML ejecutable.

Es **malo** para:

- *"¿Qué estilo debo usar para X?"* → decisión contextual, no la delegues.
- *"¿Este ADR es correcto?"* → "correcto" depende de contexto que el LLM no tiene.
- *"¿Qué modelo / base de datos / lenguaje elijo?"* → decisión contextual, no la delegues.

### Regla práctica

**Un LLM puede ayudarte a escribir *cómo* vas a argumentar. No debe decidir *qué* argumentar.** La parte de juicio de arquitectura todavía es humana; el output del juicio es lo que se puede delegar parcialmente.

---

## Concepto nombrado

- **IA generativa en arquitectura** vive en **dos conversaciones distintas** que no hay que mezclar:
  1. **Integrar un LLM** como componente — decisión arquitectónica estándar, más rails + evals + reemplazabilidad + costo/latencia explícitos.
  2. **Usar un LLM como asistente** — bueno para escribir, describir, auditar; malo para decidir. El juicio de trade-offs todavía requiere contexto humano.
- **Regla 1**: un LLM es un **quantum externo**. Trátalo con la misma disciplina operativa que a un servicio externo crítico.
- **Regla 2**: delegar juicio arquitectónico a un LLM es una forma moderna del antipatrón **Out of Context**.

---

## Pregunta del por qué

Piensa en un componente de IA generativa que hayas visto en un sistema (un asistente, un resumidor, un clasificador). Contéstate:

- ¿Qué característica arquitectónica principal está optimizando el sistema al usar IA? ¿Qué está sacrificando?
- ¿Dónde están los **rails**? ¿Hay validación de output? ¿Filtros de contenido?
- Si el proveedor del LLM cambia su API mañana, ¿cuántos lugares del código hay que tocar? ¿El LLM está detrás de una interfaz?
- ¿Cómo se mide si el sistema está **mejor** o **peor** que la semana pasada?

Si cualquiera de estas respuestas es *"no sé / no hay / no lo medimos"*, el componente de IA no está integrado arquitectónicamente — está pegado con cinta.

---

:::exercise{title="Audita un componente de LLM imaginario"}
Imagina que agregas al chatbot del curso una feature: *"resumir conversación de más de 20 mensajes al hacer click en un botón"*. Escribe las 4 cosas que tu ADR tendría que decir:

1. **Reemplazabilidad**: ¿cómo estructuras el código para que cambiar de OpenAI a Claude tome 1 cambio de config, no 1 rewrite?
2. **Rails**: ¿qué valida el output antes de mostrárselo al usuario? (schema, tamaño, contenido).
3. **Evals**: ¿qué métricas te dirían *"esta feature está funcionando como esperamos"*? Nombra al menos 3.
4. **Quantum**: ¿qué pasa si el proveedor del LLM está caído 10 minutos? ¿La feature se degrada o se rompe el chatbot entero?

Sin calificación — ejercicio de reflexión. Lo interesante es notar cuántas de estas preguntas nunca se discuten en decisiones reales de *"agreguemos un LLM"*.
:::

---

## Cierre

Este apéndice existe porque en 2026 casi cualquier sistema nuevo va a tener algún componente de IA generativa. El libro de Richards & Ford lo trata como un **cruce arquitectónico nuevo** (cap. 26) — no como un estilo, no como una tecnología, sino como un eje transversal que toca todas las decisiones.

La disciplina para pensar IA generativa en arquitectura **no es nueva** — son las mismas herramientas de todo el módulo: trade-offs explícitos, ADRs, características, quanta, rails (o sea *contratos*). Lo que cambia es que el componente es no-determinístico, caro, lento, y obsolete en 6 meses.

Si integras LLMs en un sistema **sin** el vocabulario de este módulo, vas a acabar con una variante moderna del Big Ball of Mud — un sistema donde *"la IA lo hace"* y nadie entiende por qué a veces funciona y a veces no.
