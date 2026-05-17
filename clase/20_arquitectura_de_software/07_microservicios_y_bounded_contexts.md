---
title: "Microservicios y bounded contexts"
---

# Microservicios y bounded contexts

## Tensión

Tu startup tiene **4 personas**. Están haciendo el chatbot. Tu CTO acaba de volver de una conferencia y dice:

*"Tenemos que hacer esto con 5 microservicios. Es el estándar."*

Pasa el tiempo. Ahora la startup tiene **50 personas**. El mismo CTO, mirando el monolito que se volvió bola de barro, dice:

*"Tenemos que hacer esto con 5 microservicios. Es el estándar."*

**Las dos frases son idénticas. Una es sensata. La otra es autosabotaje.**

¿Cuál es cuál? ¿Cómo lo sabes?

---

## El patrón de razonamiento

Microservicios **no son default**. Son una respuesta a **un problema específico**: equipos independientes que quieren desplegarse independientemente y cambiar a ritmos distintos.

Si tus 4 personas todas trabajan en todo, no tienes ese problema — y microservicios te cuestan 10x más que te ayudan.

Si tus 50 personas están en 5 equipos que quieren moverse independientemente, entonces microservicios empiezan a pagar — porque ahora sí tienes un problema que resuelven.

El patrón de razonamiento: **¿qué problema estás resolviendo?** No es *"queremos ser modernos"*, *"es lo que se usa"*, *"escalabilidad"*. Es un problema específico, nombrable, vinculable a una característica arquitectónica.

---

## Microservicios como estilo, no como default

Microservicios tienen un perfil bien conocido:

### Ganan cuando

- tienes equipos **independientes** con ownership claro
- los componentes cambian a **ritmos distintos** (billing cambia cada 6 meses, UI cambia cada semana)
- las **escalas** son muy distintas entre componentes (1:1000 en uso)
- compliance o seguridad **exige aislamiento** (billing tiene que estar en su propio perímetro)
- la **madurez operativa** es alta: observabilidad, CI/CD, on-call, tracing distribuido

### Pierden cuando

- equipo < 15 personas que se coordinan bien
- producto en primera release, requisitos inestables
- cero experiencia operativa en distribuido
- sistema con lógica altamente acoplada por naturaleza

### El caso donde son el estilo **incorrecto**

Un equipo de 3 ingenieros que hace un MVP con microservicios:

- **3 pipelines**, **3 dashboards**, **3 bases**, **3 on-calls**, **3 ritmos de versionado**
- cada feature cross-service es un pull request en 3 repos
- la **latencia p99** sube porque las features requieren 4-5 hops entre servicios
- el **time-to-market** se duplica

El problema no es "mal hecho". El problema es que **el estilo no matchea el contexto**.

---

## El cómo: bounded contexts

Si decides que microservicios **sí** son el estilo correcto, la pregunta siguiente es: *"¿dónde corto?"*. Si cortas mal, terminas con 15 servicios que se llaman entre sí todo el tiempo — o sea, un monolito distribuido (lo peor de ambos mundos).

El concepto que te guía se llama **bounded context**. Viene del Domain-Driven Design, pero para microservicios basta con la versión mínima:

> Un **bounded context** es una frontera dentro de la cual un concepto tiene un significado único y consistente.

### Ejemplo concreto

En el chatbot, la palabra **"usuario"** puede significar cosas distintas en contextos distintos:

| Contexto | Qué es "usuario" |
|----------|------------------|
| `auth` | credenciales, sesiones, roles |
| `conversation` | id + configuración del chat + historial |
| `billing` | cuenta, plan, método de pago, facturas |
| `inference` | id + rate limits + modelo preferido |

Cada contexto tiene **su propia** visión de usuario. Forzar a los 4 a compartir **un mismo** modelo de usuario es lo que hace grande y frágil al dominio.

### Architectural Quantum — la versión formal del bounded context

Richards & Ford formalizan el mismo concepto con un nombre distinto: **architectural quantum** (plural: *quanta*, del latín).

> Un **architectural quantum** es *"la pieza más pequeña del sistema que puede correr de forma independiente"*.

Un quantum tiene cuatro propiedades:

1. **Deployable independientemente** — incluye *todas* las piezas que necesita (código + su base de datos + sus dependencias). Un monolito con una sola base de datos es, por definición, **un solo quantum**.
2. **Cohesión funcional alta** — el quantum hace *una cosa coherente*, no una colección arbitraria de utilidades.
3. **Acoplamiento estático externo bajo** — poca "cableado" hacia otros quanta.
4. **Comunicación síncrona** con otros quanta requiere un análisis de acoplamiento dinámico aparte.

