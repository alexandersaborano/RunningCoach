// src/components/UserMacrosGoals.tsx
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, fontSizes, spacing, radius } from "../theme/theme";
import { useUserSettingsStore } from "../store/useUserSettingsStore";
import { calcularMetasDiarias } from "../utils/calculateMacros";

export default function UserMacrosGoals() {
  const settings = useUserSettingsStore();

  const metas = calcularMetasDiarias({
    pesoKg: settings.pesoKg || 0,
    proteinaPorKg: settings.proteinaPorKg,
    gorduraPorKg: settings.gorduraPorKg,
    caloriasDiaTreino: settings.caloriasDiaTreino,
    caloriasDiaDescanso: settings.caloriasDiaDescanso,
    diaTreino: settings.diaTreino,
  });

  if (!metas) {
    return (
      <View style={styles.container}>
        <Text style={styles.warning}>Configure o peso corporal para as metas.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Metas Diárias</Text>
      <View style={styles.row}>
        <Text style={styles.label}>Calorias:</Text>
        <Text style={styles.value}>{metas.caloriasTotais} kcal</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>Proteína:</Text>
        <Text style={styles.value}>{metas.proteinaGramas} g</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>Gordura:</Text>
        <Text style={styles.value}>{metas.gorduraGramas} g</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>Hidratos:</Text>
        <Text style={styles.value}>{metas.hidratosGramas} g</Text>
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
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: spacing.xs / 2,
  },
  label: {
    fontSize: fontSizes.small,
    color: colors.text,
  },
  value: {
    fontSize: fontSizes.small,
    fontWeight: "bold",
    color: colors.text,
  },
  warning: {
    fontSize: fontSizes.small,
    color: colors.danger,
    textAlign: "center",
  },
});
