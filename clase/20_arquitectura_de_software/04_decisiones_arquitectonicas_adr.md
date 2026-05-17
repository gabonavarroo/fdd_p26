---
title: "Decisiones arquitectónicas (ADRs)"
---

# Decisiones arquitectónicas (ADRs)

## Tensión

Hace 6 meses tu equipo decidió usar MongoDB para el storage del chatbot. Hoy llega un desarrollador nuevo y te pregunta:

> *"¿Por qué MongoDB? Para estos queries claramente habría sido mejor Postgres."*

Tienes dos salidas:

1. *"No me acuerdo bien. Alguien dijo algo de schema flexible en un standup."*
2. *"Léete el ADR-0007. Ahí está el contexto completo, las alternativas que consideramos, y por qué elegimos esto sabiendo lo que sabíamos entonces."*

La primera respuesta es la condición normal de casi todos los equipos. La segunda es lo que vamos a construir en esta lección.

---

## El patrón de razonamiento

El problema no es tu memoria. El problema es **la memoria colectiva del equipo**. Rotación de ingenieros, tres managers distintos, una pandemia, dos pivotes. Lo que estaba claro hace 6 meses hoy es niebla.

Si la decisión vive solo en cabezas, se pierde. Si vive escrita — en un lugar fijo, con un formato predecible — sobrevive.

**Ese es el ADR: un documento mínimo, estructurado, que convierte una decisión en un artefacto durable.**

Pero aquí viene la trampa: no basta con escribir ADRs. Hay formas de escribir ADRs **malos** que son peor que no tenerlos. Vamos primero al formato, después a los antipatrones.

---

## La plantilla ADR (7 secciones)

Un ADR es corto — **una página, máximo dos**. Estas son las secciones:

````markdown
# ADR-0007: Usar MongoDB para el storage primario

## Status
Accepted — 2025-11-14

## Context
El chatbot necesita almacenar conversaciones (estructura anidada,
longitud variable, ~500k mensajes/día proyectados). El equipo
tiene experiencia fuerte en Postgres, cero experiencia en NoSQL.
Plazo de primera release: 8 semanas.

## Decision
Usaremos MongoDB como storage primario para conversaciones.
Los datos transaccionales (billing, usuarios) quedan en Postgres.

## Consequences
- + Schema flexible: conversaciones pueden evolucionar sin migrations.
- + Menos fricción con JSON en el backend (Python → BSON).
- − El equipo pierde 2 semanas aprendiendo MongoDB bien.
- − No podemos hacer joins entre users y conversations sin denormalización.
- − Mayor riesgo operativo: nadie tiene experiencia fuerte aún.

## Governance
El owner de este ADR es el equipo de backend. Reversar requiere
un ADR que lo marque como superseded y describa la migración.

## Notes
- Consideramos Postgres JSONB. Descartado por complicaciones
  de indexación sobre estructuras profundamente anidadas.
- Consideramos DynamoDB. Descartado por costo impredecible a escala.
````

### Por qué cada sección existe

| Sección | Qué contiene | Por qué existe |
|---------|--------------|----------------|
| **Title** | Número + descripción corta | Indexable, citable ("ver ADR-0007") |
| **Status** | Proposed / Accepted / Superseded / RFC | Deja saber si es vinculante **ahora** |
| **Context** | La situación que motivó la decisión | La decisión solo tiene sentido **con** el contexto |
| **Decision** | Lo que se decidió, en una o dos oraciones | El centro — debería ser claro en 10 segundos |
| **Consequences** | Lo que ganas (+) y lo que sacrificas (−) | **Obliga** a nombrar trade-offs — sin esto, no hay ADR |
| **Governance** | Quién puede cambiarlo, cómo | Evita que alguien lo cambie silenciosamente |
| **Notes** | Alternativas consideradas, referencias | Cuando llegue el "¿y por qué no consideraron X?", la respuesta está escrita |

