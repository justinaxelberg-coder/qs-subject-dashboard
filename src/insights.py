"""Geração automática de insights em linguagem natural a partir dos dados."""

from src.constants import INDICATOR_NAMES


def decomposition_insight(contributions: dict, subject: str) -> str:
    """Gera um insight de destaque para a aba Decomposição do Escore."""
    if not contributions:
        return f"Sem dados disponíveis para {subject}."

    totals = {uni: sum(c.values()) for uni, c in contributions.items()}
    top_uni = max(totals, key=totals.get)
    top_total = totals[top_uni]
    top_contribs = contributions[top_uni]

    strongest = max(top_contribs, key=top_contribs.get)
    weakest = min(top_contribs, key=top_contribs.get) if len(top_contribs) > 1 else strongest

    strongest_name = INDICATOR_NAMES.get(strongest, strongest)
    weakest_name = INDICATOR_NAMES.get(weakest, weakest)

    return (
        f"Em {subject}, o escore ponderado total de {top_uni} ({top_total:.1f}) "
        f"é impulsionado principalmente por {strongest_name} ({top_contribs[strongest]:.1f} pts). "
        f"O contribuinte ponderado mais fraco é {weakest_name} "
        f"({top_contribs[weakest]:.1f} pts)."
    )


def gap_analysis_insight(
    focus_uni: str, subject: str, opportunities: list[dict]
) -> str:
    """Gera um insight de destaque para a aba Análise de Lacunas."""
    if not opportunities:
        return (
            f"{focus_uni} lidera ou empata com as pares em todos os indicadores "
            f"em {subject}. Nenhuma oportunidade de melhoria identificada."
        )

    top = opportunities[0]
    indicator_name = INDICATOR_NAMES.get(top["indicator"], top["indicator"])
    return (
        f"A maior oportunidade de {focus_uni} em {subject} é "
        f"{indicator_name}, valendo até {top['gap_points']:.1f} "
        f"pontos ponderados em relação às pares paulistas."
    )


def benchmarking_insight(
    focus_uni: str, faculty_area: str, peer_deltas: dict
) -> str:
    """Gera um insight de destaque para a aba Benchmarking com Pares."""
    if not peer_deltas:
        return f"Sem dados de pares disponíveis para {focus_uni} em {faculty_area}."

    indicator_counts = {}
    for peer, deltas in peer_deltas.items():
        for indicator, delta in deltas.items():
            if delta > 0:
                indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1

    if not indicator_counts:
        return (
            f"{focus_uni} lidera todas as pares em todos os indicadores "
            f"em {faculty_area}."
        )

    most_common = max(indicator_counts, key=indicator_counts.get)
    count = indicator_counts[most_common]
    total_peers = len(peer_deltas)
    indicator_name = INDICATOR_NAMES.get(most_common, most_common)

    return (
        f"{count} de {total_peers} pares superam {focus_uni} em "
        f"{indicator_name} na área de {faculty_area}, sugerindo este como "
        f"um foco prioritário de melhoria."
    )
