---
title: "Fundamentos de sistemas distribuidos"
---

# Fundamentos de sistemas distribuidos

## Tensión

Tu equipo migró el chatbot a 7 microservicios para *"resolver los problemas de escalabilidad del monolito"*.

Seis meses después:

- los problemas de escalabilidad siguen ahí
- ahora tienes además: deploys acoplados, tracing distribuido complicado, 7 pipelines, 7 dashboards, un día al mes debuggeando timeouts entre servicios, y un on-call pasando pesadillas con retries que causan double-processing de pagos

Tu CTO pregunta: *"¿Por qué esto no funciona?"*

Las dos respuestas plausibles:

1. *"Los microservicios estaban mal hechos. Necesitamos mejores contratos, mejor observabilidad, mejor DevOps."*
2. *"El problema no era escalabilidad — era modularidad. Un monolito modular lo habría resuelto sin crear todos estos problemas nuevos."*

¿Qué respuesta estás dispuesto a defender?

---

## El patrón de razonamiento

Cuando un sistema distribuido **no resuelve los problemas que prometió resolver**, suele ser porque el equipo:

1. No nombró correctamente el problema original (¿era escalabilidad? ¿o era "el código está hecho bola"?).
2. Subestimó el **costo nuevo** que trae la distribución — un costo que no se ve en el diagrama de arquitectura en Miro.
3. Asumió, implícitamente, cosas sobre la red, el tiempo, los updates, la observabilidad — que **no se cumplen**.

El libro llama a ese conjunto de suposiciones las **11 falacias del cómputo distribuido**. Son 11 formas específicas en las que los equipos se engañan a sí mismos cuando deciden distribuir.

El patrón de razonamiento: **antes de distribuir, revisa las 11**. Si tu decisión depende de alguna de ellas siendo verdadera, la decisión probablemente no es sólida.

---

## Monolítico vs distribuido: la decisión más cara

Es casi la primera decisión real que toma un equipo. Todas las demás derivan de ella:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   MONOLÍTICO                     DISTRIBUIDO            │
│   ──────────                     ────────────           │
│                                                         │
│   un proceso                     N procesos             │
│   memoria compartida             red entre ellos        │
│   un deploy                      N deploys              │
│   una base de datos              N bases de datos       │
│   un dashboard                   N dashboards           │
│   bug ≈ stacktrace               bug ≈ análisis de logs │
│   performance ≈ mediciones       performance ≈ tracing  │
│                                  distribuido            │
│                                                         │
│   simple, no escala infinito     escala, costo enorme   │
│   a veces doloroso cambiar       a veces doloroso hacer │
│                                  que funcione           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

Ninguno es mejor en abstracto. El **contexto** decide cuál duele menos.

### Señales de que probablemente sobra monolítico

- equipo pequeño (< 15 ingenieros)
- dominio poco diferenciado (todo cambia junto)
- lanzando al mercado pronto
- cero experiencia operativa en distribuido

### Señales de que probablemente pide distribuido

- equipos independientes con ritmos de cambio distintos
- componentes que **necesitan** recursos distintos (inferencia GPU vs billing CPU)
- escalas muy distintas entre partes (1000x entre ciertos componentes)
- compliance exige aislamiento

---

## Las 11 falacias

Las 8 clásicas son de L. Peter Deutsch (1994). Las 3 nuevas (versionado, updates compensatorios, observabilidad) son agregados de la 2da edición del libro.

Cada falacia tiene la misma forma: *"el equipo actúa como si X fuera verdad. No lo es."*

### Las 8 clásicas

#### 1. *"La red es confiable."*

Los paquetes se pierden. Las conexiones se rompen. Hay particiones de red — a veces una AZ entera se queda ciega del resto por 30 minutos.

**Caso chatbot**: el gateway llama al model-server. Esa llamada puede fallar. Si no manejas el fallo (retry, timeout, fallback, circuit breaker), el frontend se queda pegado con un spinner que nunca termina.

#### 2. *"La latencia es cero."*

Una llamada local toma ~100ns. Una llamada HTTP entre servicios en la misma zona toma ~1ms. Una llamada cross-región toma ~100ms. Eso son **6 órdenes de magnitud**. El código no se da cuenta, pero el usuario sí.

