---
title: "Fundamentos de arquitectura"
---

# Fundamentos de arquitectura

## Tensión

Tu compañero dice: *"Ya elegimos Python + Postgres + Kubernetes. La arquitectura ya está."*

Tu otra compañera dice: *"Eso no es arquitectura. Eso es stack. La arquitectura es cómo decidimos qué parte va dónde, por qué, y qué pasa si mañana queremos cambiarlo."*

Las dos tienen algo de razón. Pero si las dos fueran lo mismo, no tendrías nada que discutir con ellas.

¿Qué te están preguntando?

---

## El patrón de razonamiento

Fíjate qué cambia de una frase a la otra.

La primera frase habla de **cosas**: Python, Postgres, Kubernetes. Piezas. Tecnologías.

La segunda frase habla de **cómo encajan**: qué parte va dónde, por qué, y qué pasaría si cambiara.

Una conversación sobre piezas puedes cerrarla: "estas son las piezas, listo". Una conversación sobre cómo encajan **nunca se cierra**: si cambia el negocio, si cambia el equipo, si cambian los clientes, el "cómo encaja" se mueve. Es más incómoda, más lenta, más política — y es la que importa cuando el sistema tiene seis meses de vida.

Esa diferencia — entre "las piezas" y "cómo las decides poner" — es el centro de esta sección.

---

## La definición, en 4 dimensiones

Richards & Ford definen arquitectura como la combinación de cuatro cosas:

1. **Estilo (style)** — la topología gruesa del sistema. Ejemplos: monolito, microservicios, event-driven, layered.
2. **Características arquitectónicas** — las "-ilidades" que el sistema intenta servir: latencia, seguridad, modificabilidad, disponibilidad.
3. **Componentes lógicos** — las piezas que resuelven responsabilidades concretas (no el lenguaje, no el framework: la **lógica**).
4. **Decisiones arquitectónicas** — elecciones que moldean el resto: *"usamos eventos en vez de llamadas síncronas"*, *"toda la data queda en una sola base"*.

```
┌─────────────────────────────────────────────────────────────┐
│           4 DIMENSIONES DE LA ARQUITECTURA                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐         ┌────────────────────┐           │
│   │   Estilo     │────────▶│ Componentes        │           │
│   │ (topología)  │ da forma│ (responsabilidades)│           │
│   └──────────────┘  a      └────────────────────┘           │
│         ▲                          ▲                        │
│         │                          │                        │
│         │ restringe          restringen                     │
│         │                          │                        │
│   ┌──────────────┐         ┌────────────────────┐           │
│   │ Decisiones   │◀────────│ Características    │           │
│   │ (ADRs)       │  exigen │ (-ilidades)        │           │
│   └──────────────┘         └────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Las 4 dimensiones están ligadas. Si cambias las **características** (antes querías "bajo costo", ahora quieres "alta disponibilidad"), probablemente cambia el **estilo** (antes era monolito, ahora es multi-región). Si cambia el **estilo**, cambian los **componentes** (antes había 1 servicio, ahora hay 8). Cada cambio se registra en una **decisión** — porque si no, nadie va a recordar por qué.

### Mapa de esta sección a las 4 dimensiones

| Dimensión | Lecciones que la desarrollan |
|-----------|------------------------------|
| Estilo | `06_estilos_galeria`, `07_microservicios_y_bounded_contexts`, `08_elegir_un_estilo` |
| Características | `03_caracteristicas_arquitectonicas` |
| Componentes | `02_modularidad_y_acoplamiento` (la lente para evaluarlos) |
| Decisiones | `04_decisiones_arquitectonicas_adr` |

---

## Las 3 leyes de arquitectura

La segunda edición del libro nombra **tres** leyes. Los autores confiesan que la primera edición solo tenía **dos** — la tercera apareció tras años más escribiendo y enseñando, y la anotan explícitamente como nueva. Son menos "leyes de la física" y más "fotos de lo que te va a pasar".

### Ley 1 — *"Todo en arquitectura es un trade-off."*

Cada elección tiene algo que gana y algo que pierde. No existen decisiones gratuitas a nivel arquitectónico. Si parece que una decisión no tiene costo, **no detectaste el costo todavía**.

Ejemplo: "vamos a meter una cache para bajar latencia". Parece gratis. El costo:

- ahora tienes un sistema más que puede fallar
- tienes que decidir cuánto tiempo vive el dato (TTL)
- tienes que explicar por qué a veces el usuario ve data vieja
- tienes que saber reaccionar cuando la cache se cae y el backend recibe el tráfico completo

Nada de eso es un problema imposible. Pero todos son costos reales.

### Ley 2 — *"El por qué importa más que el cómo."*

Seis meses después de que tomes la decisión, la implementación (el *cómo*) está en el código — cualquiera puede leerlo. Pero el **por qué** solo está en tu cabeza. Y tu cabeza no va a estar aquí para siempre.

Esta ley es el motivo de existir de los **ADRs** (lección 04). Un ADR es el artefacto que convierte el *por qué* de una decisión en algo que sobrevive al equipo. Richards & Ford lo dicen sin rodeos: si solo documentas el *cómo*, tienes **la mitad de la historia**.

### Ley 3 — *"La mayoría de las decisiones arquitectónicas no son binarias — viven en un espectro entre extremos."* *(nueva en 2da edición)*

Sería cómodo que las decisiones fueran binarias: monolito **o** microservicios, síncrono **o** asíncrono, orquestación **o** coreografía. Pero en arquitectura casi nunca lo son. Cada dicotomía esconde un espectro de opciones intermedias, y el trabajo del arquitecto es **ubicar tu decisión dentro de ese espectro**, no reducirla a un lado u otro.

Por eso la respuesta más frecuente en arquitectura es *"depende"* — depende de **dónde en el espectro** está tu contexto. La Ley 3 formaliza ese reflejo: si alguien responde binariamente sin preguntar contexto, está vendiéndote un default, no una decisión.

Esta ley también explica por qué la misma decisión (*"¿microservicios o monolito?"*) puede tener respuestas distintas en dos equipos sin que ninguno esté equivocado — están en puntos distintos del espectro.

---

## Arquitectura vs diseño

Los términos suenan parecido, pero viven en escalas distintas.

```
                  estratégico ──────────▶ táctico
                  (arquitectura)          (diseño)

  "partimos el                           "esta función
   sistema en 3     ◀── diferencia de ──▶ se llama
   servicios"        reversibilidad      calcular_neto"

   cara de revertir ──────────────▶ fácil de revertir
   cross-team       ──────────────▶ dentro del equipo
   mucho blast radius ────────────▶ poco blast radius