La sección más importante es **Consequences**. Un ADR sin trade-offs explícitos no es un ADR — es un anuncio.

---

## Status lifecycle

Un ADR pasa por estados:

```
   ┌────────────┐
   │  Proposed  │  ← recién escrito, en discusión
   └─────┬──────┘
         │  (equipo acepta)
         ▼
   ┌────────────┐
   │  Accepted  │  ← la decisión está en efecto
   └─────┬──────┘
         │  (cambió el contexto, nueva decisión toma su lugar)
         ▼
   ┌──────────────┐
   │  Superseded  │  ← ya no aplica, pero se conserva como historia
   │  by ADR-N    │
   └──────────────┘
```

### Un caso concreto

Seis meses después de aceptar el ADR-0007 (MongoDB), el equipo se da cuenta de que los queries analíticos son una pesadilla y el costo operativo subió. Escriben el **ADR-0023** que dice *"Migrar conversaciones a Postgres JSONB"*. El nuevo ADR referencia al viejo: *"Supersedes ADR-0007"*. El viejo se marca como *Superseded by ADR-0023*.

Nadie borra el ADR-0007. Sigue ahí. La razón: cuando dentro de un año otro ingeniero pregunte *"¿por qué alguna vez usamos Mongo?"*, la respuesta está en ADR-0007, y la razón por la que lo dejaron está en ADR-0023.

**Historia > prolijidad.**

---

## Las 4 justificaciones de negocio

El libro nota que casi todas las decisiones arquitectónicas se justifican por **una** de estas cuatro razones:

1. **Costo** — *"nos ahorra $X al año"*, *"evita gastar $Y"*
2. **Time-to-market** — *"llegamos N semanas antes"*, *"bloquearía el lanzamiento si hacemos la otra opción"*
3. **Satisfacción del usuario** — *"mejora latencia p95 de 800 → 300 ms"*, *"reduce errores visibles"*
4. **Posicionamiento estratégico** — *"nos coloca en un nicho"*, *"diferencia del competidor"*, *"abre una línea de producto"*

Cuando escribas un ADR, la sección **Context** debe **nombrar** cuál de las cuatro es el driver principal. Si no puedes, probablemente la decisión no es arquitectónica — es de implementación.

---

## Un ejemplo trabajado — shared library vs shared service

La sección **Consequences** no sale de la intuición. Sale de un **análisis de trade-offs** concreto. Richards & Ford usan este ejemplo canónico en el capítulo 27 y vale la pena caminarlo completo: te da un molde reusable.

**El escenario**: tienes comportamiento común (validación, formatos de fecha, traducción de códigos de error) que varios servicios necesitan. ¿Lo pones en una **librería compartida** que cada servicio compila, o en un **servicio compartido** que los otros llaman por red?

### Paso 1 — listar los factores que te importan

Los factores son **específicos a tu contexto**, no genéricos. Para este ejemplo:

- **Código heterogéneo** — ¿tu equipo tiene varios stacks (Python + Go + TS)?
- **Volatilidad** — ¿este código cambia seguido?
- **Versionado** — ¿qué tan fácil es forzar una nueva versión?
- **Riesgo de cambio** — ¿qué tan probable es que un cambio rompa consumidores?
- **Desempeño** — ¿el costo de un call por red importa?
- **Tolerancia a fallas** — ¿qué pasa si el componente compartido se cae?
- **Escalabilidad** — ¿distintos consumidores necesitan escalar distinto?

### Paso 2 — llenar la matriz

| Factor | Shared library | Shared service |
|--------|:-:|:-:|
| Código heterogéneo | − | **+** |
| Volatilidad alta | − | **+** |
| Versionado | **+** | − |
| Riesgo de cambio | **+** | − |
| Desempeño | **+** | − |
| Tolerancia a fallas | **+** | − |
| Escalabilidad diferencial | − | **+** |

Para este conteo simple: librería = 4 positivos, servicio = 3. **La librería gana… en este contexto, con pesos uniformes.**

