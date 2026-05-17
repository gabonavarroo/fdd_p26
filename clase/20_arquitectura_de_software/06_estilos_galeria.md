---
title: "Galería de estilos"
---

# Galería de estilos

## Tensión

Tres ingenieros, tres historias sobre el mismo chatbot:

- El primero dibuja **capas** apiladas: UI encima, API en medio, data abajo. *"Así se hace."*
- La segunda dibuja **una caja con módulos bien definidos adentro**, un solo deploy. *"Empieza simple; separa cuando duela."*
- El tercero dibuja **7 cajitas conectadas por flechas**. *"Microservicios. Es el estándar moderno."*

Los tres dibujan el **mismo problema**. Los tres nombran la misma idea fundamental: *"separar responsabilidades"*. Y sin embargo los sistemas que proponen son **completamente distintos** — en complejidad, costo, flexibilidad, y en las características que optimizan.

¿Cómo puede la misma idea producir cosas tan distintas?

---

## El patrón de razonamiento

La idea *"separar por responsabilidad"* no te dice:

- **qué eje** separar (por tipo de trabajo, por flujo de datos, por dominio, por ciclo de cambio)
- **cuántas piezas** crear
- **cómo hablan** entre sí (memoria, red, eventos, cola de mensajes)
- **quién es dueño** de cada pieza

Cada estilo es una respuesta **específica** a esas 4 preguntas. Los estilos son **formas concretas** de separar, con trade-offs bien conocidos.

El patrón: **conocer los estilos** no te dice cuál elegir. Te da **un menú comparable**: "estos son los nombres, éstas son sus propiedades, éstos son sus costos típicos". Con ese menú, elegir deja de ser intuición.

---

## Antes de los estilos — Big Ball of Mud

Richards & Ford abren el capítulo de estilos con un recordatorio incómodo: **el estilo más común en la práctica no está en la galería.**

Se llama **Big Ball of Mud** (Brian Foote & Joseph Yoder, 1997). La definición original:

> *"Un Big Ball of Mud es un sistema con estructura aleatoria, desordenada, enredada como spaghetti, pegada con cinta y alambre. Estos sistemas muestran signos inequívocos de crecimiento descontrolado y reparaciones apresuradas repetidas."*

No es un estilo — es **la ausencia de estilo**. Ocurre cuando nadie decide, cuando cada feature encuentra su propio camino, cuando *"arreglar rápido"* se vuelve el modo por default.

**¿Por qué abrir con esto?** Porque el Big Ball of Mud es lo que obtienes si **no** haces lo que el resto de la lección enseña. Elegir un estilo — cualquiera de los 5 — ya es un paso adelante. El estilo que no elegiste conscientemente ya lo tienes: es Mud.

---

## Antes de los estilos — partitioning por dominio vs por técnica

La segunda decisión **previa a elegir estilo** es cómo vas a partir el sistema. Hay dos formas canónicas, y cada estilo de la galería es una combinación específica de ellas.

### Partitioning técnico

Separas por **tipo de trabajo**: UI aquí, lógica de negocio allá, acceso a datos abajo. Es la partición que ves en **Layered**. El Model-View-Controller clásico es su caso más visible.

