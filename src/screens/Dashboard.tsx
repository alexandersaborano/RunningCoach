// Tela de dashboard do aplicativo de fitness

import React from "react";
import { View, Text } from "react-native";
import { globalStyles } from "../theme/globalStyles";

export default function DashboardScreen() {
  return (
    <View style={globalStyles.container}>
      <Text style={globalStyles.title}>Dashboard</Text>
      <Text style={globalStyles.subtitle}>Resumo do teu progresso</Text>
      <View style={globalStyles.card}>
        <Text style={globalStyles.text}>Aqui vai um gráfico futuramente 📊</Text>
      </View>
    </View>
  );
}
