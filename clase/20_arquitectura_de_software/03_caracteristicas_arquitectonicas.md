---
title: "Características arquitectónicas"
---

# Características arquitectónicas

## Tensión

Tu gerente te pide: *"Quiero que el chatbot sea rápido, seguro, escalable, modular, observable, auditable, tolerante a fallos, multi-región, low-cost y con zero downtime deploys."*

Tú sabes que pidió **diez** cosas. También sabes que si optimizas las diez por igual, no optimizas ninguna.

¿Cuáles le concedes? ¿Cuáles le niegas? ¿Cómo justificas la negación?

---

## El patrón de razonamiento

Las diez palabras que dijo tu gerente son todas **"-ilidades"**: latencia, seguridad, escalabilidad, modularidad, observabilidad, auditabilidad, tolerancia a fallas, disponibilidad regional, costo, deploys sin downtime.

Todas son deseables. Todas son caras. **No se pueden maximizar todas a la vez**, porque optimizar una suele costar otra:

- *"Más tolerante a fallos"* → más redundancia → **más caro**
- *"Más modular"* → más módulos → **más latencia** (más hops)
- *"Más seguro"* → más validación → **menos rápido**
- *"Más escalable"* → más distribución → **menos simple de operar**

El patrón: las características se **pelean entre sí**. Elegir una es sacrificar otras. Por eso el arquitecto no las acumula — las **prioriza**.

---

## ¿Qué convierte a una "-ilidad" en una característica arquitectónica?

No cualquier adjetivo califica. Una característica arquitectónica cumple los **3 criterios** del libro:

1. **No es de dominio.** *"Procesa pagos en MXN"* no es arquitectónico — es de negocio. *"Latencia p95 < 300ms"* sí es arquitectónico, porque aplica a cualquier sistema con tráfico.
2. **Influye en decisiones estructurales.** *"El código debe usar camelCase"* no influye en estructura — es estilo. *"El sistema debe sobrevivir la caída de una zona de AWS"* sí — obliga a replicación, a multi-AZ, a cambiar el estilo.
3. **Es crítico o importante para el éxito del sistema.** Si nadie se va a enojar cuando falle, no es característica arquitectónica. Si tu compliance officer renuncia cuando falle, claramente sí.

### Ejercicio mental — ¿cuál califica?

| Requisito | ¿Característica arquitectónica? | Por qué |
|-----------|---------------------------------|---------|
| *"Response time < 200ms"* | Sí | Afecta estructura (cache, CDN, co-ubicación), no-dominio, crítico |
| *"Usuario puede cambiar su password"* | No | Requisito de dominio |
| *"API devuelve JSON"* | No | Decisión de implementación, no estructural |
| *"Sobrevive caída de una AZ"* | Sí | Cambia la forma del sistema (réplicas, health checks), cross-dominio |
| *"Código pasa linter"* | No | Proceso de desarrollo, no del sistema en operación |

---

## La taxonomía (un mapa, no un catálogo para memorizar)

Las características se agrupan para orientar la conversación, no para hacer checklist:

