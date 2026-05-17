---
title: "Arquitectura de Software"
---

# Arquitectura de Software

En las secciones 16 a 19 aprendiste a **construir**: cómo correr cómputo (16), dónde guardar datos (17), cómo hablar entre servicios (18) y cómo diseñar APIs durables (19). Tienes vocabulario técnico para las piezas.

Lo que todavía no tienes es vocabulario para **la forma del sistema completo**:

- ¿Por qué este estilo y no otro?
- ¿Qué trade-off implica cada decisión?
- ¿Cuándo un "buen módulo" deja de serlo?
- ¿Cómo justificas — y dejas registro — de una decisión que sobreviva seis meses de rotación del equipo?

Esta sección cubre ese hueco. Está basada en Richards & Ford, *Fundamentals of Software Architecture* (2nd ed., 2023), pero no es un resumen del libro. Es **la mínima cantidad de vocabulario** que necesitas para razonar sobre arquitectura como disciplina.

---

## El chatbot, ahora anotado con características

Venimos siguiendo el mismo sistema desde §16. En cada sección le agregamos una capa distinta:

- §16 puso **cómputo** en las cajas.
- §17 puso **almacenamiento** en las cajas.
- §18 puso **protocolos** en las flechas.
- §19 puso **contratos** en las flechas.
- §20 pone **características arquitectónicas** en las cajas y en el sistema completo.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     ARQUITECTURA DE UN CHATBOT LLM                           │
│                     (ahora vista como sistema con -ilidades)                 │
│                                                                              │
│  ┌──────────┐     ┌──────────┐     ┌─────────────────────┐                   │
│  │ Usuario  │────▶│ Frontend │────▶│ API del chatbot      │                  │
│  │ browser  │     │ React    │     │ lat p95 < 500ms      │                  │
│  └──────────┘     └──────────┘     │ disponibilidad 99.9% │                  │
│                                    └──────────┬───────────┘                  │
│                                               │                              │
│                                               ▼                              │
│                                    ┌─────────────────────┐                   │
│                                    │ Gateway / borde      │                  │
│                                    │ auditable, seguro    │                  │
│                                    └──────────┬───────────┘                  │
│                                               │                              │
│                                               ▼                              │
│                                    ┌─────────────────────┐                   │
│                                    │ Model server         │                  │
│                                    │ escalable, costoso   │                  │
│                                    └─────────────────────┘                   │
│                                                                              │
│  Preguntas nuevas:                                                           │
│  - ¿Qué característica optimiza este sistema? ¿Qué sacrifica?                │
│  - ¿Este sistema es un monolito, event-driven, microservices? ¿Por qué?      │
│  - ¿Qué decisiones hay escritas y cuáles viven solo en la cabeza del equipo? │
│  - ¿Dónde están los módulos dolorosos de cambiar? ¿Por qué lo son?           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Cómo se enseña esta sección

Cada lección sigue la misma forma: **tensión → patrón de razonamiento → concepto nombrado → pregunta del por qué + kata**.

1. **Tensión**: dos respuestas plausibles a la misma pregunta. No hay respuesta correcta obvia.
2. **Patrón de razonamiento**: la heurística que te lleva a elegir, antes de nombrar el concepto.
3. **Concepto nombrado**: recién aquí aparece el término técnico — como etiqueta de algo que ya entendiste.
4. **Por qué + kata**: aplicación al chatbot (o a tu propio proyecto), **graded por la legibilidad del razonamiento, no por la respuesta**.

### Por qué graded por razonamiento

Arquitectura es disciplina de juicio bajo ambigüedad. Un estudiante que cita las 7 formas de cohesión pero no sabe por qué funcional le gana a secuencial en un caso concreto no aprendió nada transferible. El kata pide:

- **Legibilidad del razonamiento** — ¿se reconstruye el "por qué" en 3 oraciones?
- **Trade-off explícito** — ¿nombraste lo que sacrificaste?
- **Trazabilidad al concepto** — ¿el razonamiento cita una característica, una falacia, un nivel de conectividad?

No graded: qué estilo elegiste, si tu ADR coincide con "la respuesta oficial" (no existe), si tu ranking de características matchea el del instructor.

---

## Progresión del módulo

Se enseña en dos clases. La primera construye vocabulario. La segunda aplica ese vocabulario a estilos concretos.

### Clase 1 — Vocabulario

