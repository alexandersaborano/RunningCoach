import type { Meal } from "../types";

export function getDailyTotals(meals: Meal[]) {
  let calories = 0;
  let protein = 0;
  let carbs = 0;
  let fat = 0;
  meals.forEach(meal => {
    meal.foods.forEach(f => {
      calories += (f.calories * f.quantity) / 100;
      protein += (f.protein * f.quantity) / 100;
      carbs += (f.carbs * f.quantity) / 100;
      fat += (f.fat * f.quantity) / 100;
    });
  });
  return {
    calories: Math.round(calories),
    protein: +protein.toFixed(1),
    carbs: +carbs.toFixed(1),
    fat: +fat.toFixed(1)
  };
}