```

### Ejemplos concretos con el chatbot

**Decisiones de arquitectura** (difíciles de revertir, cruzan equipos):

- Separar el model-server del backend como servicio independiente.
- Elegir Postgres en vez de MongoDB como base principal.
- Usar gRPC para comunicación interna y REST para el borde.

**Decisiones de diseño** (reversibles, dentro de un equipo):

- Renombrar una función `parseMessage` → `parse_message`.
- Extraer la lógica de retry en un decorador.
- Elegir entre `dataclasses` y `pydantic` para un modelo interno.

### Heurística rápida

Pregunta: *"¿Cuántos equipos tendrían que coordinarse para revertir esta decisión?"*

- Si la respuesta es "ninguno, lo hago yo en la rama": diseño.
- Si la respuesta es "2+ equipos y un ADR que dice 'superseded'": arquitectura.

---

## Amplitud técnica: el otro músculo del arquitecto

Un desarrollador puede ser *profundo* en una pila (conoce Postgres como nadie). Un arquitecto necesita **amplitud**: saber que Cassandra, DynamoDB, ClickHouse, BigQuery y Postgres existen, para qué sirven, y por qué no elegirías uno de los otros.

No tienes que ser experto en todos. **Tienes que reconocerlos.** La diferencia:

- profundidad: *"sé exactamente cómo tunear esto"*
- amplitud: *"sé qué puedo comprar, y cuándo"*

El arquitecto vive en la amplitud. La profundidad se la contrata al equipo.

---

## Concepto nombrado

Cuando alguien dice *"arquitectura"* en una reunión, suele querer decir una de tres cosas:

1. *"Las tecnologías que usamos"* — esto es **stack**.
2. *"Cómo se dibuja el sistema"* — esto es **diagrama**.
3. *"Qué decidimos, por qué, y qué trade-off aceptamos"* — esto es **arquitectura** en el sentido que vamos a usar toda la sección.

Las tres son útiles, pero solo la tercera sobrevive a cambios.

---

## Pregunta del por qué

Lee las dos frases del inicio:

> *"Ya elegimos Python + Postgres + Kubernetes. La arquitectura ya está."*
>
> *"Eso no es arquitectura. Eso es stack. La arquitectura es cómo decidimos qué parte va dónde, por qué, y qué pasa si mañana queremos cambiarlo."*

Ahora contéstate:

- ¿Cuál de las 4 dimensiones nombra la primera frase? ¿Cuál ignora?
- Si la segunda compañera tiene razón, ¿qué ADR falta en tu equipo imaginario?
- ¿Qué ley de arquitectura viola la primera frase sin darse cuenta?

---

:::exercise{title="Clasifica 6 decisiones: ¿arquitectura o diseño?"}
Clasifica cada una como **arquitectura** o **diseño**, y defiende cada clasificación con **una sola oración** que mencione *reversibilidad* o *blast radius*:

1. *"Migramos el backend de Flask a FastAPI."*
2. *"Movemos el model-server a una VPC separada por razones de compliance."*
3. *"Cambiamos el formato de los IDs de `int` a `uuid`."*
4. *"El equipo de frontend decide renombrar el componente `ChatBox` a `ConversationView`."*
5. *"Vamos a empezar a comunicarnos entre servicios por eventos en vez de llamadas HTTP síncronas."*
6. *"Usamos `typing.Literal` en vez de enums para valores cerrados en Python."*

El kata se evalúa por:

- ¿La clasificación es defendible? (no "la correcta" — defendible)
- ¿La oración nombra explícitamente el criterio?
- ¿Identificaste al menos un caso ambiguo y lo dijiste?
:::

---

## Cierre

En la siguiente lección vamos a abrir la dimensión **componentes**: cómo notar cuándo un módulo empieza a doler, con vocabulario medible (cohesión, acoplamiento, conectividad). Ese es el primer paso para responder *"¿cuál parte de este sistema cambiar duele más?"* sin necesidad de esperar a que duela.