### Paso 3 — reflexionar sobre los pesos

Aquí está la trampa: en el paso 2 dimos a todos los factores **el mismo peso**. Pero si tu equipo tiene **5 stacks distintos**, el factor *"código heterogéneo"* pesa 5x más que los demás — y la respuesta se invierte. Si estás en un solo stack pero con **volatilidad brutal** (el código cambia cada semana), también cambia.

**El análisis objetivo te da la estructura. Los pesos vienen del contexto del equipo.**

Este es el molde que va en **Consequences**: no una lista de pros y contras al azar, sino una **matriz de factores** con los pesos del contexto explicados. Un ADR con una tabla así es casi imposible de atacar con *"¿y si hubieran considerado X?"*, porque X está en la tabla con su signo.

---

## Los 3 antipatrones

Aquí está la parte más útil del capítulo 21. Los ADRs malos caen casi siempre en uno de estos tres patrones.

### Antipatrón 1 — Covering Your Assets ("cubrirse las espaldas")

El ADR está lleno de *"consideramos", "evaluamos", "podríamos"*, pero no **decide nada**. Es un documento defensivo: el autor quería verse responsable sin comprometerse.

**Señal**: lees el ADR y no puedes decir cuál fue la decisión. Hay una lista de opciones y un tono de "en el fondo cualquiera de estas funcionaría".

**Remedio**: obligar a que la sección **Decision** sea **una oración declarativa**. *"Usaremos X."* Si no puedes escribir esa oración, no hay decisión.

### Antipatrón 2 — Groundhog Day

La misma decisión se discute una y otra vez. Se escribe un ADR. Tres meses después, otro equipo propone la misma opción descartada. Nadie recuerda por qué se descartó.

**Señal**: estás en una reunión donde alguien dice *"¿por qué no hacemos X?"*, y la respuesta honesta es *"ya lo discutimos pero no me acuerdo de la razón"*.

**Remedio**: la sección **Notes** (alternativas consideradas) tiene que listar las opciones descartadas **con una oración de por qué**. Cuando Groundhog Day empiece a ocurrir, el ADR corta la discusión antes del segundo ciclo.

### Antipatrón 3 — Email-Driven Architecture

La decisión vive en un hilo de Slack o un thread de email. Se pierde cuando nadie lo archiva. Nadie fuera de los participantes originales sabe que existió.

**Señal**: la única manera de enterarte de por qué se decidió algo es preguntando a una persona específica.

**Remedio**: **regla del equipo**: *"si una decisión requiere más de 3 mensajes de discusión, se convierte en ADR"*. El hilo original se pega en Context. El resultado se pega en Decision.

### Antipatrón 4 — Out of Context

Los 3 anteriores son sobre **escribir** ADRs. Este es sobre **leerlos** o **copiarlos** mal.

Ocurre cuando alguien toma un análisis de trade-offs correcto — la matriz shared library vs shared service del ejemplo trabajado, por ejemplo — y lo **copia a otro contexto** **sin re-pesarlo**.

**Señal**: *"pero el libro / el blog / el ADR-0042 dice que la librería gana…"* — y quien lo dice no mencionó el contexto en que ganó.

**Remedio**: en la sección **Context** de cualquier ADR derivado, **nombra explícitamente** qué pesos cambiaste respecto al ADR del que te inspiras. El mismo análisis con pesos distintos puede dar la respuesta opuesta. Por eso Richards & Ford dicen que *"un análisis de trade-offs genérico no es útil — se vuelve útil cuando se aplica a un contexto específico"*.

Este antipatrón vive bajo la Ley 1 (todo es un trade-off): sabes que los trade-offs existen, pero no sabes cómo **pesarlos** aquí.

---

## La decisión no es el ADR

Un detalle importante: **escribir el ADR no es tomar la decisión**. Es **registrarla**.

Antes del ADR:

