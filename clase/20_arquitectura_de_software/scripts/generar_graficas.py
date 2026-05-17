"""
generar_graficas.py
Genera las imagenes del modulo 20 (Arquitectura de Software).

Requiere: matplotlib, numpy
Uso:
  python3 clase/20_arquitectura_de_software/scripts/generar_graficas.py

Las imagenes se guardan en:
  clase/20_arquitectura_de_software/images/
"""

from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
except ImportError as e:
    raise SystemExit(f"Falta dependencia: {e}. Instala con: pip install matplotlib numpy")

SCRIPT_DIR = Path(__file__).parent
IMAGES_DIR = SCRIPT_DIR.parent / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

BG = "#1a1a2e"
FG = "#e0e0e0"
ACCENT1 = "#7b2d8b"
ACCENT2 = "#00a8cc"
ACCENT3 = "#e94560"
ACCENT4 = "#f5a623"
ACCENT5 = "#43b581"
GRID_CLR = "#2a2a4e"


def apply_theme(fig, axes):
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(BG)
        ax.tick_params(colors=FG, labelsize=10)
        ax.xaxis.label.set_color(FG)
        ax.yaxis.label.set_color(FG)
        ax.title.set_color(FG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_CLR)


def save(fig, name):
    out = IMAGES_DIR / name
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  OK {out}")


# ---------------------------------------------------------------------------
# 1. Matriz cohesion / acoplamiento
# ---------------------------------------------------------------------------


def gen_cohesion_coupling_matrix():
    fig, ax = plt.subplots(figsize=(9, 7))
    apply_theme(fig, [ax])

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("Acoplamiento entre modulos", fontsize=12)
    ax.set_ylabel("Cohesion dentro del modulo", fontsize=12)
    ax.set_title("Cohesion vs acoplamiento: 4 zonas", fontsize=14, fontweight="bold")

    quadrants = [
        (0, 5, 5, 5, ACCENT5, "TARGET\nalta cohesion\nbajo acoplamiento"),
        (5, 5, 5, 5, ACCENT4, "Bolas de spaghetti\ncohesivas\n(fuerte pero pegado)"),
        (0, 0, 5, 5, ACCENT2, "Modulos inutiles\n(desacoplados pero\nsin identidad)"),
        (5, 0, 5, 5, ACCENT3, "Big ball of mud\n(el peor escenario)"),
    ]
    for x, y, w, h, color, label in quadrants:
        rect = patches.Rectangle((x, y), w, h, facecolor=color, alpha=0.35, edgecolor=GRID_CLR)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color=FG, fontsize=10, fontweight="bold")

    ax.axhline(5, color=GRID_CLR, linewidth=1)
    ax.axvline(5, color=GRID_CLR, linewidth=1)
    ax.grid(False)
    ax.set_xticks([0, 5, 10])
    ax.set_xticklabels(["bajo", "medio", "alto"])
    ax.set_yticks([0, 5, 10])
    ax.set_yticklabels(["baja", "media", "alta"])
    plt.tight_layout()
    save(fig, "cohesion_coupling_matrix.png")


# ---------------------------------------------------------------------------
# 2. Escalera de conectividad (connascence)
# ---------------------------------------------------------------------------


