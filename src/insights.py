"""Geração automática de insights em linguagem natural a partir dos dados."""

from src.constants import INDICATOR_NAMES


def decomposition_insight(contributions: dict, subject: str) -> str:
    """Gera um insight de composição para a aba Decomposição do Escore."""
    if not contributions:
        return f"Sem dados disponíveis para {subject}."

    totals = {uni: sum(c.values()) for uni, c in contributions.items()}
    top_uni = max(totals, key=totals.get)
    top_total = totals[top_uni]
    top_contribs = contributions[top_uni]

    reputation_total = top_contribs.get("AR", 0) + top_contribs.get("ER", 0)
    reputation_pct = round(reputation_total / top_total * 100) if top_total > 0 else 0

    return (
        f"Em {subject}, {reputation_pct}% do escore ponderado de {top_uni} "
        f"({top_total:.1f} pts) é determinado por indicadores de reputação "
        f"institucional (AR + ER)."
    )


def gap_analysis_insight(
    focus_uni: str, subject: str, opportunities: list[dict]
) -> str:
    """Gera um insight de perfil para a aba Perfil dos Indicadores."""
    if not opportunities:
        return (
            f"{focus_uni} está acima ou igual à média das pares "
            f"em todos os indicadores em {subject}."
        )

    top = opportunities[0]
    indicator_name = INDICATOR_NAMES.get(top["indicator"], top["indicator"])
    return (
        f"Em {subject}, {focus_uni} apresenta a maior diferença de perfil "
        f"em {indicator_name}: {top['gap_points']:.1f} pts ponderados "
        f"abaixo da média das pares paulistas."
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
            f"{focus_uni} está acima ou igual a todas as pares "
            f"em todos os indicadores em {faculty_area}."
        )

    most_common = max(indicator_counts, key=indicator_counts.get)
    count = indicator_counts[most_common]
    total_peers = len(peer_deltas)
    indicator_name = INDICATOR_NAMES.get(most_common, most_common)

    return (
        f"{count} de {total_peers} grupos de pares apresentam diferença "
        f"positiva em relação a {focus_uni} em {indicator_name} "
        f"na área de {faculty_area}."
    )