1. alguien propone
2. el equipo discute trade-offs
3. el equipo llega a un acuerdo (o a un "vamos a probar esto por 2 semanas")

El ADR es el paso 4, el **artefacto durable** que deja registro de los pasos 1-3.

Un ADR que no captura discusión real es ficción. Un ADR que captura una discusión real de 40 minutos en una página es un tesoro.

---

## Concepto nombrado

Un **ADR** (Architectural Decision Record) es un documento mínimo, estructurado, con 7 secciones, que convierte una decisión arquitectónica en un artefacto que sobrevive al equipo. Su valor real está en la sección **Consequences** — **obliga** a nombrar trade-offs — y en su **Status lifecycle**, que permite cambiar de opinión **con trazabilidad**.

Los 4 antipatrones — Covering Your Assets, Groundhog Day, Email-Driven Architecture, Out of Context — son los fallos más comunes en equipos que "empiezan a hacer ADRs". Los 3 primeros fallan al **escribir** el ADR; el 4º falla al **aplicar** uno ajeno sin re-pesar el contexto.

---

## Pregunta del por qué

Piensa en una decisión arquitectónica que tu equipo, o un equipo que conoces, haya tomado recientemente. Contéstate:

- ¿Cuál de las **4 justificaciones de negocio** era la principal?
- Si tuvieras que escribir el **Context** en 3 oraciones, ¿lo podrías?
- Si tuvieras que escribir **Consequences** con 2 pros y 2 contras, ¿lo podrías? ¿O solo sabes los pros?
- ¿Cuál de los 3 antipatrones es más probable que hubieran cometido?

---

:::homework{id="20.2" title="ADR real: storage del chatbot" due="2026-04-30" points="15"}
Escribe el **ADR-0007** del chatbot del curso. Imagina que es **noviembre 2025**, estás por la primera release, y tienes que decidir el storage primario.

### Elige una de estas 3 decisiones

1. *Postgres (con JSONB para conversaciones)*
2. *MongoDB*
3. *Separar: Postgres para usuarios/billing, DynamoDB para conversaciones*

### Formato (obligatorio)

Usa exactamente las 7 secciones del libro:

- **Title**: `ADR-0007: [tu decisión en una línea]`
- **Status**: `Proposed — 2025-11-14`
- **Context** (máx 4 oraciones): incluye la **justificación de negocio** principal (costo / time-to-market / satisfacción / posicionamiento).
- **Decision** (1-2 oraciones declarativas): *"Usaremos X."*
- **Consequences** (2 pros y 2 contras, mínimo, con `+` y `−`).
- **Governance** (1-2 oraciones): quién es el owner, cómo se reversa.
- **Notes**: las **dos opciones que descartaste**, con **una oración** de por qué cada una.

### Grading

- **Trade-off legibility (40%)** — ¿un lector ajeno al equipo puede reconstruir el razonamiento? ¿Están los trade-offs nombrados sin eufemismos?
- **Razones de exclusión (20%)** — ¿la sección Notes descarta las alternativas con razón contextual, no genérica?
- **Consequences completas (20%)** — ¿hay trade-offs reales (no solo pros)? ¿Al menos 1 contra está vinculada a una característica arquitectónica?
- **Evitación de antipatrones (20%)** — ¿cae en Covering Your Assets? (lista opciones pero no decide)? ¿Groundhog Day? (no descarta alternativas con razón)? Si cae en alguno: cero en esta sección.

No hay respuesta correcta de **qué** elegir. Hay ADRs honestos y ADRs defensivos. Este kata se evalúa por honestidad.
:::

---

## Cierre

Ya tienes vocabulario para **piezas** (módulos, lección 02), para **el sistema** (características, 03), y para **las decisiones** (ADRs, esta). Falta una clase más de Clase 1: la **geometría del sistema** — monolítico vs distribuido — que es una de las decisiones más caras y más normalizadas del oficio. Lección 05.
