from statistics import mean


def summarize(times):
    if not times:
        raise ValueError('Não há tempos para calcular as estatísticas.')
    return {
        'min_s': min(times),
        'mean_s': mean(times),
        'max_s': max(times),
    }