```
┌─────────────────────────────────────────────────────────────────┐
│             TAXONOMÍA DE CARACTERÍSTICAS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   OPERATIVAS        ESTRUCTURALES     CROSS-CUTTING             │
│   ─────────────     ────────────      ─────────────             │
│   disponibilidad    modificabilidad   seguridad                 │
│   latencia          extensibilidad    auditabilidad             │
│   escalabilidad     acoplamiento      accesibilidad             │
│   tolerancia        testabilidad      legal/compliance          │
│   recuperabilidad   instalabilidad    privacidad                │
│                                                                 │
│                       CLOUD-ESPECÍFICAS                         │
│                       ─────────────                             │
│                       elasticidad, multi-región,                │
│                       cold-start, costo-por-request             │
│                                                                 │
│                       DE PROCESO                                │
│                       ─────────────                             │
│                       time-to-market, frecuencia de deploy      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Las características **cloud-específicas** son un agregado de la 2da edición, y son particularmente relevantes cuando corres LLMs (cold starts del model server, costo por inferencia, escalabilidad bajo bursts).

---

## Implícitas vs explícitas

Las que **escribes** son las explícitas. Las que **asumes sin escribir** son las implícitas.

Las implícitas son peligrosas porque nadie las discute hasta que se rompen.

### Caso chatbot — una implícita que se volvió explícita

El equipo del chatbot asume *"operamos solo en una región (MX)"*. Nadie lo escribió. Seis meses después, el CEO promete a un cliente brasileño tiempos de respuesta locales. De pronto:

- *"Operamos en una región"* se vuelve **una restricción** que bloquea el negocio.
- Hay que rediseñar storage (replicación cross-region), compute (deploy en SA), compliance (leyes locales).
- Nadie firmó un ADR, pero todo el sistema depende de esa suposición no escrita.

**Lección**: cuando te sientes a listar características, pasas por encima primero las **implícitas**. *"¿Qué estamos asumiendo que no estamos escribiendo?"*

---

## La enseñanza central: elige pocas, no muchas

Un arquitecto principiante intenta satisfacer **todas** las características. Un arquitecto practicante sabe que eso no existe.

Regla práctica del libro: **3 a 7 características explícitas. Nunca más.**

Por qué:

- más de 7, nadie las recuerda
- más de 7, se contradicen entre sí
- más de 7, el sistema no puede optimizar nada claramente
- más de 7, los trade-offs se vuelven política en vez de ingeniería

### El kata "defiende tus exclusiones"

Cuando elijas 5 características para un sistema, la parte **difícil** no es defender las 5 que elegiste. Es defender las **20 que excluiste**:

- *"No elegí 'escalabilidad horizontal' porque el sistema atiende a máximo 500 usuarios simultáneos, que caben en una sola instancia."*
- *"No elegí 'multi-región' porque el tiempo-a-mercado importa más que la latencia global en esta fase."*
- *"No elegí 'compliance SOC2' porque no aplica al producto actual."*

La exclusión es donde se ve si entendiste el sistema. Elegir 5 sin justificar qué dejaste afuera es acumulación de deseos, no arquitectura.

---

## Tres chatbots, tres priorizaciones

El mismo chatbot puede existir en tres versiones, cada una optimizando distinto:

![Radar de características](./images/radar_characteristics.png)

| Variante | Top 3 características | Sacrificios |
|----------|------------------------|-------------|
| **Latency-first** | latencia, disponibilidad, escalabilidad | costo (cache caliente cara), simplicidad (multi-región) |
| **Cost-first** | costo, simplicidad, testabilidad | latencia (cold starts aceptables), multi-región (no aplica) |
| **Compliance-first** | auditabilidad, seguridad, privacidad | velocidad de deploy (cada cambio auditado), costo (encryption at rest everywhere) |

No son "mejores" o "peores". Responden a **contextos distintos**. El mismo equipo puede tener que defender cualquiera de las tres según a quién le están vendiendo.

---

## Concepto nombrado

Una **característica arquitectónica** es una "-ilidad" que:

1. aplica más allá del dominio,
2. influye en la forma del sistema,
3. es crítica para el éxito.

El trabajo del arquitecto no es listar todas — es elegir las **3 a 7** que este sistema, en este contexto, va a optimizar, y defender qué **no** optimiza.

---

## Pregunta del por qué

Vuelve a la petición del gerente: *"rápido, seguro, escalable, modular, observable, auditable, tolerante a fallos, multi-región, low-cost, zero downtime."*

Contéstate:

- Si tuvieras que **quitar** 5 de esas 10, ¿cuáles quitas y por qué?
- ¿Cuáles son **implícitas** que tu gerente probablemente asume sin decir?
- Las 5 que mantuviste, ¿se pelean entre sí? ¿Cuál ganará la pelea si no lo decides explícitamente?

---

:::homework{id="20.1" title="5 características para tu chatbot + 20 exclusiones" due="2026-04-28" points="10"}
Imagina que el chatbot del curso va a lanzar públicamente dentro de **dos meses** a un público universitario. Tú eres el arquitecto responsable.

Entrega:

### Parte A — Las 5 que eliges

Lista **5 características arquitectónicas** que el sistema va a priorizar. Para cada una:

- Nómbrala (una palabra o dos).
- **Defínela medible**: *"latencia"* no sirve; *"latencia p95 < 400ms para el endpoint `/chat`"* sí.
- Justifica en **una oración** por qué es crítica para este contexto (usuarios universitarios, 2 meses, primera release).

### Parte B — Las 20 que excluyes

Lista **20 características que NO vas a priorizar**. Para cada una, **una oración** explicando por qué no aplica o por qué la sacrificas conscientemente.

### Parte C — Los trade-offs

De tus 5 elegidas, ¿cuáles **se pelean entre sí**? Nombra al menos un par en conflicto y explica cómo resuelves la pelea.

### Grading

- **Parte A (25%)** — ¿Las 5 son medibles? ¿Son característica arquitectónicas (no requisitos de dominio)?
- **Parte B (50%)** — Sí, **el peso fuerte está aquí**. ¿Las 20 están defendidas con razones contextuales, no genéricas?
- **Parte C (25%)** — ¿Identificaste un conflicto real? ¿Propusiste una resolución explícita en vez de "las haremos ambas"?

No hay "respuesta correcta" de qué 5 elegir. Hay respuestas legibles y defendibles, y respuestas que son una lista de deseos.
:::

---

## Cierre

Ya tienes lentes para módulos (lección 02) y para el sistema completo (esta). La siguiente pregunta es: *"¿cómo dejo registro de que elegí estas 5 características y no otras?"*. El artefacto que convierte la elección en algo que sobrevive al equipo se llama **ADR**. Lección 04.
