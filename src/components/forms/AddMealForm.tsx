// src/components/forms/AddMealForm.tsx
import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from "react-native";
import { colors, spacing, fontSizes, radius } from "../../theme/theme";
import { globalStyles } from "../../theme/globalStyles";
import type { FoodData, Food } from "../../types";

type Props = {
  foodsData: FoodData[];
  onAddFood: (food: Food) => void; // recebe Food com quantity definido
  onClose: () => void;
};

export default function AddMealForm({ foodsData, onAddFood, onClose }: Props) {
  const [searchText, setSearchText] = useState("");
  const [quantityText, setQuantityText] = useState(""); // começa blank
  const [selectedFood, setSelectedFood] = useState<FoodData | null>(null);

  const filteredFoods = foodsData.filter((food) =>
    food.name.toLowerCase().includes(searchText.toLowerCase())
  );

  const handleAdd = () => {
    if (!selectedFood) {
      Alert.alert("Selecione um alimento antes de adicionar.");
      return;
    }
    const quantity = parseInt(quantityText, 10);
    if (!quantity || quantity <= 0) {
      Alert.alert("Por favor insira uma quantidade válida (maior que zero).");
      return;
    }
    onAddFood({ ...selectedFood, quantity });
    setSelectedFood(null);
    setQuantityText("");
  };

  return (
    <View style={[globalStyles.container, styles.container]}>
      <Text style={[globalStyles.title, styles.title]}>Adicionar Alimento</Text>

      <TextInput
        style={styles.input}
        placeholder="Pesquisar alimento..."
        value={searchText}
        onChangeText={setSearchText}
      />

      <FlatList
        data={filteredFoods}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.foodItem,
              selectedFood?.id === item.id && styles.selectedFoodItem,
            ]}
            onPress={() => setSelectedFood(item)}
          >
            <Text style={styles.foodName}>{item.name}</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text>Nenhum alimento encontrado.</Text>}
      />

      <TextInput
        style={styles.input}
        placeholder="Quantidade (g)"
        value={quantityText}
        onChangeText={setQuantityText}
        keyboardType="numeric"
      />

      <View style={styles.buttonsRow}>
        <Button title="Adicionar" onPress={handleAdd} />
        <Button title="Fechar" color={colors.danger} onPress={onClose} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.background,
    padding: spacing.md,
    borderRadius: radius.md,
    maxHeight: "85%",
  },
  title: {
    marginBottom: spacing.md,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: radius.sm,
    padding: spacing.sm,
    marginBottom: spacing.md,
  },
  foodItem: {
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  selectedFoodItem: {
   backgroundColor: "#e0f2f1",
  },
  foodName: {
    fontSize: fontSizes.normal,
    color: colors.text,
  },
  buttonsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
});
