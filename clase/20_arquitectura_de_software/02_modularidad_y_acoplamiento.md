---
title: "Modularidad y acoplamiento"
---

# Modularidad y acoplamiento

## Tensión

Tienes dos módulos en el chatbot:

- `auth` — verifica tokens, rota secretos, emite sesiones
- `conversation` — arma el historial de mensajes, los manda al modelo

Ambos hoy llaman a `user_repository` para leer datos del usuario.

Un compañero dice: *"Junta estos dos módulos. Siempre cambian juntos cuando cambia el modelo de usuario."*

Otra compañera dice: *"Sepáralos. `auth` es estable, cambia dos veces al año por compliance. `conversation` cambia cada semana. Juntarlos va a forzar redeploys de auth por razones que no tienen nada que ver con auth."*

¿Quién tiene razón? ¿O los dos? ¿O ninguno?

---

## El patrón de razonamiento

Fíjate qué está preguntándose cada uno:

- El primero: *"¿qué cambia junto?"* (lo que en el libro se llama **cohesión** del sistema).
- La segunda: *"¿qué tan grave es que uno te obligue a tocar el otro?"* (lo que se llama **acoplamiento**).

Dos lentes distintas. La misma decisión cambia dependiendo de qué lente priorices. **Este es el ejercicio central de modularidad**: mirar el mismo código desde lentes complementarias.

---

## Lente 1 — Cohesión

*¿Las cosas que viven juntas pertenecen juntas?*

La cohesión mide **qué tan relacionadas están las responsabilidades dentro de un mismo módulo**. Va de peor a mejor:

```
  peor cohesión  ┐
                 │
  1. Coincidental  "están juntas porque sí"   (util.py con todo)
  2. Logical       "están juntas porque son del mismo tipo"
  3. Temporal      "se ejecutan en el mismo momento"
  4. Procedural    "se ejecutan en el mismo orden"
  5. Communicational "trabajan sobre los mismos datos"
  6. Sequential    "la salida de una es la entrada de la otra"
  7. Functional    "hacen juntas una sola cosa bien definida"
                 │
  mejor cohesión ┘
```

### Cuatro ejemplos en el chatbot

| Nivel | Módulo ficticio | Por qué |
|-------|-----------------|---------|
| 1. Coincidental | `utils.py` con `parse_token`, `format_price`, `slugify` | Nada las une salvo que todas son "útiles" |
| 2. Logical | `validators.py` con 40 validadores distintos | Son del mismo tipo pero no se usan juntas |
| 5. Communicational | `conversation.py` que lee/escribe mensajes | Distintas funciones, pero todas operan sobre la misma conversación |
| 7. Functional | `token_verifier.py` que solo verifica JWTs | Una responsabilidad clara, cohesiva |

### Para qué sirve esta escalera

**No es una regla. Es una lente.** Si tu módulo `conversation` se siente en el nivel 5 (communicational), probablemente está bien. Si tu `utils.py` se siente en el 1 (coincidental), el problema no es "mala cohesión" — el problema es que el código te va a doler cuando cambie, porque no tienes manera de predecir qué se rompe.

---

## Lente 2 — Acoplamiento

*¿Cuánto se empujan los módulos cuando cambias uno?*

Dos medidas simples:

- **Acoplamiento aferente (Ca)** — cuántos módulos **entran** a este (quién depende de mí).
- **Acoplamiento eferente (Ce)** — a cuántos módulos **sale** este (de quién dependo yo).

```
           ┌─────────────┐         ┌─────────────┐
           │  frontend   │         │  dashboard  │
           └──────┬──────┘         └──────┬──────┘
                  │                       │
                  ▼                       ▼
                  ┌──────────────────────────┐     Ca(auth) = 2
   Ce(auth) = 3 ──│      auth module         │──── (2 entran)
                  └──────┬────────┬──────┬───┘
                         │        │      │
                         ▼        ▼      ▼
                     ┌────┐   ┌────┐   ┌────┐
                     │db  │   │kms │   │log │
                     └────┘   └────┘   └────┘
```

### Métricas derivadas

Con Ca y Ce puedes calcular tres cosas que, juntas, dibujan una imagen del codebase:

- **Abstracción** $A = \dfrac{\text{clases abstractas}}{\text{clases totales}}$ — qué tan "etéreo" es el módulo (0 = todo concreto, 1 = todo abstracto).
- **Inestabilidad** $I = \dfrac{Ce}{Ca + Ce}$ — qué tan fácil es cambiarlo sin romper a otros (0 = estable, todos dependen de él; 1 = inestable, solo depende de otros).
- **Distancia al main sequence** $D = |A + I - 1|$ — qué tan lejos está del "buen lugar".

El **main sequence** es la línea diagonal donde los módulos son:

- o **abstractos e inestables** (interfaces, puertos) — fáciles de cambiar porque no hay implementación que romper,
- o **concretos y estables** (librerías, utilidades) — nadie las cambia porque mucha gente depende de ellas.

### Las dos zonas dolorosas

![Zona de dolor](./images/zone_of_pain.png)

**Zona de dolor** (low A, low I): módulos **concretos** (tienen implementación real) y **estables** (muchos otros dependen de ellos). Cambiarlos rompe a mucha gente. Ejemplo: un `user_repository` concreto que medio sistema importa directamente.

**Zona de inutilidad** (high A, high I): módulos **abstractos** (puro contrato) y **inestables** (no los usa casi nadie). Existen pero no aportan nada. Ejemplo: una interfaz que solo tiene una implementación y un consumidor.

