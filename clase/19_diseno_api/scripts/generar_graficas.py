"""
generar_graficas.py
Genera las imagenes del modulo 19 (Diseno de APIs).

Requiere: matplotlib, numpy
Uso:
  python3 clase/19_diseno_api/scripts/generar_graficas.py

Las imagenes se guardan en:
  clase/19_diseno_api/images/
"""

from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
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
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  OK {out}")


def gen_contract_surface():
    labels = ["Wiki suelta", "README", "Ejemplos", "OpenAPI + schema"]
    values = [2, 4, 6, 10]
    colors = [ACCENT1, ACCENT4, ACCENT2, ACCENT5]

    fig, ax = plt.subplots(figsize=(9, 5))
    apply_theme(fig, [ax])
    bars = ax.bar(labels, values, color=colors, edgecolor=BG, linewidth=1.2)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            str(val),
            ha="center",
            va="bottom",
            color=FG,
            fontsize=11,
            fontweight="bold",
        )
    ax.set_ylim(0, 11)
    ax.set_ylabel("Fuerza del contrato")
    ax.set_title("Superficie de contrato: informal vs verificable", fontsize=14, fontweight="bold")
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5, axis="y")
    plt.tight_layout()
    save(fig, "contract_surface.png")


def gen_breaking_vs_nonbreaking():
    labels = ["Agregar opcional", "Endpoint nuevo", "Quitar campo", "Cambiar tipo", "Renombrar"]
    values = [1, 2, 9, 10, 9]
    colors = [ACCENT5, ACCENT2, ACCENT3, ACCENT3, ACCENT4]

    fig, ax = plt.subplots(figsize=(10, 5))
    apply_theme(fig, [ax])
    bars = ax.barh(labels, values, color=colors, edgecolor=BG, linewidth=1.2)
    for bar, val in zip(bars, values):
        ax.text(val + 0.15, bar.get_y() + bar.get_height() / 2, str(val), color=FG, va="center")
    ax.set_xlim(0, 11)
    ax.set_xlabel("Riesgo de ruptura")
    ax.set_title("Cambios non-breaking vs breaking", fontsize=14, fontweight="bold")
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5, axis="x")
    ax.invert_yaxis()
    plt.tight_layout()
    save(fig, "breaking_vs_nonbreaking.png")


def gen_canary_rollout():
    traffic = np.array([0, 10, 25, 50, 100])
    error_new = np.array([0.0, 0.7, 0.8, 1.2, 1.1])

    fig, ax1 = plt.subplots(figsize=(9, 5))
    apply_theme(fig, [ax1])
    ax2 = ax1.twinx()
    ax2.set_facecolor(BG)
    ax2.tick_params(colors=FG, labelsize=10)
    ax2.yaxis.label.set_color(FG)
    for spine in ax2.spines.values():
        spine.set_edgecolor(GRID_CLR)

    line1 = ax1.plot(
        traffic,
        traffic,
        color=ACCENT2,
        linewidth=2.5,
        marker="o",
        label="Trafico enviado a v2 (%)",
    )[0]
    line2 = ax2.plot(
        traffic,
        error_new,
        color=ACCENT3,
        linewidth=2.5,
        marker="s",
        label="Error rate observado en v2 (%)",
    )[0]

    ax1.set_xlabel("Porcentaje de trafico hacia v2")
    ax1.set_ylabel("Trafico canary (%)")
    ax2.set_ylabel("Error rate de v2 (%)")
    ax1.set_title("Canary rollout y salud de la nueva version", fontsize=14, fontweight="bold")
    ax1.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5)

    legend = ax1.legend(
        [line1, line2],
        [line1.get_label(), line2.get_label()],
        loc="upper left",
        fontsize=9,
        facecolor=BG,
        edgecolor=GRID_CLR,
        labelcolor=FG,
    )
    for text in legend.get_texts():
        text.set_color(FG)

    ax1.annotate(
        "Mas trafico a v2",
        xy=(50, 50),
        xytext=(18, 68),
        color=FG,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1.2),
    )
    ax2.annotate(
        "Si esta linea sube demasiado,\nse frena el rollout",
        xy=(50, 1.2),
        xytext=(62, 0.88),
        color=FG,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=ACCENT3, lw=1.2),
    )
    plt.tight_layout()
    save(fig, "canary_rollout.png")


def gen_latency_error_budget():
    labels = ["v1 estable", "v2 10%", "v2 50%", "v2 100%"]
    latency = [420, 435, 510, 500]
    error = [0.5, 0.7, 1.8, 1.4]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 5))
    apply_theme(fig, [ax1])
    ax2 = ax1.twinx()
    ax2.set_facecolor(BG)
    ax2.tick_params(colors=FG, labelsize=10)
    ax2.yaxis.label.set_color(FG)
    for spine in ax2.spines.values():
        spine.set_edgecolor(GRID_CLR)

    bars1 = ax1.bar(
        x - width / 2,
        latency,
        width,
        color=ACCENT2,
        label="Barra azul: latencia p95 (ms)",
        edgecolor=BG,
        linewidth=1.1,
    )
    bars2 = ax2.bar(
        x + width / 2,
        error,
        width,
        color=ACCENT3,
        label="Barra roja: error rate (%)",
        edgecolor=BG,
        linewidth=1.1,
    )

    for bar, val in zip(bars1, latency):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 8,
            f"{val} ms",
            ha="center",
            va="bottom",
            color=FG,
            fontsize=9,
            fontweight="bold",
        )

    for bar, val in zip(bars2, error):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            color=FG,
            fontsize=9,
            fontweight="bold",
        )

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Latencia p95 (ms)")
    ax2.set_ylabel("Error rate (%)")
    ax1.set_title("Latencia y error budget durante el rollout", fontsize=14, fontweight="bold")
    ax1.grid(color=GRID_CLR, linestyle="--", linewidth=0.5, alpha=0.5, axis="y")

    legend = ax1.legend(
        [bars1, bars2],
        ["Barra azul: latencia p95 (ms)", "Barra roja: error rate (%)"],
        loc="upper left",
        fontsize=9,
        facecolor=BG,
        edgecolor=GRID_CLR,
        labelcolor=FG,
    )
    for text in legend.get_texts():
        text.set_color(FG)

    ax2.annotate(
        "Aqui el rollout se ve riesgoso:\nsuben latencia y errores",
        xy=(2 + width / 2, 1.8),
        xytext=(2.45, 1.45),
        color=FG,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=ACCENT3, lw=1.2),
    )
    plt.tight_layout()
    save(fig, "latency_error_budget.png")


def main():
    print(f"Directorio de imagenes: {IMAGES_DIR}\n")
    gen_contract_surface()
    gen_breaking_vs_nonbreaking()
    gen_canary_rollout()
    gen_latency_error_budget()
    print("\nTodas las imagenes generadas correctamente.")


if __name__ == "__main__":
    main()
