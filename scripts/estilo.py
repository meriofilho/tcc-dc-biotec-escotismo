"""Estilo comum das figuras do TCC."""
import matplotlib as mpl

AREA_COR = {
    "Ciências Biológicas": "#2E8B57",
    "Ciências Exatas": "#E07B39",
    "Ciências Humanas": "#3B6FB6",
    "Tecnologia": "#8E5AA8",
}

# Cores no padrão do manual da UEB (Neurociências, cognição e as especialidades escoteiras, 2023)
BLOOM_NIVEIS = ["Participar", "Lembrar", "Compreender", "Aplicar", "Analisar", "Avaliar", "Criar"]
BLOOM_COR = {
    "Participar": "#D3D3D3",
    "Lembrar": "#FF9FC6",
    "Compreender": "#00A3F5",
    "Aplicar": "#1DB300",
    "Analisar": "#FFD52E",
    "Avaliar": "#F57A0A",
    "Criar": "#FF6550",
}


def aplicar():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "svg.fonttype": "none",
    })


def salvar(fig, caminho_sem_ext):
    fig.savefig(caminho_sem_ext + ".png")
    fig.savefig(caminho_sem_ext + ".svg")
