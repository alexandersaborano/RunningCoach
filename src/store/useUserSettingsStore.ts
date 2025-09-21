// src/store/useUserSettingsStore.ts
import { create } from "zustand";

type UserSettingsState = {
  pesoKg: number | null;
  proteinaPorKg: number;
  gorduraPorKg: number;
  caloriasDiaTreino: number;
  caloriasDiaDescanso: number;
  diaTreino: boolean;

  setPesoKg: (peso: number) => void;
  setProteinaPorKg: (value: number) => void;
  setGorduraPorKg: (value: number) => void;
  setCaloriasDiaTreino: (value: number) => void;
  setCaloriasDiaDescanso: (value: number) => void;
  setDiaTreino: (value: boolean) => void;
};
  
export const useUserSettingsStore = create<UserSettingsState>((set) => ({
  pesoKg: null,
  proteinaPorKg: 2.7,
  gorduraPorKg: 0.7,
  caloriasDiaTreino: 2000,
  caloriasDiaDescanso: 1900,
  diaTreino: true,
  
  setPesoKg: (peso) => set({ pesoKg: peso }),
  setProteinaPorKg: (value) => set({ proteinaPorKg: value }),
  setGorduraPorKg: (value) => set({ gorduraPorKg: value }),
  setCaloriasDiaTreino: (value) => set({ caloriasDiaTreino: value }),
  setCaloriasDiaDescanso: (value) => set({ caloriasDiaDescanso: value }),
  setDiaTreino: (value) => set({ diaTreino: value }),
}));
