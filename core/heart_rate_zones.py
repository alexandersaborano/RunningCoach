"""Cálculos explícitos de zonas de frequência cardíaca."""

from collections.abc import Sequence


def calcular_zonas_hrr(
    fc_maxima: int | float,
    fc_repouso: int | float,
    percentagens: Sequence[float] = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
) -> list[int]:
    """Calcula limites superiores por Karvonen/%HRR."""
    try:
        maxima = float(fc_maxima)
        repouso = float(fc_repouso)
    except (TypeError, ValueError) as exc:
        raise ValueError("FC máxima e FC de repouso devem ser numéricas.") from exc
    if maxima <= repouso or repouso < 0:
        raise ValueError("FC máxima deve ser superior à FC de repouso.")
    if not percentagens or any(not 0 < float(percentagem) <= 1 for percentagem in percentagens):
        raise ValueError("As percentagens devem estar entre 0 e 1.")
    reserva = maxima - repouso
    return [round(repouso + float(percentagem) * reserva) for percentagem in percentagens]