**Caso chatbot**: *"el backend solo consulta 3 servicios antes de responder"*. Cada consulta es 5-10ms. Tres consultas secuenciales son 30ms — que es la mitad del budget de latencia si apuntas a 100ms p50.

#### 3. *"El ancho de banda es infinito."*

No lo es. Transferir un modelo de 7GB entre nodos no es gratis. Stream de video tampoco.

**Caso chatbot**: *"vamos a loggear todas las conversaciones para analytics"*. Con 500k mensajes/día, cada uno de 2KB, eso es 1GB/día solo de logs. El pipeline de analytics ahora es un sistema más.

#### 4. *"La red es segura."*

Entre dos servicios dentro del data center, un MITM es posible si alguien tiene acceso interno. El término **zero trust** existe porque "red interna = red confiable" era falacia peligrosa.

**Caso chatbot**: el model-server habla con el backend sin TLS *"porque es red interna"*. Un pentest interno encuentra que cualquiera con acceso al cluster puede leer prompts de usuarios.

#### 5. *"La topología no cambia."*

Servicios se agregan, se quitan, se mueven de zona, se renombran. El código que hard-codea IPs o hostnames va a romperse.

**Caso chatbot**: el backend tiene `MODEL_SERVER_HOST=10.0.3.47` hard-codeado. Operaciones mueve el model server. Downtime de 2 horas porque nadie se acordó del hard-code.

#### 6. *"Solo hay un administrador."*

En un monolito, una persona puede saber *todo*. En un sistema distribuido, cada servicio tiene un dueño distinto, y la coordinación es un problema social más que técnico.

**Caso chatbot**: el equipo de model-inference quiere upgradar la versión del modelo. Eso afecta el formato de respuesta. El equipo de backend no se entera. El frontend empieza a mostrar errores. *"¿Quién tenía que avisar a quién?"*

#### 7. *"Transportar datos es gratis."*

Los egress costs son reales. Las conversiones de formato (JSON → protobuf → JSON) tienen costo de CPU. Serializar y deserializar **es** el 80% del tiempo en muchos sistemas distribuidos.

**Caso chatbot**: cada mensaje pasa por 4 servicios, serializando/deserializando JSON cada vez. 40% del CPU del cluster se va en eso. Ningún equipo lo mide, porque cada equipo solo ve *su* CPU.

#### 8. *"La red es homogénea."*

No lo es. Mezclar AWS + on-prem + un proveedor de modelos externo, cada uno con su latencia, su fiabilidad, sus tiempos de autenticación — eso es heterogeneidad. No se comporta como "una red".

**Caso chatbot**: el frontend está en CloudFront, el backend en ECS, el model server en un proveedor externo. Latencia p99 tiene picos bizarros que nadie explica hasta que alguien se da cuenta de que el proveedor externo tiene timeouts distintos.

### Las 3 agregadas en la 2da edición

#### 9. *"El versionado es fácil."*

En un monolito, agregar un campo a una función es local. En un sistema distribuido, **el servicio que llama** y **el servicio llamado** tienen que acordar la nueva versión. Multiplica por N servicios.

**Caso chatbot**: el equipo de auth agrega un campo `role` al token. Desplegaron auth v2 primero. El backend todavía usa tokens v1. Todos los usuarios quedan deslogueados 20 minutos, hasta que rollback.

#### 10. *"Los updates compensatorios siempre funcionan."*

*"Si algo falla, revertimos."* Suena bonito. En un sistema distribuido, revertir requiere **volver a encontrar** los datos que cambiaron — en N bases de datos, cada una con su lógica, tal vez con eventos ya procesados por consumidores downstream.

**Caso chatbot**: la factura se emite, el email se envía, el modelo responde. Falla el paso 4 (acreditar tokens gratis). *"Revertimos."* Pero el email ya voló. La factura ya está en contabilidad. Rollback real ≠ ctrl-Z.

#### 11. *"La observabilidad es opcional."*

En un monolito, `print()` y un stacktrace bastan. En un sistema distribuido, si no puedes ver dónde se pierde una request entre 7 servicios, el sistema es operativamente ilegible. **Tracing, metrics, structured logs** no son "nice to have" — son **requisito para operar**.

