// src/screens/UserSettingsScreen.tsx
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  Alert,
  ScrollView,
  Switch,
} from "react-native";
import { useUserSettingsStore } from "../store/useUserSettingsStore";
import { colors, spacing, fontSizes, radius } from "../theme/theme";
import { globalStyles } from "../theme/globalStyles";

export default function UserSettingsScreen() {
  // Obter estado e setters do Zustand
  const {
    pesoKg,
    proteinaPorKg,
    gorduraPorKg,
    caloriasDiaTreino,
    caloriasDiaDescanso,
    diaTreino,

    setPesoKg,
    setProteinaPorKg,
    setGorduraPorKg,
    setCaloriasDiaTreino,
    setCaloriasDiaDescanso,
    setDiaTreino,
  } = useUserSettingsStore();

  // Local state para inputs (strings pois TextInput usa string)
  const [pesoText, setPesoText] = useState(pesoKg?.toString() || "");
  const [proteinaText, setProteinaText] = useState(proteinaPorKg.toString());
  const [gorduraText, setGorduraText] = useState(gorduraPorKg.toString());
  const [caloriasTreinoText, setCaloriasTreinoText] = useState(
    caloriasDiaTreino.toString()
  );
  const [caloriasDescansoText, setCaloriasDescansoText] = useState(
    caloriasDiaDescanso.toString()
  );
  const [diaTreinoSwitch, setDiaTreinoSwitch] = useState(diaTreino);

  useEffect(() => {
    // Sincronizar local state com global quando abrir
    setPesoText(pesoKg?.toString() || "");
    setProteinaText(proteinaPorKg.toString());
    setGorduraText(gorduraPorKg.toString());
    setCaloriasTreinoText(caloriasDiaTreino.toString());
    setCaloriasDescansoText(caloriasDiaDescanso.toString());
    setDiaTreinoSwitch(diaTreino);
  }, [
    pesoKg,
    proteinaPorKg,
    gorduraPorKg,
    caloriasDiaTreino,
    caloriasDiaDescanso,
    diaTreino,
  ]);

  const handleSave = () => {
    const peso = parseFloat(pesoText);
    const proteina = parseFloat(proteinaText);
    const gordura = parseFloat(gorduraText);
    const calTreino = parseInt(caloriasTreinoText, 10);
    const calDescanso = parseInt(caloriasDescansoText, 10);

    if (
      !peso ||
      peso <= 0 ||
      !proteina ||
      proteina <= 0 ||
      !gordura ||
      gordura <= 0 ||
      !calTreino ||
      calTreino <= 0 ||
      !calDescanso ||
      calDescanso <= 0
    ) {
      Alert.alert("Por favor insira valores válidos em todos os campos.");
      return;
    }

    setPesoKg(peso);
    setProteinaPorKg(proteina);
    setGorduraPorKg(gordura);
    setCaloriasDiaTreino(calTreino);
    setCaloriasDiaDescanso(calDescanso);
    setDiaTreino(diaTreinoSwitch);

    Alert.alert("Configurações salvas com sucesso!");
  };

  return (
    <ScrollView style={globalStyles.container} contentContainerStyle={styles.content}>
      <Text style={globalStyles.title}>Configurações Nutrição</Text>

      <View style={styles.field}>
        <Text style={styles.label}>Peso Corporal (kg)</Text>
        <TextInput
          style={styles.input}
          keyboardType="numeric"
          value={pesoText}
          onChangeText={setPesoText}
          placeholder="Ex: 75"
        />
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Proteína (g/kg corporal)</Text>
        <TextInput
          style={styles.input}
          keyboardType="numeric"
          value={proteinaText}
          onChangeText={setProteinaText}
          placeholder="Ex: 2.7"
        />
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Gorduras (g/kg corporal)</Text>
        <TextInput
          style={styles.input}
          keyboardType="numeric"
          value={gorduraText}
          onChangeText={setGorduraText}
          placeholder="Ex: 0.7"
        />
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Calorias em dias de treino (kcal)</Text>
        <TextInput
          style={styles.input}
          keyboardType="numeric"
          value={caloriasTreinoText}
          onChangeText={setCaloriasTreinoText}
          placeholder="Ex: 2000"
        />
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Calorias em dias de descanso (kcal)</Text>
        <TextInput
          style={styles.input}
          keyboardType="numeric"
          value={caloriasDescansoText}
          onChangeText={setCaloriasDescansoText}
          placeholder="Ex: 1900"
        />
      </View>

      <View style={[styles.field, styles.switchField]}>
        <Text style={styles.label}>Hoje é dia de treino?</Text>
        <Switch
          value={diaTreinoSwitch}
          onValueChange={setDiaTreinoSwitch}
          thumbColor={diaTreinoSwitch ? colors.primary : colors.muted}
        />
      </View>

      <Button title="Salvar Configurações" onPress={handleSave} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    paddingBottom: 40,
  },
  field: {
    marginBottom: spacing.md,
  },
  label: {
    fontSize: fontSizes.normal,
    marginBottom: spacing.xs,
    color: colors.text,
  },
  input: {
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 6,
    padding: spacing.sm,
    fontSize: fontSizes.normal,
    backgroundColor: colors.card,
    color: colors.text,
  },
  switchField: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
});
