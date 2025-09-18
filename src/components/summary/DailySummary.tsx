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
    borderRadius: radius.sm,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
    flexDirection: "row",
    justifyContent: "space-around",
  },
  title: {
    display: "none", // esconder título para economizar espaço
  },
  totals: {
    fontSize: fontSizes.small,
    color: colors.text,
  },
});