**Caso chatbot**: *"haremos observabilidad en la siguiente fase"*. En producción, llega un bug donde 0.3% de las requests cuelgan. Nadie puede reproducirlo. Pasan 3 semanas antes de que alguien se dé cuenta de que todos los casos comparten un tenant específico.

---

## La anécdota del data-center 2002

El libro cuenta el caso de un equipo que, en 2002, discutía migrar su monolito a una arquitectura distribuida por *"problemas de escalabilidad"*. Fueron al data center. Se dieron cuenta de que **el servidor era de 1998**, con RAM de 2001, corriendo en un disco SCSI al borde de fallar.

Compraron hardware nuevo. Los problemas de escalabilidad desaparecieron.

### La moraleja

"El problema es arquitectónico" suele ser la conclusión **más cómoda** para un equipo de ingeniería (redesign es glamoroso). A menudo el problema es otra cosa — un problema de hardware, de operación, de modularidad dentro del monolito, de priorización.

**La decisión de distribuir no es inherente al problema. Es una respuesta a un problema específico. Si no nombras el problema con precisión, cualquier respuesta — incluyendo "distribuir" — va a fallar.**

Ese es el núcleo de la **Ley 3 de arquitectura** (*"las decisiones viven en un espectro, no son binarias"*): las buenas decisiones son context-dependent — ubican tu caso dentro del espectro. Las malas son default-dependent — eligen un extremo sin mirar el espectro.

---

## Concepto nombrado

Las **11 falacias del cómputo distribuido** son las 11 formas específicas en las que un equipo se engaña a sí mismo cuando decide distribuir un sistema. No son reglas — son **checks** que se aplican cuando estás considerando romper un monolito en partes.

La decisión **monolítico vs distribuido** no es técnica en abstracto: es una respuesta a un problema nombrado. Si no puedes nombrar el problema, ninguna respuesta — ni siquiera una popular — es buena.

---

## Pregunta del por qué

Vuelve a la tensión inicial (los 7 microservicios que no arreglaron nada). Contéstate:

- ¿Cuáles de las 11 falacias probablemente estaban operando sin que el equipo las nombrara?
- ¿Qué hubiera pasado si, en vez de microservicios, el equipo hubiera hecho un monolito modular bien hecho (lección 02)?
- Si hoy fueras el arquitecto, ¿qué ADR escribirías para marcar el antiguo como *Superseded*?

---

:::exercise{title="Identifica 3 falacias en una historia real"}
Lee este post-mortem ficticio pero realista:

> *"El 2025-11-03 sufrimos una caída de 47 minutos en el endpoint `/chat`. La causa raíz fue una actualización del model-server que cambió silenciosamente el formato del campo `tokens_usados` de `int` a `{count: int, cost_cents: int}`. El backend no fue actualizado. Como el backend tiene retry automático, cada llamada fallida se reintentaba 3 veces, triplicando el costo. El sistema de billing, al detectar la inconsistencia, lanzó compensating updates para revertir los cargos erróneos — pero los emails de factura ya se habían mandado a 2300 usuarios. Recuperación requirió rollback manual + mensaje a los usuarios afectados."*

Responde:

1. Identifica **3 falacias** de las 11 que operaron en este incidente. Cita cuál y con **una oración** por qué aplica.
2. ¿Qué ADR podría haber prevenido este incidente?
3. ¿En qué orden habrías mitigado las 3 falacias si tuvieras que priorizar?

Evaluación:

- ¿Las 3 falacias son **distintas** y **claramente defendibles**?
- ¿El ADR propuesto es específico (no *"mejor comunicación entre equipos"*)?
- ¿La priorización cita costo, frecuencia o severidad?
:::

---

## Cierre

Cerramos la Clase 1. Hasta aquí construimos el vocabulario:

- **lección 01**: qué es arquitectura (4 dims, 3 leyes, architecture vs diseño).
- **lección 02**: módulos (cohesión, coupling, conectividad).
- **lección 03**: sistema completo (características arquitectónicas).
- **lección 04**: cómo dejar registro (ADRs y antipatrones).
- **lección 05**: la decisión más cara (distribuido vs no, 11 falacias).

En la Clase 2 aplicamos este vocabulario a **estilos concretos**: qué formas reales toma la arquitectura, cómo decidir entre ellas, y cómo dejar escrito el por qué.
