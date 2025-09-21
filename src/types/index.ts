export type FoodData = {
  id: string;
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
};

export type Food = FoodData & {
  quantity: number;
};

export type Meal = {
  id: string;
  name: string;
  foods: Food[];
};

export type DailyMeals = {
  [date: string]: Meal[];
};

export type NutritionStackParamList = {
  NutritionHome: undefined;
  MealDetails: { meal: Meal; date: string };
  AddFood: { mealId: string; date: string };
  UserSettings: undefined;
};