**Por qué importa la distinción**: el bounded context es un concepto de **dominio** (¿dónde están las fronteras semánticas?). El quantum es un concepto **operacional** (¿qué unidad puedo desplegar, escalar y fallar de forma aislada?). En microservicios bien hechos, **cada bounded context = un quantum**. Pero pueden separarse: dos servicios que comparten una base de datos son **dos bounded contexts pero un solo quantum** — porque un corte en la DB los derriba a ambos.

**Regla práctica**: si dos "servicios" no pueden fallar de forma independiente — porque comparten DB, cache, cola crítica, o schema de eventos — son **el mismo quantum** aunque los hayas desplegado en dos contenedores distintos. Y si son el mismo quantum, **no ganaste los beneficios operativos de microservicios**.

Este es el test más honesto para saber si tienes microservicios reales o un monolito distribuido disfrazado.

### El chatbot decomposición en bounded contexts

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────┐   ┌────────────────┐   ┌──────────────┐       │
│  │  auth    │   │  conversation  │   │  inference   │       │
│  │          │   │                │   │              │       │
│  │  users   │   │  conversations │   │  rate_limits │       │
│  │  tokens  │   │  messages      │   │  model_prefs │       │
│  │  roles   │   │                │   │              │       │
│  └──────────┘   └────────────────┘   └──────────────┘       │
│                                                             │
│                 ┌──────────────┐                            │
│                 │   billing    │                            │
│                 │              │                            │
│                 │  accounts    │                            │
│                 │  plans       │                            │
│                 │  invoices    │                            │
│                 └──────────────┘                            │
│                                                             │
│   Cada contexto es dueño de SU data, SU API, SU schema     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Dos heurísticas para la granularidad

¿Cómo saber si tus contextos están "bien cortados"?

### Heurística 1 — *"Un servicio, una base de datos. Ningún otro servicio la lee o escribe directamente."*

Si dos servicios comparten una base, están acoplados por datos — aunque no por código. Cambiar el schema requiere coordinación entre equipos. Eso es "microservicios de nombre, monolito de facto".

**Caso chatbot**: si `auth` y `conversation` comparten la tabla `users`, no tienes dos servicios — tienes un monolito en dos binarios.

**Remedio**: cada servicio tiene su base. Si otro servicio necesita data, la pide por API.

### Heurística 2 — *"Un cambio en un servicio no fuerza redeploy de otros."*

Si agregas un campo a `auth` y tienes que desplegar `conversation` al mismo tiempo, tus servicios están **acoplados por versión** — la falacia #9 de la lección 05 te va a morder.

**Caso chatbot**: cambias el formato de los tokens emitidos por `auth`. Si el cambio requiere redeploy coordinado con el frontend, no ganaste nada con haber separado.

**Remedio**: versionar las APIs internas. Desplegar `auth` que emite ambas versiones por un tiempo. Migrar clientes después.

### Una heurística fallida que verás mucho

*"Un servicio por entidad."*

No. Eso produce servicios tipo `UserService`, `MessageService`, `TokenService` — que terminan llamándose entre sí constantemente, porque los casos de uso reales cruzan varias entidades.

El corte correcto es por **contexto de negocio** (`auth`, `conversation`, `billing`), no por entidad técnica (`User`, `Message`, `Token`).

---

## El costo operativo, sin cobertura publicitaria

La parte que los blogs sobre microservicios casi nunca cuentan: **microservicios multiplican el costo operativo casi linealmente por el número de servicios**.

### Qué se multiplica

- **Pipelines CI/CD** — un pipeline por servicio. 5 servicios = 5 pipelines mantenidos.
- **Dashboards** — uno por servicio para métricas operativas (latencia, errores, tráfico).
- **Dashboards de negocio** — uno transversal que requiere agregar datos de todos.
- **Contratos entre servicios** — N × N potencialmente. Prácticamente ~3N. Cada contrato es un test de contrato que se mantiene.
- **Versionado** — cada servicio versionado independientemente; cada cliente tiene que tolerar versiones mixtas en producción.
- **On-call** — antes había un sistema que alguien conocía bien. Ahora hay 5 sistemas.
- **Tracing distribuido** — obligatorio. Un timeout en el frontend requiere poder ver la cadena completa.
- **Observabilidad** — metrics + logs + traces, por servicio, correlacionables.

