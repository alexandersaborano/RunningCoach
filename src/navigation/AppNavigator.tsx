//Configuração da navegação principal do aplicativo de fitness
import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { NavigationContainer } from "@react-navigation/native";

import Dashboard from "../screens/Dashboard";
import Workouts from "../screens/Workouts";
import Nutrition from "../screens/Nutrition";
import Charts from "../screens/Charts";
import ImportCsv from "../screens/ImportCsv";

const Tab = createBottomTabNavigator();

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator initialRouteName="Dashboard">
        <Tab.Screen name="Dashboard" component={Dashboard} options={{ headerShown: false, tabBarLabel: 'Home' }} />
        <Tab.Screen name="Treino" component={Workouts} options={{ headerShown: false, tabBarLabel: 'Treino' }} />
        <Tab.Screen name="Nutrição" component={Nutrition} options={{ headerShown: false, tabBarLabel: 'Nutrição' }} />
        <Tab.Screen name="Gráficos" component={Charts} options={{ headerShown: false, tabBarLabel: 'Gráficos' }} />
        <Tab.Screen name="Import CSV" component={ImportCsv} options={{ headerShown: false, tabBarLabel: 'Importar CSV' }} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

