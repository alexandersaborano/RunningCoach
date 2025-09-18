import React, { useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Button,
  Modal,
} from "react-native";
import { useNutritionStore } from "../store/useNutritionStore";
import { colors, spacing, fontSizes, radius } from "../theme/theme";
import { globalStyles } from "../theme/globalStyles";
import AddMealForm from "../components/forms/AddMealForm";
import foodsData from "../data/foods.json";
import type { Food } from "../types";

export default function MealDetailsScreen({ route, navigation }: any) {
  const { meal, date } = route.params;
  const { removeFood, updateFoodQuantity, addFood } = useNutritionStore();

  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [quantityText, setQuantityText] = useState("0");
  const [isAddFoodModalVisible, setIsAddFoodModalVisible] = useState(false);

  const handleRemove = (index: number) => {
    removeFood(date, meal.id, index);
  };

  const handleStartEdit = (index: number, currentQty: number) => {
    setEditIndex(index);
    setQuantityText(currentQty.toString());
  };

  const handleConfirmEdit = () => {
    if (editIndex !== null) {
      const newQty = parseInt(quantityText) || 0;
      updateFoodQuantity(date, meal.id, editIndex, newQty);
      setEditIndex(null);
    }
  };

  const handleAddFood = (food: Food) => {
    addFood(date, meal.id, food);
    // Permite adicionar vários alimentos antes de fechar o modal
  };

  return (
    <View style={globalStyles.container}>
      <Text style={globalStyles.title}>{meal.name}</Text>

      <Button
        title="Adicionar Alimento"
        onPress={() => setIsAddFoodModalVisible(true)}
      />

      <FlatList
        data={meal.foods}
        keyExtractor={(_, idx) => idx.toString()}
        renderItem={({ item, index }) => (
          <View style={styles.foodItem}>
            <View style={styles.foodRow}>
              <Text style={styles.foodName}>{item.name}</Text>
              <TouchableOpacity onPress={() => handleRemove(index)}>
                <Text style={styles.removeText}>Remover</Text>
              </TouchableOpacity>
            </View>

            {editIndex === index ? (
              <View style={styles.editRow}>
                <TextInput
                  style={styles.input}
                  keyboardType="numeric"
                  value={quantityText}
                  onChangeText={setQuantityText}
                />
                <Button title="OK" onPress={handleConfirmEdit} />
              </View>
            ) : (
              <TouchableOpacity
                onPress={() => handleStartEdit(index, item.quantity)}
              >
                <Text style={styles.foodQuantity}>{item.quantity}g</Text>
              </TouchableOpacity>
            )}

            <Text style={styles.foodMacros}>
              {((item.calories * item.quantity) / 100).toFixed(0)} kcal | P:{" "}
              {((item.protein * item.quantity) / 100).toFixed(1)}g | C:{" "}
              {((item.carbs * item.quantity) / 100).toFixed(1)}g | G:{" "}
              {((item.fat * item.quantity) / 100).toFixed(1)}g
            </Text>
          </View>
        )}
        ListEmptyComponent={
          <Text style={styles.emptyText}>Nenhum alimento adicionado.</Text>
        }
      />

      {/* Modal de adicionar alimentos */}
      <Modal visible={isAddFoodModalVisible} animationType="slide">
        <AddMealForm
          foodsData={foodsData}
          onAddFood={handleAddFood}
          onClose={() => setIsAddFoodModalVisible(false)}
        />
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  foodItem: {
    backgroundColor: colors.card,
    padding: spacing.sm,
    borderRadius: radius.sm,
    marginBottom: spacing.sm,
  },
  foodRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  foodName: {
    fontSize: fontSizes.normal,
    fontWeight: "bold",
    color: colors.text,
  },
  removeText: {
    color: colors.danger,
    fontSize: fontSizes.small,
  },
  editRow: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.xs,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: radius.sm,
    padding: spacing.xs,
    width: 80,
    marginRight: spacing.sm,
  },
  foodQuantity: {
    fontSize: fontSizes.normal,
    color: colors.primary,
    marginVertical: spacing.xs,
  },
  foodMacros: {
    fontSize: fontSizes.small,
    color: colors.text,
  },
  emptyText: {
    fontSize: fontSizes.normal,
    color: colors.muted,
    textAlign: "center",
    marginTop: spacing.md,
  },
});
// Tela principal de nutrição com resumo diário, navegação de data e lista de refeições