### Regla de pulgar

**Antes de pasar de 1 a 2 servicios, pregúntate: ¿estoy listo para pagar al menos 10 artefactos operativos adicionales?**

Si la respuesta es no, estás monolítico-modular (lección 06) — y probablemente eso sea correcto.

### Las 11 falacias, revisitadas

Los microservicios son el estilo donde las 11 falacias más muerden — en particular:

- #1 *"La red es confiable"* → retries, circuit breakers
- #2 *"La latencia es cero"* → tu budget de latencia se gasta en hops
- #9 *"El versionado es fácil"* → contratos entre servicios se vuelven política
- #10 *"Los updates compensatorios siempre funcionan"* → sagas
- #11 *"La observabilidad es opcional"* → no lo es

Si en la lección 05 las falacias te parecían abstractas, aquí se vuelven la **lista operativa** de lo que tu equipo va a sufrir.

---

## Sagas, coreografía vs orquestación: mencionadas, no mecanizadas

Cuando una operación cruza servicios — *"cobra al usuario + genera la factura + envía el email + desbloquea el acceso"* — pasa algo que en un monolito era trivial (una transacción de base de datos) y ahora es un problema:

- no hay transacción distribuida que funcione bien
- no hay "rollback" real (falacia #10)

La respuesta conceptual: **sagas**. Una saga es una secuencia de operaciones locales, cada una con una **operación compensatoria** en caso de fallo. Hay dos formas:

- **Coreografía** — cada servicio publica un evento al terminar, el siguiente lo consume. No hay coordinador central.
- **Orquestación** — un coordinador central dirige la secuencia, llama a cada servicio en orden, maneja los fallos.

**Ambas son caras.** Ambas requieren decisiones explícitas (ADRs). Este módulo **no te enseña a implementarlas** — pero tienes que saber que **existen** y que son uno de los costos ocultos de microservicios.

Regla: si tu sistema tiene **más de 2 sagas**, probablemente los cortes de tus bounded contexts están mal.

---

## Concepto nombrado

**Microservicios** son un estilo arquitectónico donde el sistema se parte en servicios independientes, cada uno dueño de su data, desplegables independientemente, comunicándose por red.

**Bounded contexts** son el principio que guía **dónde cortar**: frontera dentro de la cual un concepto tiene significado único y consistente.

Microservicios **no son default**. Son una respuesta a problemas específicos (independencia de equipos, ritmos de cambio distintos, escalas asimétricas). Usarlos cuando el problema no existe multiplica los costos sin entregar el beneficio.

---

## Pregunta del por qué

Vuelve a las dos frases del CTO (4 personas vs 50 personas). Contéstate:

- ¿Qué problema específico resuelve microservicios en el equipo de 50? ¿Cómo lo nombras?
- ¿Qué problema específico **no** resuelve en el equipo de 4?
- Si el equipo de 50 estuviera organizado como **un solo equipo grande** (sin sub-equipos independientes), ¿cambiaría tu análisis?

---

:::exercise{title="Decompón el chatbot en bounded contexts"}
Toma el chatbot del curso y:

1. Identifica **al menos 3 bounded contexts**. Para cada uno:
   - Nombre
   - Qué data posee (con qué queda dueño)
   - Qué operaciones expone en su API pública

2. Identifica **al menos 1 punto de integración entre contextos**:
   - Qué contexto pide qué del otro
   - ¿Es síncrono (REST/gRPC) o asíncrono (evento)? ¿Por qué?

3. **Aplica las 2 heurísticas** (una base por servicio; sin redeploy coordinado). ¿Tu decomposición las pasa? ¿Qué fallas identificas?

4. **Calcula el costo operativo nuevo**: lista al menos 3 artefactos operativos nuevos que aparecen por haber cortado (además del monolito modular).

Evaluación:

- ¿Los contextos son de **dominio**, no de entidad técnica?
- ¿Nombraste la data y los bordes explícitamente?
- ¿Las dos heurísticas están aplicadas y comentadas (no solo invocadas)?
- ¿El conteo de costos es realista?
:::

---

## Cierre

Ya conoces los estilos (06) y la decomposición más difícil de los cinco (esta lección). La siguiente pregunta es la central del módulo: **¿cómo eliges?**. No es una receta. Es un proceso. Lección 08.
