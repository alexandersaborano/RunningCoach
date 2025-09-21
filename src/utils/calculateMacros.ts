// src/utils/calculateMacros.ts

type UserSettings = {
  pesoKg: number;
  proteinaPorKg: number;
  gorduraPorKg: number;
  caloriasDiaTreino: number;
  caloriasDiaDescanso: number;
  diaTreino: boolean;
};

export function calcularMetasDiarias(settings: UserSettings) {
  const {
    pesoKg,
    proteinaPorKg,
    gorduraPorKg,
    caloriasDiaTreino,
    caloriasDiaDescanso,
    diaTreino,
  } = settings;

  if (!pesoKg || pesoKg <= 0) {
    return null; // Ou lançar erro, ou outro comportamento
  }

  const caloriasTotais = diaTreino ? caloriasDiaTreino : caloriasDiaDescanso;

  const proteinaGramas = pesoKg * proteinaPorKg;
  const gorduraGramas = pesoKg * gorduraPorKg;

  const caloriasProteina = proteinaGramas * 4;
  const caloriasGordura = gorduraGramas * 9;

  const caloriasRestantes = caloriasTotais - (caloriasProteina + caloriasGordura);

  const hidratosGramas = caloriasRestantes > 0 ? caloriasRestantes / 4 : 0;

  return {
    caloriasTotais,
    proteinaGramas: +proteinaGramas.toFixed(1),
    gorduraGramas: +gorduraGramas.toFixed(1),
    hidratosGramas: +hidratosGramas.toFixed(1),
  };
}