| Archivo | Pregunta que responde |
|---------|-----------------------|
| `01_fundamentos_arquitectura` | ¿Qué es arquitectura, en serio? ¿Qué la distingue de diseño? |
| `02_modularidad_y_acoplamiento` | ¿Por qué este módulo duele cambiarlo? ¿Cómo lo mides antes de que duela? |
| `03_caracteristicas_arquitectonicas` | ¿Qué optimiza este sistema? ¿Cómo eliges entre 30 candidatos? |
| `04_decisiones_arquitectonicas_adr` | ¿Cómo dejas registro de una decisión que va a sobrevivir al equipo? |
| `05_sistemas_distribuidos_fundamentos` | ¿Cuándo la "solución" distribuida multiplica el problema? |

### Clase 2 — Estilos

| Archivo | Pregunta que responde |
|---------|-----------------------|
| `06_estilos_galeria` | ¿Qué formas toma la misma idea de "separar por responsabilidad"? |
| `07_microservicios_y_bounded_contexts` | ¿Cómo decides dónde cortar el sistema? ¿Cuándo no cortar? |
| `08_elegir_un_estilo` | ¿Cómo llegas de "este sistema" a "este estilo" sin recetario? |
| `09_sintesis_y_arbol_de_decision` | ¿Qué aprendiste que no sabías al empezar? |

### Apéndices (opcional)

| Archivo | Pregunta que responde |
|---------|-----------------------|
| `a_generative_ai_y_arquitectura` | ¿Cómo razonas sobre arquitectura cuando uno de los componentes es un LLM — y cómo **no** delegar el juicio arquitectónico al LLM? |

---

## Notebooks

| Notebook | Tema | Tiempo est. |
|----------|------|-------------|
| [01 — Zona de dolor](./code/01_zona_de_dolor.ipynb) | Medir acoplamiento/abstracción en un codebase real con `ast` | ~30 min |
| [02 — Radar de características](./code/02_radar_caracteristicas.ipynb) | Comparar tres variantes del chatbot por -ilidades | ~25 min |
| [03 — Galería de estilos](./code/03_galeria_estilos.ipynb) | Renderizar los estilos desde descripción estructurada | ~20 min |

Los notebooks abren con una tensión y cierran con una pregunta del por qué, como las lecciones.

---

## Terminología: por qué decimos "características arquitectónicas" y no "requisitos no funcionales"

El libro rechaza deliberadamente el término *non-functional requirements*. El argumento:

> Llamar "no funcional" a lo que suele ser lo **más importante** del sistema — latencia, disponibilidad, seguridad, evolución — es degradante y erróneo.

Adoptamos la terminología del libro. Si ves **"requisitos no funcionales"** en literatura hispana o en tu trabajo, es el mismo concepto. Usamos **"características arquitectónicas"** porque es el nombre que se está volviendo estándar.

### Glosario de términos que usamos (y alternativas que verás por ahí)

| Término que usamos | Qué significa | Otras formas que verás |
|--------------------|---------------|------------------------|
| Característica arquitectónica | "-ilidad" del sistema (latencia, seguridad, modificabilidad...) | Requisito no funcional, cualidad, atributo de calidad |
| Estilo | Topología gruesa (microservicios, layered, event-driven) | Arquitectura (ambiguo), patrón macro |
| Patrón | Solución fina reutilizable (circuit breaker, strangler fig) | (mismo término) |
| Conectividad | *Connascence* — qué tan acopladas están dos piezas | Acoplamiento tipo (ambiguo) |
| ADR | Architectural Decision Record | ADL, Decision Log |
| Bounded context | Frontera de un modelo de dominio coherente | (no tiene buena traducción) |

---

## Antes de empezar, un por qué

Escribe **una oración** que complete:

> **"Una arquitectura es buena cuando ______."**

Guárdala. Volverás a esa oración en la última lección (`09_sintesis_y_arbol_de_decision`). El objetivo no es que aciertes ahora — es que tu respuesta cambie de forma interesante después de leer la sección.

---

## Prerrequisitos

- Haber visto §16 (cómputo), §18 (APIs), §19 (diseño de APIs)
- Saber leer código Python (los notebooks usan `ast` del stdlib, `matplotlib` y `numpy`)

```bash
pip install matplotlib numpy
```

---

## Qué cambia respecto a la sección 19

En §19 la pregunta era:

> "Elegiste esta API. ¿Cómo la haces durable?"

En §20 la pregunta es:

> "Elegiste este sistema. ¿**Es la forma correcta**? ¿Cómo lo justificas? ¿Cómo lo dejas escrito?"

Ese salto — de flecha durable a sistema justificable — es el objeto de estudio de esta sección.
