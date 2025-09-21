// src/components/summary/DailySummary.tsx
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, fontSizes, spacing, radius } from "../../theme/theme";
import { useUserSettingsStore } from "../../store/useUserSettingsStore";
import { calcularMetasDiarias } from "../../utils/calculateMacros";
import type { Meal } from "../../types";

// Função para obter cor conforme diferença percentual
function getColorForDifference(diffPercent: number) {
  const absDiff = Math.abs(diffPercent);
  if (absDiff <= 5) return colors.success;       // Verde: dentro 5%
  if (absDiff <= 10) return colors.warning;      // Amarelo: até 10%
  return colors.danger;                           // Vermelho: > 10%
}

type Props = {
  meals: Meal[];
};

export default function DailySummary({ meals }: Props) {
  const settings = useUserSettingsStore();

  const metas = calcularMetasDiarias({
    pesoKg: settings.pesoKg || 0,
    proteinaPorKg: settings.proteinaPorKg,
    gorduraPorKg: settings.gorduraPorKg,
    caloriasDiaTreino: settings.caloriasDiaTreino,
    caloriasDiaDescanso: settings.caloriasDiaDescanso,
    diaTreino: settings.diaTreino,
  });

  if (!metas) return null;

  // Somar o consumo atual das refeições
  let totalCalories = 0,
    totalProtein = 0,
    totalCarbs = 0,
    totalFat = 0;

  meals.forEach((meal) => {
    meal.foods.forEach((food) => {
      totalCalories += (food.calories * food.quantity) / 100;
      totalProtein += (food.protein * food.quantity) / 100;
      totalCarbs += (food.carbs * food.quantity) / 100;
      totalFat += (food.fat * food.quantity) / 100;
    });
  });

  // Função para calcular diferença percentual = (consumo - meta) / meta * 100
  const diff = (consumo: number, meta: number) =>
    meta > 0 ? ((consumo - meta) / meta) * 100 : 0;

  const caloriesDiff = diff(totalCalories, metas.caloriasTotais);
  const proteinDiff = diff(totalProtein, metas.proteinaGramas);
  const carbsDiff = diff(totalCarbs, metas.hidratosGramas);
  const fatDiff = diff(totalFat, metas.gorduraGramas);

  // Função para formatar exibição da diferença
  const renderDiffText = (difference: number) => {
    const prefix = difference >= 0 ? "+" : "-";
    return `${prefix}${Math.abs(difference).toFixed(1)}%`;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sumário</Text>
      <View style={styles.row}>
        <Text style={styles.label}>Calorias</Text>
        <Text style={[styles.value, { color: getColorForDifference(caloriesDiff) }]}>
          {totalCalories.toFixed(0)} kcal ({renderDiffText(caloriesDiff)})
        </Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>Proteína</Text>
        <Text style={[styles.value, { color: getColorForDifference(proteinDiff) }]}>
          {totalProtein.toFixed(1)} g ({renderDiffText(proteinDiff)})
        </Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>Hidratos</Text>
        <Text style={[styles.value, { color: getColorForDifference(carbsDiff) }]}>
          {totalCarbs.toFixed(1)} g ({renderDiffText(carbsDiff)})
        </Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>Gordura</Text>
        <Text style={[styles.value, { color: getColorForDifference(fatDiff) }]}>
          {totalFat.toFixed(1)} g ({renderDiffText(fatDiff)})
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.card,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.sm,
    marginBottom: spacing.md,
  },
  title: {
    fontSize: fontSizes.normal,
    fontWeight: "bold",
    color: colors.text,
    marginBottom: spacing.xs,
    textAlign: "center",
  },
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.sm,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: spacing.xs / 2,
  },
  label: {
    fontSize: fontSizes.small,
    color: colors.text,
  },
  value: {
    fontSize: fontSizes.small,
    fontWeight: "bold",
  },
});