def gen_connascence_ladder():
    static_levels = [
        ("1. Nombre", "ambos usan 'user_id'"),
        ("2. Tipo", "ambos tratan id como string"),
        ("3. Significado", "ambos saben que status=1 es 'activo'"),
        ("4. Posicion", "orden de args importa (send(a, b, c))"),
        ("5. Algoritmo", "ambos hashan con la misma funcion"),
    ]
    dynamic_levels = [
        ("6. Ejecucion", "A se ejecuta antes que B"),
        ("7. Tiempo", "timeout asume B < 500ms"),
        ("8. Valores", "saldo y tx cambian juntos"),
        ("9. Identidad", "dos modulos usan el mismo lock"),
    ]

    fig, ax = plt.subplots(figsize=(11, 9))
    apply_theme(fig, [ax])

    all_levels = list(reversed(dynamic_levels + static_levels))
    y_positions = np.arange(len(all_levels))
    n_static = len(static_levels)

    for i, (name, example) in enumerate(all_levels):
        is_static = i >= len(dynamic_levels)
        color = ACCENT2 if is_static else ACCENT3
        ax.barh(i, 8, color=color, alpha=0.5, edgecolor=GRID_CLR)
        ax.text(0.1, i, name, va="center", color=FG, fontsize=11, fontweight="bold")
        ax.text(3.8, i, example, va="center", color=FG, fontsize=9, style="italic")

    ax.text(
        8.3,
        n_static + len(dynamic_levels) / 2 - 0.5,
        "mejor\n(refactor trivial)",
        va="center",
        color=ACCENT5,
        fontsize=10,
        fontweight="bold",
    )
    ax.text(
        8.3,
        len(dynamic_levels) / 2 - 0.5,
        "peor\n(solo en runtime)",
        va="center",
        color=ACCENT3,
        fontsize=10,
        fontweight="bold",
    )

    ax.axhline(n_static - 0.5, color=GRID_CLR, linewidth=1.5, linestyle="--")
    ax.text(
        4.0,
        n_static - 0.5,
        "  Estatica (se ve leyendo el codigo)  |  Dinamica (solo en runtime)",
        va="bottom",
        ha="center",
        color=FG,
        fontsize=9,
        style="italic",
    )

    ax.set_xlim(0, 11)
    ax.set_ylim(-0.7, len(all_levels) - 0.3)
    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(
        "Escalera de conectividad (connascence): de mejor a peor", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    save(fig, "connascence_ladder.png")


# ---------------------------------------------------------------------------
# 3. Zone of Pain scatter
# ---------------------------------------------------------------------------


def gen_zone_of_pain():
    rng = np.random.default_rng(42)
    a = rng.uniform(0, 1, 22)
    i = rng.uniform(0, 1, 22)
    distances = np.abs(a + i - 1)

    fig, ax = plt.subplots(figsize=(9, 7))
    apply_theme(fig, [ax])

    pain_x = np.array([0, 0.5, 0.5, 0])
    pain_y = np.array([0, 0, 0.5, 0.5])
    ax.fill(pain_x, pain_y, color=ACCENT3, alpha=0.18, label="Zona de dolor")

    useless_x = np.array([0.5, 1.0, 1.0, 0.5])
    useless_y = np.array([0.5, 0.5, 1.0, 1.0])
    ax.fill(useless_x, useless_y, color=ACCENT4, alpha=0.18, label="Zona de inutilidad")

    ax.plot([0, 1], [1, 0], color=ACCENT5, linestyle="--", linewidth=2, label="Main sequence")

    norm = (distances - distances.min()) / (distances.max() - distances.min() + 1e-9)
    colors_point = [(1 - n, n * 0.6, 0.3 + n * 0.3) for n in norm]
    ax.scatter(a, i, c=colors_point, s=90, edgecolors=FG, linewidths=0.8, zorder=5)

    worst_idx = int(np.argmax(distances))
    ax.annotate(
        f"modulo mas doloroso\nD={distances[worst_idx]:.2f}",
        xy=(a[worst_idx], i[worst_idx]),
        xytext=(a[worst_idx] + 0.1, i[worst_idx] + 0.12),
        color=FG,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=ACCENT3, lw=1.2),
    )

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Abstraccion (A)", fontsize=12)
    ax.set_ylabel("Inestabilidad (I)", fontsize=12)
    ax.set_title("Zona de dolor: distancia al main sequence", fontsize=14, fontweight="bold")
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5)

    legend = ax.legend(loc="upper right", facecolor=BG, edgecolor=GRID_CLR, labelcolor=FG, fontsize=9)
    for text in legend.get_texts():
        text.set_color(FG)
    plt.tight_layout()
    save(fig, "zone_of_pain.png")


# ---------------------------------------------------------------------------
# 4. Radar chart de caracteristicas
# ---------------------------------------------------------------------------


def gen_radar_characteristics():
    labels = [
        "Latencia",
        "Costo",
        "Seguridad",
        "Disponibilidad",
        "Modificabilidad",
        "Simplicidad op",
    ]
    n = len(labels)

    variants = {
        "Latency-first": [0.95, 0.35, 0.55, 0.90, 0.70, 0.55],
        "Cost-first": [0.50, 0.95, 0.55, 0.50, 0.60, 0.80],
        "Compliance-first": [0.55, 0.45, 0.95, 0.80, 0.55, 0.40],
    }
    colors = [ACCENT2, ACCENT4, ACCENT3]

    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)

    for (name, values), color in zip(variants.items(), colors):
        vals = values + values[:1]
        ax.plot(angles, vals, color=color, linewidth=2.2, label=name)
        ax.fill(angles, vals, color=color, alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=FG, fontsize=10)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], color=FG, fontsize=8)
    ax.set_ylim(0, 1)
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.6, alpha=0.7)
    ax.spines["polar"].set_color(GRID_CLR)
    ax.set_title(
        "Caracteristicas priorizadas: tres variantes del chatbot",
        fontsize=13,
        fontweight="bold",
        color=FG,
        y=1.1,
    )

    legend = ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.3, 1.05),
        facecolor=BG,
        edgecolor=GRID_CLR,
        labelcolor=FG,
        fontsize=10,
    )
    for text in legend.get_texts():
        text.set_color(FG)
    plt.tight_layout()
    save(fig, "radar_characteristics.png")