La lente no te dice qué hacer. Te dice **dónde mirar primero**.

---

## Lente 3 — Conectividad (*connascence*)

Dos piezas están conectadas si **una tiene que saber algo de la otra** para funcionar. La conectividad mide *qué tan doloroso es ese saber*.

Hay dos ejes: estática y dinámica.

![Escalera de conectividad](./images/connascence_ladder.png)

### Conectividad estática (detectable leyendo el código)

De mejor (menos doloroso) a peor:

1. **De nombre (Name)** — dos piezas tienen que estar de acuerdo en cómo se llama un identificador (función, campo). Ejemplo: ambas usan `user_id`. Refactor trivial.
2. **De tipo (Type)** — tienen que estar de acuerdo en el tipo de dato. Ejemplo: ambas tratan `user_id` como string. Refactor manejable.
3. **De significado (Meaning)** — tienen que estar de acuerdo en qué significa un valor. Ejemplo: ambas saben que `status = 1` significa "activo". Peor: cambios silenciosos.
4. **De posición (Position)** — tienen que estar de acuerdo en el **orden** de los argumentos/campos. Ejemplo: `send(user_id, msg, urgent)` — si alguien invierte dos, el bug no se ve. Doloroso.
5. **De algoritmo (Algorithm)** — tienen que implementar **el mismo algoritmo** para estar en sincronía. Ejemplo: dos servicios que hashan passwords con la misma función de derivación. Si uno la cambia, nada se compila mal, pero los usuarios no pueden login.

### Conectividad dinámica (solo se ve en runtime)

Peor que la estática, porque el compilador no te puede ayudar:

6. **De ejecución (Execution)** — módulo A tiene que ejecutarse **antes** que B. Ejemplo: `init_database()` antes que cualquier query.
7. **De tiempo (Timing)** — tienen que sincronizarse en el tiempo. Ejemplo: un timeout que asume que B responde en < 500ms.
8. **De valores (Values)** — dos valores tienen que cambiar juntos. Ejemplo: actualizar saldo y registro de transacción en la misma operación atómica.
9. **De identidad (Identity)** — dos módulos tienen que referirse al **mismo objeto** (no dos copias). Ejemplo: un lock compartido.

### Cómo se usa

La conectividad es una **escalera**: el refactor típico es **bajar un rung**.

Ejemplo: dos servicios se comunican pasando una lista de booleanos donde el orden importa. Eso es **Position** (malo). Si cambias la lista por un objeto con nombres (`{urgent: true, important: false}`), bajas a **Name** (mejor). Mismo código, mejor conectividad.

---

## Cohesión y acoplamiento al mismo tiempo

Un sistema bien modularizado tiende a:

- **alta cohesión dentro** — las responsabilidades que viven juntas pertenecen juntas
- **bajo acoplamiento entre** — los módulos no se empujan cuando cambias uno

Los dos ejes dan cuatro zonas:

```
                      cohesión
                        ↑
                        │
       alta cohesión    │    alta cohesión
       bajo acoplamiento│    alto acoplamiento
       ✓ target         │    ✗ bolas de spaghetti cohesivas
       ─────────────────┼──────────────────────────── acoplamiento
       baja cohesión    │    baja cohesión
       bajo acoplamiento│    alto acoplamiento
       ✗ módulos inútiles│   ✗ big ball of mud
                        │
```

![Matriz cohesión/acoplamiento](./images/cohesion_coupling_matrix.png)

---

## Concepto nombrado: modularidad como **lente**, no como ley

"Modularidad buena" no es un checklist. Es tres lentes complementarias (cohesión, acoplamiento, conectividad) que, aplicadas al mismo código, te dejan ver **dónde el sistema te va a doler cuando cambie**.

La utilidad práctica es identificar **dónde refactorizar primero** — no construir el sistema "perfectamente modular" desde cero.

---

## Pregunta del por qué

Vuelve a la tensión inicial:

> *"Junta estos dos módulos. Siempre cambian juntos."* vs *"Sepáralos. Tienen ritmos de cambio distintos."*

Ahora contéstate:

- ¿Qué lente prioriza cada compañero?
- ¿Hay alguna lente que ninguno de los dos está usando?
- Si aplicas la lente de **conectividad**, ¿encuentras algo que ninguno de los dos notó?

---

:::exercise{title="Zona de dolor en tu propio código"}
Corre el notebook [`01_zona_de_dolor.ipynb`](./code/01_zona_de_dolor.ipynb) sobre el directorio `uu_framework/scripts/`. Responde:

1. ¿Cuál es el módulo con mayor **distancia al main sequence**?
2. ¿Está en Zona de Dolor o Zona de Inutilidad? ¿Cómo lo sabes?
3. Lee ese módulo 5 minutos. ¿Tiene sentido que esté donde está (es, genuinamente, una librería estable concreta que debería ser estable)? ¿O el código huele a que el autor no notó que tanta gente lo importa?

Evaluación:

- ¿Tu respuesta al (3) cita al menos un detalle específico del código, no solo el número?
- ¿Identificas cuándo el número miente (ej: es un `__init__.py` inflado artificialmente)?
- ¿Propones **un** refactor concreto que bajaría la distancia?
:::

---

## Cierre

Ya tienes lentes para responder *"¿qué pieza del sistema duele?"* La siguiente lección cambia la escala de análisis del **módulo** a **todo el sistema**: *¿qué está optimizando este sistema en su conjunto, y qué está sacrificando?* Eso son las **características arquitectónicas**.