**Consecuencia (Conway's Law)**: si particionas técnicamente, tu organización tenderá a formar equipos por función — un equipo de backend, un equipo de frontend, un equipo de DBA. Ya verás esto en la lección 08.

### Partitioning por dominio

Separas por **qué problema resuelve cada pedazo**: `auth`, `conversation`, `billing`, `inference`. La partición por dominio viene del **Domain-Driven Design** de Eric Evans (2003). Es la partición detrás del **modular monolith** y de los **microservicios**.

**Consecuencia**: los equipos tienden a organizarse por dominio — *"el equipo de conversaciones"*, *"el equipo de billing"* — en vez de por función técnica.

### Por qué importa antes de la galería

De los 5 estilos que vienen:

- **Layered** es partitioning **técnico** puro.
- **Pipeline** es partitioning por **etapa de procesamiento** (variante técnica).
- **Modular monolith, Event-driven, Microkernel, Microservicios** son partitioning por **dominio** (cada uno con su giro).

**Elegir "partición técnica vs partición por dominio" ya es una decisión arquitectónica grande** — frecuentemente la primera que tomas antes de elegir estilo. Un equipo que decide "dominio" ya descartó Layered como estilo principal.

---

## La galería (5 estilos, 1 pantalla)

![Galería de estilos](./images/gallery_styles.png)

Vamos a ver cinco estilos de primer nivel, cada uno con su topología, y con el chatbot como caso de aplicación. El resto — space-based, SOA orquestada, service-based — quedan como pie de página al final.

---

## Estilo 1 — Layered (N-tier)

### Topología

```
 ┌───────────────────────┐
 │   Presentación        │   UI, controllers
 ├───────────────────────┤
 │   Lógica de negocio   │   servicios, reglas
 ├───────────────────────┤
 │   Persistencia        │   repositorios
 ├───────────────────────┤
 │   Base de datos       │   tablas
 └───────────────────────┘
```

Las capas están **apiladas** y **solo la capa de arriba llama a la de abajo**.

### Donde gana

- Equipos que apenas están aprendiendo a estructurar un sistema. Es el estilo más fácil de enseñar.
- Sistemas pequeños donde las responsabilidades son claramente *técnicas* (view, logic, data) en vez de *de dominio*.
- Testabilidad **mecánica** alta — cada capa se prueba en aislamiento.

### Donde rompe

- Las capas son **técnicas**, no de dominio. Un cambio de feature que afecta "user flow X" termina tocando las 4 capas — con lo cual aunque hay "capas", todo se mueve junto.
- Rendimiento: cada request atraviesa todas las capas, aunque no las necesite.
- No maneja bien la escala de equipos: todos tocan todas las capas, no hay dueños claros.

### Aplicado al chatbot

Layered puro al chatbot se vería así: UI React encima, un `ChatService` en la capa media que habla con `ConversationRepository`, y Postgres al fondo. Funciona. Pero cada nueva feature (agregar "likes" a mensajes, integrar plugins) toca las 3 capas — y el diagrama esconde que en realidad todo cambia junto.

### Características que optimiza vs sacrifica

- **+** testabilidad, simplicidad inicial
- **−** modificabilidad frente a features cross-capa, escalabilidad de equipos

---

## Estilo 2 — Modular Monolith

### Topología

```
 ┌──────────────────────────────────────────────────────┐
 │                  SERVICIO ÚNICO                      │
 │                                                      │
 │   ┌────────┐   ┌──────────┐   ┌─────────┐            │
 │   │  auth  │   │ chat     │   │ billing │            │
 │   │ module │   │ module   │   │ module  │            │
 │   └────────┘   └──────────┘   └─────────┘            │
 │                                                      │
 │   fronteras claras entre módulos                     │
 │   (enforced at build time: paquetes separados,       │
 │   APIs internas explícitas, tests de frontera)       │
 │                                                      │
 │   un solo deploy, una sola base de datos             │
 │                                                      │
 └──────────────────────────────────────────────────────┘
```

**Un solo proceso. Un solo deploy. Pero los módulos adentro tienen fronteras reales y explícitas.**

Es la **arquitectura honesta** que casi cualquier sistema nuevo debería empezar siendo.

### Donde gana

- Equipos pequeños/medianos (< 20 ingenieros) que quieren productividad **ahora** y flexibilidad para separar **después**.
- Sistemas en los que los dominios son claros pero todavía **cambian juntos** frecuentemente.
- Reduce drásticamente todos los costos de distribuido (latencia, falacias, ops): sigue siendo un monolito — pero no una bola de barro.

### Donde rompe

- Requires discipline. Si el equipo no **hace cumplir** las fronteras, se convierte en monolito tradicional.
- No separa deploys — un bug en `billing` puede tirar el servicio entero.
- No separa recursos — todo comparte CPU, memoria, y escala juntos.

### Aplicado al chatbot

Un proceso Python con 4 paquetes: `auth/`, `conversation/`, `inference/`, `billing/`. Cada paquete expone una interfaz interna. `billing` no importa nada de `auth` que no esté en la interfaz pública de `auth`. Tests de frontera verifican esto.

Desde fuera, el mundo ve un solo servicio. Desde dentro, el código sabe que hay **4 dominios** que podrían separarse mañana si el dolor lo justifica.

### Características que optimiza vs sacrifica

- **+** time-to-market, simplicidad operativa, modificabilidad
- **−** escalabilidad independiente por módulo, tolerancia a fallo por módulo

---

## Estilo 3 — Pipeline (pipe-and-filter)

### Topología

```
   entrada ──▶ [filter 1] ──▶ [filter 2] ──▶ [filter 3] ──▶ salida
```

Cada *filter* es una etapa que transforma entrada → salida. Los *pipes* son las conexiones (memoria, stdin/stdout, Kafka).

### Donde gana

- **Procesamiento de datos** por etapas: ETL, compilación, pipelines de ML.
- **Composabilidad**: agregas/quitas etapas cambiando el pipe.
- **Testabilidad**: cada filter se prueba con entradas/salidas conocidas.

### Donde rompe

- No modela bien **interacción** (pedidos de usuario que requieren I/O bidireccional).
- Errores que necesitan volver hacia atrás son difíciles de modelar.
- Debugging requiere inspeccionar entre etapas.

### Aplicado al chatbot

El **pipeline de mensajes entrantes** encaja: `recibir → validar → moderar → enrutar al modelo → postprocesar → devolver`. Cada etapa es un filter. El pipeline es Kafka o colas internas.

No encaja para **el request síncrono** del usuario (*"escribe, espera, recibe"*) — ese es mejor event-driven o REST simple.

### Características que optimiza vs sacrifica

- **+** modificabilidad por etapa, testabilidad
- **−** latencia (cada etapa suma), interactividad bidireccional

---

## Estilo 4 — Event-driven

### Topología

```
                  ┌───────────────────────┐
                  │     event bus         │
                  │   (Kafka / NATS /     │
                  │    RabbitMQ / ...)    │
                  └───┬───────┬───────┬───┘
                      │       │       │
                      ▼       ▼       ▼
                   ┌────┐  ┌────┐  ┌────┐
                   │ A  │  │ B  │  │ C  │
                   └────┘  └────┘  └────┘
                    │        │      │
                    └────────┴──────┘
                    publican eventos también
```

Los componentes no se llaman entre sí directamente. Publican **eventos** en un bus. Otros componentes los consumen.

### Donde gana

- **Desacople** fuerte entre componentes — no tienen que conocerse.
- **Escalabilidad** desigual: cada consumidor se escala según su carga.
- Añadir un nuevo consumidor no requiere cambiar nada en los productores.

### Donde rompe

- **Orden** de eventos: saber "qué pasó antes" es no-trivial.
- **Debugging**: una cadena de 5 eventos es más difícil de trazar que 5 llamadas síncronas.
- **Consistencia**: dos consumidores procesan en distinto momento. Ya no hay una "foto" consistente del sistema.
- Requiere **observabilidad seria** — la falacia #11 de la lección 05 muerde fuerte aquí.

### Aplicado al chatbot

Cada mensaje del usuario genera eventos: `MessageReceived → ModerationRequested → ModerationCompleted → ModelInferenceRequested → InferenceCompleted → MessageDelivered`. Cada servicio consume lo que le toca y publica lo siguiente.

**Gana**: si mañana se quiere agregar un servicio de "analytics" o "compliance logging", solo se suscribe al bus. No cambia nadie más.

**Pierde**: si el usuario nunca recibe respuesta, hay que trazar 6 eventos en 4 servicios.

### Características que optimiza vs sacrifica

- **+** modificabilidad, escalabilidad, desacople
- **−** observabilidad (cara de agregar), consistencia, latencia p99

---

## Estilo 5 — Microkernel (plugin architecture)

### Topología

```
                  ┌──────────────────────┐
                  │      CORE            │
                  │   (mínimo estable)   │
                  └─────┬──────┬────┬────┘
                        │      │    │
                        ▼      ▼    ▼
                     ┌────┐ ┌────┐ ┌────┐
                     │ P1 │ │ P2 │ │ P3 │  plugins
                     └────┘ └────┘ └────┘
```

Un **core** mínimo que define lo imprescindible. Extensiones ("plugins") que añaden funcionalidad sin modificar el core.

### Donde gana

- **Productos** que se venden configurables: IDEs (VS Code, IntelliJ), navegadores, sistemas de pagos con múltiples providers.
- **Extensibilidad** sin acoplar al core a los plugins.
- Plugins pueden ser escritos por terceros sin que toquen el core.

### Donde rompe

- El **core** es crítico — si falla, todo falla. Cambiar el core es caro porque todos los plugins dependen.
- La **API de plugins** se vuelve un contrato público: cambiarla rompe todo el ecosistema.
- No todos los sistemas tienen naturalmente esta forma — forzarla es peor que no tenerla.

### Aplicado al chatbot

El chatbot puede ser **microkernel por modelo**: un core (`gateway + routing + logging`) y *plugins* que son adaptadores de modelo (OpenAI, Anthropic, local, cliente enterprise). Agregar un nuevo modelo = escribir un nuevo plugin sin tocar el core.

Gana cuando el producto es *"el chatbot que soporta cualquier modelo"*. Pierde si la mayor parte del valor está en la lógica del core — en ese caso microkernel agrega complejidad sin pagar.

### Características que optimiza vs sacrifica

- **+** extensibilidad, aislamiento de funcionalidad de terceros
- **−** simplicidad, performance (cada plugin cruza boundary)

---

## El mismo chatbot, 3 formas

![Chatbot en 3 estilos](./images/chatbot_three_styles.png)

Los mismos 4 dominios (auth, conversación, inferencia, billing):

- como **monolito modular**: un servicio, 4 paquetes adentro, todo síncrono.
- como **event-driven**: 4 servicios independientes que se comunican por bus.
- como **microservicios**: 4 servicios con APIs REST/gRPC y 4 bases de datos separadas.

Los tres resuelven el mismo problema. Los tres **optimizan cosas distintas**. La decisión de cuál elegir vuelve a ser la Ley 3: no es binaria, los tres viven en un **espectro** entre acoplamiento fuerte (monolito) y desacoplamiento total (microservicios), y tu contexto ubica dónde caes.

---

## Los tres que no caben aquí (footnote)

- **Service-based** — menos servicios que microservicios, comparten algo de infraestructura (base común). Útil como paso intermedio entre monolito y microservicios.
- **Space-based** — cache distribuida como backbone; diseñado para sistemas con picos extremos de tráfico donde la base de datos es el cuello de botella (ej: sistemas de trading). Raro fuera de nichos.
- **Orchestration-driven SOA** — SOA tradicional con un orquestador central. Muchos sistemas enterprise viejos viven aquí. Hoy en día suele tener mala fama por la centralización; a veces justificada, a veces no.

No los enseñamos en detalle porque (a) son nichos y (b) con los 5 estilos de arriba tienes lo suficiente para razonar.

---

## Concepto nombrado

Un **estilo arquitectónico** es una topología gruesa con propiedades conocidas, trade-offs identificados, y un menú de decisiones implícitas que ya tomaste al adoptarlo.

Los 5 estilos de este módulo — layered, modular monolith, pipeline, event-driven, microkernel — son los que más probablemente verás. Cada uno tiene **ganancias** y **rompimientos** específicos. Saber nombrarlos es la mitad de la batalla; la otra mitad es saber **cuándo usar cuál**.

---

## Pregunta del por qué

Vuelve a los tres ingenieros de la tensión inicial. Contéstate:

- ¿Cuál de los 5 estilos está defendiendo cada uno?
- Si los tres defendieran el **mismo** sistema, ¿cuál de los tres tendría el ADR más sólido?
- ¿Alguno de los tres está implicitamente asumiendo una de las 11 falacias de la lección 05?

---

:::exercise{title="Elige un estilo y describe sus costos"}
Para **uno** de los siguientes sistemas, elige el estilo que usarías de los 5, y lista **3 costos específicos** (no genéricos):

1. Un servicio interno de generación de reportes PDF a demanda, ~100 usuarios internos, ejecuta ~1 reporte/minuto.
2. Un procesador de pagos que debe manejar 5000 tx/s en picos, con compliance SOC2, distribuido en 2 regiones.
3. Un editor de código en el browser con soporte para extensiones de terceros (el target: miles de extensiones comunitarias).

Evaluación:

- ¿El estilo elegido matchea el **perfil de uso**? (#1 no debería ser event-driven si nadie lo justifica)
- ¿Los 3 costos son específicos al estilo + sistema, no genéricos?
- ¿Nombraste al menos una **característica** que el estilo sacrifica?
:::

---

## Cierre

Ya conoces los 5 estilos y cómo se aplican. La siguiente lección profundiza en **microservicios + bounded contexts**, porque es el estilo que más se sobreusa y más se malinterpreta — y el que exige la vocabulario más rica para usarse bien.
