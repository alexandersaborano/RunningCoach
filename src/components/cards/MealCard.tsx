import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { colors, spacing, fontSizes, radius } from "../../theme/theme";
import type { Meal } from "../../types";

type Props = {
  meal: Meal;
  onPressDetails: () => void;
};

export default function MealCard({ meal, onPressDetails }: Props) {
  const totalCalories = meal.foods.reduce((sum, f) => sum + (f.calories * f.quantity) / 100, 0).toFixed(0);
  const totalProtein = meal.foods.reduce((sum, f) => sum + (f.protein * f.quantity) / 100, 0).toFixed(1);
  const totalCarbs = meal.foods.reduce((sum, f) => sum + (f.carbs * f.quantity) / 100, 0).toFixed(1);
  const totalFat = meal.foods.reduce((sum, f) => sum + (f.fat * f.quantity) / 100, 0).toFixed(1);
  const totalQuantity = meal.foods.reduce((sum, f) => sum + f.quantity, 0);

  return (
    <TouchableOpacity onPress={onPressDetails} style={styles.card}>
      <Text style={styles.mealName}>{meal.name}</Text>
      <Text style={styles.macrosText}>
        Calorias: {totalCalories} kcal | Proteína: {totalProtein}g | Carbs: {totalCarbs}g | Gordura: {totalFat}g
      </Text>
      <Text style={styles.quantityText}>Quantidade total: {totalQuantity} g</Text>
      <Text style={styles.itemCount}>
        {meal.foods.length} {meal.foods.length === 1 ? 'alimento' : 'alimentos'}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    padding: spacing.md,
    borderRadius: radius.md,
    marginBottom: spacing.md,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  mealName: {
    fontSize: fontSizes.large,
    fontWeight: "bold",
    marginBottom: spacing.sm,
    color: colors.text,
  },
  macrosText: {
    fontSize: fontSizes.normal,
    color: colors.text,
  },
  quantityText: {
    fontSize: fontSizes.small,
    color: colors.muted,
    marginTop: spacing.xs,
  },
  itemCount: {
    fontSize: fontSizes.small,
    color: colors.muted,
  },
});