# ---------------------------------------------------------------------------
# 5. Galeria de estilos (5 subplots)
# ---------------------------------------------------------------------------


def _style_layered(ax):
    ax.set_title("Layered", color=FG, fontsize=11, fontweight="bold")
    layers = ["Presentacion", "Logica", "Persistencia", "Base de datos"]
    for i, layer in enumerate(layers):
        y = 3 - i
        rect = patches.Rectangle((0.1, y), 1.8, 0.8, facecolor=ACCENT2, alpha=0.5, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(1.0, y + 0.4, layer, ha="center", va="center", color=FG, fontsize=9)
        if i < 3:
            ax.annotate("", xy=(1.0, y), xytext=(1.0, y - 0.2), arrowprops=dict(arrowstyle="->", color=FG, lw=1))


def _style_modular_monolith(ax):
    ax.set_title("Modular monolith", color=FG, fontsize=11, fontweight="bold")
    outer = patches.Rectangle((0.1, 0.3), 1.8, 3.2, facecolor="none", edgecolor=ACCENT5, linewidth=2)
    ax.add_patch(outer)
    ax.text(1.0, 3.65, "servicio unico", ha="center", color=ACCENT5, fontsize=9, style="italic")
    modules = ["auth", "chat", "bill"]
    for i, m in enumerate(modules):
        y = 2.5 - i * 0.9
        rect = patches.Rectangle((0.3, y), 1.4, 0.6, facecolor=ACCENT5, alpha=0.5, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(1.0, y + 0.3, m, ha="center", va="center", color=FG, fontsize=9)


def _style_pipeline(ax):
    ax.set_title("Pipeline", color=FG, fontsize=11, fontweight="bold")
    stages = ["recibe", "valida", "modera", "modelo", "formatea"]
    for i, s in enumerate(stages):
        y = 3.2 - i * 0.65
        rect = patches.Rectangle((0.3, y), 1.4, 0.45, facecolor=ACCENT4, alpha=0.5, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(1.0, y + 0.22, s, ha="center", va="center", color=FG, fontsize=8)
        if i < len(stages) - 1:
            ax.annotate("", xy=(1.0, y), xytext=(1.0, y - 0.2), arrowprops=dict(arrowstyle="->", color=FG, lw=1))


def _style_event_driven(ax):
    ax.set_title("Event-driven", color=FG, fontsize=11, fontweight="bold")
    bus = patches.Rectangle((0.1, 1.8), 1.8, 0.5, facecolor=ACCENT3, alpha=0.5, edgecolor=FG)
    ax.add_patch(bus)
    ax.text(1.0, 2.05, "event bus", ha="center", va="center", color=FG, fontsize=9, fontweight="bold")
    positions = [(0.3, 3.0), (1.1, 3.0), (0.3, 0.8), (1.1, 0.8)]
    names = ["A", "B", "C", "D"]
    for (x, y), name in zip(positions, names):
        rect = patches.Rectangle((x, y), 0.6, 0.5, facecolor=ACCENT3, alpha=0.3, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(x + 0.3, y + 0.25, name, ha="center", va="center", color=FG, fontsize=10)
        y_bus = 2.3 if y > 2 else 1.8
        ax.annotate(
            "",
            xy=(x + 0.3, y_bus),
            xytext=(x + 0.3, y + (0 if y > 2 else 0.5)),
            arrowprops=dict(arrowstyle="->", color=FG, lw=0.8),
        )


def _style_microkernel(ax):
    ax.set_title("Microkernel", color=FG, fontsize=11, fontweight="bold")
    core = patches.Circle((1.0, 2.0), 0.45, facecolor=ACCENT1, alpha=0.6, edgecolor=FG, linewidth=2)
    ax.add_patch(core)
    ax.text(1.0, 2.0, "CORE", ha="center", va="center", color=FG, fontsize=10, fontweight="bold")
    plugin_positions = [(0.15, 3.2), (1.85, 3.2), (0.15, 0.6), (1.85, 0.6)]
    for px, py in plugin_positions:
        plug = patches.Circle((px, py), 0.25, facecolor=ACCENT1, alpha=0.4, edgecolor=FG)
        ax.add_patch(plug)
        ax.annotate("", xy=(1.0, 2.0), xytext=(px, py), arrowprops=dict(arrowstyle="-", color=FG, lw=0.8))


def gen_gallery_styles():
    styles = [
        _style_layered,
        _style_modular_monolith,
        _style_pipeline,
        _style_event_driven,
        _style_microkernel,
    ]
    fig, axes = plt.subplots(1, 5, figsize=(18, 5))
    apply_theme(fig, list(axes))
    for ax, renderer in zip(axes, styles):
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 4)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(GRID_CLR)
        renderer(ax)
    fig.suptitle(
        "Galeria de estilos: 5 topologias distintas",
        color=FG,
        fontsize=15,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    save(fig, "gallery_styles.png")


# ---------------------------------------------------------------------------
# 6. Chatbot en 3 estilos (side-by-side)
# ---------------------------------------------------------------------------


def _chatbot_monolith(ax):
    ax.set_title("Monolito modular", color=FG, fontsize=12, fontweight="bold")
    outer = patches.Rectangle((0.1, 0.3), 2.8, 3.5, facecolor="none", edgecolor=ACCENT5, linewidth=2)
    ax.add_patch(outer)
    ax.text(1.5, 3.95, "1 deploy, 1 base de datos", ha="center", color=ACCENT5, fontsize=9, style="italic")
    names = ["auth", "conversation", "inference", "billing"]
    for i, n in enumerate(names):
        y = 3.0 - i * 0.7
        rect = patches.Rectangle((0.3, y), 2.4, 0.55, facecolor=ACCENT5, alpha=0.5, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(1.5, y + 0.28, n, ha="center", va="center", color=FG, fontsize=10)


def _chatbot_event_driven(ax):
    ax.set_title("Event-driven", color=FG, fontsize=12, fontweight="bold")
    bus = patches.Rectangle((0.1, 1.7), 2.8, 0.5, facecolor=ACCENT3, alpha=0.5, edgecolor=FG)
    ax.add_patch(bus)
    ax.text(1.5, 1.95, "event bus", ha="center", va="center", color=FG, fontsize=10, fontweight="bold")
    positions = [(0.2, 2.8), (1.1, 2.8), (2.0, 2.8), (1.1, 0.5)]
    names = ["auth", "conversation", "inference", "billing"]
    for (x, y), name in zip(positions, names):
        rect = patches.Rectangle((x, y), 0.85, 0.55, facecolor=ACCENT3, alpha=0.4, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(x + 0.425, y + 0.28, name, ha="center", va="center", color=FG, fontsize=9)
        ax.annotate(
            "",
            xy=(x + 0.425, 2.2 if y > 2 else 1.7),
            xytext=(x + 0.425, y + (0 if y > 2 else 0.55)),
            arrowprops=dict(arrowstyle="<->", color=FG, lw=0.8),
        )


def _chatbot_microservices(ax):
    ax.set_title("Microservicios", color=FG, fontsize=12, fontweight="bold")
    positions = [(0.2, 2.8), (1.1, 2.8), (2.0, 2.8), (1.1, 0.8)]
    names = ["auth", "conv", "inf", "billing"]
    for (x, y), name in zip(positions, names):
        rect = patches.Rectangle((x, y), 0.85, 0.6, facecolor=ACCENT4, alpha=0.5, edgecolor=FG)
        ax.add_patch(rect)
        ax.text(x + 0.425, y + 0.3, name, ha="center", va="center", color=FG, fontsize=10)
        db = patches.Ellipse((x + 0.425, y - 0.3), 0.7, 0.25, facecolor=ACCENT4, alpha=0.2, edgecolor=FG)
        ax.add_patch(db)
        ax.text(x + 0.425, y - 0.32, "db", ha="center", va="center", color=FG, fontsize=7)
    for (x1, y1), (x2, y2) in [((0.625, 2.8), (1.525, 2.8)), ((1.525, 2.8), (2.425, 2.8)), ((1.525, 2.8), (1.525, 1.4))]:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-", color=FG, lw=0.8, linestyle=":"))


def gen_chatbot_three_styles():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    apply_theme(fig, list(axes))
    renderers = [_chatbot_monolith, _chatbot_event_driven, _chatbot_microservices]
    for ax, r in zip(axes, renderers):
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 4.2)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color(GRID_CLR)
        r(ax)
    fig.suptitle(
        "El mismo chatbot, 3 estilos — 4 dominios (auth / conversation / inference / billing)",
        color=FG,
        fontsize=13,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    save(fig, "chatbot_three_styles.png")


# ---------------------------------------------------------------------------
# 7. Heat map estilos x caracteristicas
# ---------------------------------------------------------------------------


def gen_heatmap_styles_characteristics():
    chars = [
        "Simplicidad op",
        "Time-to-market",
        "Modificabilidad",
        "Escalabilidad",
        "Extensibilidad",
        "Testabilidad",
        "Tolerancia a fallo",
        "Aislamiento compliance",
        "Desacople de equipos",
    ]
    styles = ["Layered", "Monolito modular", "Pipeline", "Event-driven", "Microkernel", "Microservicios"]

    data = np.array(
        [
            # simpl tt-mkt modif escal exten test tolf comp desac
            [3, 2, 2, 1, 1, 4, 1, 1, 1],  # Layered
            [4, 4, 3, 1, 1, 4, 2, 2, 2],  # Modular monolith
            [3, 3, 4, 2, 2, 5, 3, 2, 3],  # Pipeline
            [2, 2, 4, 4, 2, 3, 4, 2, 4],  # Event-driven
            [3, 2, 3, 2, 5, 3, 3, 3, 3],  # Microkernel
            [1, 1, 4, 5, 3, 3, 4, 5, 5],  # Microservices
        ]
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    apply_theme(fig, [ax])
    cmap = plt.get_cmap("magma")
    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=5)

    ax.set_xticks(np.arange(len(chars)))
    ax.set_xticklabels(chars, rotation=30, ha="right", color=FG, fontsize=10)
    ax.set_yticks(np.arange(len(styles)))
    ax.set_yticklabels(styles, color=FG, fontsize=11)

    for i in range(len(styles)):
        for j in range(len(chars)):
            val = int(data[i, j])
            dot = "●" * val
            ax.text(j, i, dot, ha="center", va="center", color="white" if val < 3 else "black", fontsize=11)

    ax.set_title(
        "Como sirve cada estilo a cada caracteristica (tendencias, no absolutos)",
        fontsize=13,
        fontweight="bold",
    )
    cb = fig.colorbar(im, ax=ax, shrink=0.7)
    cb.ax.yaxis.set_tick_params(color=FG)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color=FG)
    cb.outline.set_edgecolor(GRID_CLR)
    plt.tight_layout()
    save(fig, "heatmap_styles_x_characteristics.png")


# ---------------------------------------------------------------------------
# 8. Decision tree (PNG fallback del Mermaid)
# ---------------------------------------------------------------------------


def gen_decision_tree():
    fig, ax = plt.subplots(figsize=(13, 9))
    apply_theme(fig, [ax])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    def node(x, y, text, color, size=(2.8, 0.9)):
        w, h = size
        rect = patches.FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.05",
            facecolor=color,
            alpha=0.55,
            edgecolor=FG,
            linewidth=1.2,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", color=FG, fontsize=9, fontweight="bold")

    def edge(x1, y1, x2, y2, label=None):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=FG, lw=1.2))
        if label:
            ax.text((x1 + x2) / 2 + 0.1, (y1 + y2) / 2, label, color=FG, fontsize=9, style="italic")

    node(7, 10, "¿Que estas construyendo?", ACCENT1)
    node(3.5, 8, "¿Dominio coherente?\n(todo cambia junto)", ACCENT2)
    node(10.5, 8, "¿Procesamiento por\netapas? o ¿plugins?", ACCENT4)

    node(2, 6, "¿Equipo pequeno\n(< 15 personas)?", ACCENT5)
    node(5, 6, "¿Interaccion\nasincrona dominante?", ACCENT3)
    node(9, 6, "Pipeline", ACCENT4)
    node(12, 6, "Microkernel", ACCENT1)

    node(1, 3.5, "Monolito modular", ACCENT5)
    node(3, 3.5, "¿Madurez\noperativa alta?", ACCENT2)
    node(5, 3.5, "Event-driven", ACCENT3)

    node(2, 1.5, "Microservicios", ACCENT4)
    node(4, 1.5, "Monolito modular\n(prepara para separar)", ACCENT5)

    edge(7, 9.55, 3.5, 8.45, "dominio")
    edge(7, 9.55, 10.5, 8.45, "otros")
    edge(3.5, 7.55, 2, 6.45, "si")
    edge(3.5, 7.55, 5, 6.45, "no")
    edge(2, 5.55, 1, 3.95, "si")
    edge(2, 5.55, 3, 3.95, "no")
    edge(5, 5.55, 5, 3.95, "si")
    edge(5, 5.55, 3, 3.95, "no")
    edge(3, 3.05, 2, 1.95, "si")
    edge(3, 3.05, 4, 1.95, "no")
    edge(10.5, 7.55, 9, 6.45, "etapas")
    edge(10.5, 7.55, 12, 6.45, "plugins")

    ax.set_title("Arbol de decision: primer estilo tentativo", fontsize=14, fontweight="bold")
    ax.text(
        7,
        0.3,
        "Este arbol sugiere un punto de partida. La decision final se defiende con un ADR (leccion 04) y triangulacion (leccion 08).",
        ha="center",
        color=FG,
        fontsize=9,
        style="italic",
    )
    plt.tight_layout()
    save(fig, "decision_tree.png")


# ---------------------------------------------------------------------------
# 9. Through-line chatbot (§16 -> §20)
# ---------------------------------------------------------------------------


def gen_through_line_chatbot():
    fig, ax = plt.subplots(figsize=(14, 7))
    apply_theme(fig, [ax])
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    boxes = [
        (1.5, 4, "Usuario\n(browser)", ACCENT1),
        (5, 4, "Frontend\nReact", ACCENT2),
        (8.5, 4, "API del chatbot", ACCENT5),
        (12, 4, "Model server", ACCENT4),
    ]
    box_annots_16_17 = [None, "compute: CDN edge", "compute: contenedores\nstorage: Postgres", "compute: GPU"]
    box_annots_20 = [None, "char: latencia p50", "char: disp 99.9%\nlat p95 < 500ms", "char: escalabilidad,\ncosto"]

    for (x, y, text, color), c16, c20 in zip(boxes, box_annots_16_17, box_annots_20):
        rect = patches.FancyBboxPatch(
            (x - 1.2, y - 0.6),
            2.4,
            1.2,
            boxstyle="round,pad=0.05",
            facecolor=color,
            alpha=0.55,
            edgecolor=FG,
            linewidth=1.5,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", color=FG, fontsize=10, fontweight="bold")
        if c16:
            ax.text(x, y + 1.3, c16, ha="center", va="bottom", color=ACCENT2, fontsize=8, style="italic")
        if c20:
            ax.text(x, y - 1.3, c20, ha="center", va="top", color=ACCENT4, fontsize=8, style="italic")

    arrows = [
        (1.5, 4, 5, 4, "HTTPS / WebSocket", "OpenAPI + versionado"),
        (5, 4, 8.5, 4, "REST / SSE", "contratos JSON"),
        (8.5, 4, 12, 4, "gRPC interno", "versionado semantico"),
    ]
    for x1, y1, x2, y2, p_label, c_label in arrows:
        ax.annotate("", xy=(x2 - 1.2, y2), xytext=(x1 + 1.2, y1), arrowprops=dict(arrowstyle="->", color=FG, lw=1.5))
        ax.text((x1 + x2) / 2, y1 + 0.25, p_label, ha="center", color=ACCENT3, fontsize=8, fontweight="bold")
        ax.text((x1 + x2) / 2, y1 - 0.25, c_label, ha="center", color=ACCENT5, fontsize=8, fontweight="bold")

    ax.text(
        0.3,
        7.2,
        "Cajas:  §16 compute,  §17 storage,  §20 caracteristicas + ADRs",
        color=ACCENT2,
        fontsize=10,
        fontweight="bold",
    )
    ax.text(
        0.3,
        6.7,
        "Flechas:  §18 protocolos,  §19 contratos durables",
        color=ACCENT3,
        fontsize=10,
        fontweight="bold",
    )
    ax.set_title(
        "Through-line del chatbot: 4 capas de anotacion (§16 → §20)", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    save(fig, "through_line_chatbot.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print(f"Directorio de imagenes: {IMAGES_DIR}\n")
    gen_cohesion_coupling_matrix()
    gen_connascence_ladder()
    gen_zone_of_pain()
    gen_radar_characteristics()
    gen_gallery_styles()
    gen_chatbot_three_styles()
    gen_heatmap_styles_characteristics()
    gen_decision_tree()
    gen_through_line_chatbot()
    print("\nTodas las imagenes generadas correctamente.")


if __name__ == "__main__":
    main()
