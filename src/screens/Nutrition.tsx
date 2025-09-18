import React from "react";
import {
  View,
  Text,
  FlatList,
  Button,
  StyleSheet,
  TouchableOpacity,
} from "react-native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import MealCard from "../components/cards/MealCard";
import MealDetailsScreen from "./MealDetailsScreen";
import DailySummary from "../components/summary/DailySummary";
import { globalStyles } from "../theme/globalStyles";
import { colors, spacing, fontSizes } from "../theme/theme";
import { useNutritionStore } from "../store/useNutritionStore";
import type { Meal, NutritionStackParamList } from "../types";

const Stack = createNativeStackNavigator<NutritionStackParamList>();

const getDefaultMeals = (): Meal[] => [
  { id: "breakfast", name: "Pequeno Almoço", foods: [] },
  { id: "snack1", name: "1º Lanche", foods: [] },
  { id: "lunch", name: "Almoço", foods: [] },
  { id: "snack2", name: "2º Lanche", foods: [] },
  { id: "dinner", name: "Jantar", foods: [] },
  { id: "supper", name: "Ceia", foods: [] },
];

const formatDateForDisplay = (dateString: string): string => {
  const date = new Date(dateString + "T00:00:00");
  return date.toLocaleDateString("pt-PT", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

function NutritionHomeScreen({ navigation }: any) {
  const { dailyMeals, currentDate, setCurrentDate } = useNutritionStore();

  const getCurrentMeals = (): Meal[] =>
    dailyMeals[currentDate] || getDefaultMeals();

  const handleMealPress = (meal: Meal) => {
    navigation.navigate("MealDetails", { meal, date: currentDate });
  };

  const changeDate = (days: number) => {
    const dateObj = new Date(currentDate);
    dateObj.setDate(dateObj.getDate() + days);
    setCurrentDate(dateObj.toISOString().split("T")[0]);
  };

  const goToToday = () => setCurrentDate(new Date().toISOString().split("T")[0]);

  return (
    <View style={globalStyles.container}>
      {/*<Text style={globalStyles.title}>Nutrição</Text>*/}

      <DailySummary meals={getCurrentMeals()} />

      <View style={styles.dateNavigation}>
        <TouchableOpacity
          style={styles.dateButton}
          onPress={() => changeDate(-1)}
        >
          <Text style={styles.dateButtonText}>◀ Anterior</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.currentDate} onPress={goToToday}>
          <Text style={styles.currentDateText}>
            {formatDateForDisplay(currentDate)}
          </Text>
          {currentDate !== new Date().toISOString().split("T")[0] && (
            <Text style={styles.todayHint}>Toque para hoje</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.dateButton}
          onPress={() => changeDate(1)}
        >
          <Text style={styles.dateButtonText}>Seguinte ▶</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={getCurrentMeals()}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <MealCard meal={item} onPressDetails={() => handleMealPress(item)} />
        )}
      />
    </View>
  );
}

export default function Nutrition() {
  return (
    <Stack.Navigator initialRouteName="NutritionHome">
      <Stack.Screen
        name="NutritionHome"
        component={NutritionHomeScreen}
        options={{ title: "Nutrição" }}
      />
      <Stack.Screen
        name="MealDetails"
        component={MealDetailsScreen}
        options={{ title: "Detalhes da Refeição" }}
      />
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  dateNavigation: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  dateButton: {
    padding: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: 8,
    minWidth: 80,
    alignItems: "center",
  },
  dateButtonText: {
    color: "#fff",
    fontSize: fontSizes.small,
    fontWeight: "bold",
  },
  currentDate: {
    flex: 1,
    alignItems: "center",
    marginHorizontal: spacing.sm,
  },
  currentDateText: {
    fontSize: fontSizes.normal,
    fontWeight: "bold",
    color: colors.text,
    textAlign: "center",
  },
  todayHint: {
    fontSize: fontSizes.small,
    color: colors.muted,
    textAlign: "center",
  },
});
// Tela principal de nutrição com resumo diário, navegação de data e lista de refeições