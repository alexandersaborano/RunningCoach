import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, fontSizes, spacing, radius } from "../../theme/theme";
import { getDailyTotals } from "../../utils/nutritionTotals";
import type { Meal } from "../../types";

type Props = { meals: Meal[] };

export default function DailySummary({ meals }: Props) {
  const { calories, protein, carbs, fat } = getDailyTotals(meals);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>Resumo diário</Text>
      <Text style={styles.totals}>
        Calorias: {calories} kcal
      </Text>
      <Text style={styles.totals}>
        Proteína: {protein} g
      </Text>
      <Text style={styles.totals}>
        Carbs: {carbs} g
      </Text>
      <Text style={styles.totals}>
        Gordura: {fat} g
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
    alignItems: "center"
  },
  title: {
    fontSize: fontSizes.large,
    fontWeight: "bold",
    color: colors.text,
    marginBottom: spacing.sm,
  },
  totals: {
    fontSize: fontSizes.normal,
    color: colors.text,
    marginBottom: spacing.xs,
  },
});
