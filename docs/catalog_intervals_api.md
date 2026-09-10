# Cat?logo Abrangente de Dados e M?tricas ? Intervals.icu API

Este documento serve como invent?rio completo e detalhado de todos os dados e m?tricas expostos pela API do **Intervals.icu**, explicando o significado fisiol?gico/t?cnico de cada campo e como pode ser integrado no ecossistema do **Atleta AI Coach** no futuro.

---

## ?ndice
1. [Vis?o Geral da API](#1-vis?o-geral-da-api)
2. [Atividades e Treinos Realizados (`Activity`)](#2-atividades-e-treinos-realizados-activity)
   - [M?tricas Gerais e de Execu??o](#21-m?tricas-gerais-e-de-execu??o)
   - [Fisiologia, Carga e Stress Card?aco](#22-fisiologia-carga-e-stress-card?aco)
   - [Din?mica de Corrida e T?cnica](#23-din?mica-de-corrida-e-t?cnica)
   - [Pot?ncia e Curvas de Esfor?o (Power / HR Curves)](#24-pot?ncia-e-curvas-de-esfor?o)
   - [Condi??es Meteorol?gicas e Ambientais](#25-condi??es-meteorol?gicas-e-ambientais)
   - [Intervalos, Laps e Melhores Esfor?os (Best Efforts)](#26-intervalos-laps-e-melhores-esfor?os)
   - [Streams Brutas de Sensores (`/activity/{id}/streams`)](#27-streams-brutas-de-sensores)
3. [Wellness e M?tricas Di?rias de Sa?de (`Wellness`)](#3-wellness-e-m?tricas-di?rias-de-sa?de-wellness)
   - [Recupera??o, Sono e Sistema Nervoso Aut?nomo](#31-recupera??o-sono-e-sistema-nervoso-aut?nomo)
   - [Estado Subjetivo do Atleta](#32-estado-subjetivo-do-atleta)
   - [Carga Cr?nica, Aguda e Forma (CTL / ATL / TSB)](#33-carga-cr?nica-aguda-e-forma-fitness--fatigue)
   - [Biometria, Sa?de e Nutri??o](#34-biometria-sa?de-e-nutri??o)
4. [Perfil, Zonas e Fisiologia do Atleta (`Athlete` & `SportSettings`)](#4-perfil-zonas-e-fisiologia-do-atleta)
   - [Limiares e Frequ?ncia Card?aca](#41-limiares-e-frequ?ncia-card?aca)
   - [Zonas de Ritmo (Pace Zones) e Pot?ncia (Power Zones)](#42-zonas-de-ritmo-e-pot?ncia)
   - [Defini??es Espec?ficas por Desporto](#43-defini??es-espec?ficas-por-desporto)
5. [Calend?rio, Eventos e Planeamento (`Event` & `Workout`)](#5-calend?rio-eventos-e-planeamento)
   - [Competi??es e Objetivos (Provas A, B, C)](#51-competi??es-e-objetivos)
   - [Treinos Estruturados e Prescri??es](#52-treinos-estruturados-e-prescri??es)
6. [Equipamento e Cal?ado (`Gear`)](#6-equipamento-e-cal?ado-gear)
7. [Rotas e Percursos (`Route`)](#7-rotas-e-percursos-route)
8. [Matriz de Prioridade para Implementa??o Futura no Atleta AI Coach](#8-matriz-de-prioridade-para-implementa??o-futura)

---

## 1. Vis?o Geral da API

* **Protocolo:** REST API com endpoints em `https://intervals.icu/api/v1/`.
* **Autentica??o:** Basic Auth (`API_KEY:<chave>`) ou OAuth2 Bearer Token.
* **Identificador de Atleta:** `0` representa o atleta associado ? chave de API configurada.
* **Volume:** Mais de 117 endpoints e 109 schemas estruturados com suporte a dados temporais, agrega??o de s?ries longas e streams de alta resolu??o (1 Hz).

---

## 2. Atividades e Treinos Realizados (`Activity`)

O schema de atividade (`Activity`) possui mais de **180 propriedades**. Abaixo est?o agrupadas e descritas as mais relevantes para o treino de corrida e endurance:

### 2.1. M?tricas Gerais e de Execu??o
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `id` | String | Identificador ?nico da atividade no Intervals.icu (ex: `i12345` ou ID Strava/Garmin). |
| `name` | String | Nome dado ? atividade (ex: "S?ries 5x1000m", "Long?o de Domingo"). |
| `type` / `icu_type` | String | Tipo de desporto (`Run`, `VirtualRun`, `TrailRun`, `Ride`, `Swim`, etc.). |
| `start_date_local` | String (ISO) | Data e hora de in?cio no fuso hor?rio local. |
| `distance` | Float (m) | Dist?ncia total percorrida em metros. |
| `elapsed_time` | Int (s) | Dura??o total cronometrada (incluindo pausas). |
| `moving_time` | Int (s) | Tempo em movimento real (excluindo paragens em sem?foros, etc.). |
| `total_elevation_gain` | Float (m) | Desn?vel positivo acumulado em metros (D+). |
| `total_elevation_loss` | Float (m) | Desn?vel negativo acumulado em metros (D-). |
| `average_speed` | Float (m/s) | Velocidade m?dia (m/s). Convert?vel para pace (min/km). |
| `max_speed` | Float (m/s) | Velocidade m?xima atingida. |
| `gap` / `icu_gap` | Float (m/s) | **Grade Adjusted Pace (GAP)**: Pace ajustado ao declive/inclina??o, essencial para comparar esfor?o em percursos com relevo ou trail. |
| `gap_model` | String | Modelo usado para calcular o GAP (ex: Strava, Minetti, etc.). |
| `calories` | Int | Gasto energ?tico total estimado em calorias. |
| `device_name` | String | Dispositivo usado para gravar (ex: `Garmin Forerunner 965`, `Apple Watch`, `Coros Pace 3`). |

### 2.2. Fisiologia, Carga e Stress Card?aco
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `average_heartrate` | Int (bpm) | Frequ?ncia card?aca m?dia durante o treino. |
| `max_heartrate` | Int (bpm) | Frequ?ncia card?aca m?xima registada no treino. |
| `icu_resting_hr` | Int (bpm) | FC de repouso associada ao atleta na data da sess?o. |
| `icu_hr_zones` / `hr_zones` | Array[Int] | Distribui??o do tempo passado em cada zona de FC (em segundos). |
| `icu_training_load` / `icu_load` | Float | **TSS / Training Load**: Carga de treino calculada com base na intensidade e dura??o da sess?o. |
| `icu_intensity` | Float (%) | **Intensity Factor (IF)**: R?cio entre a intensidade da sess?o e o limiar (LTHR ou FTP). |
| `trimp` | Float | **TRIMP (Training Impulse)** de Banister: Medida fisiol?gica de sobrecarga cardiovascular baseada na reserva de FC. |
| `hr_load_type` | String | M?todo usado para calcular a carga (`HR`, `PACE`, `POWER`, `HRSS`). |
| `decoupling` / `hr_drift` | Float (%) | **Aerobic Decoupling (Pw:HR ou Pa:HR)**: Mede o desacoplamento aer?bio (deriva card?aca). Um valor < 5% indica excelente efici?ncia e estabilidade aer?bia; valores > 8% indicam fadiga, desidrata??o ou in?cio de sobretreino. |
| `efficiency_factor` (EF) | Float | **Efficiency Factor**: Rela??o entre velocidade (ou pot?ncia) e frequ?ncia card?aca m?dia (Pace / HR ou Power / HR). Subidas no EF indicam ganho de forma f?sica. |
| `hr_recovery` | Object | **Recupera??o de FC ap?s o treino**: Queda de bpm nos primeiros 60s/120s ap?s o t?rmino, ?timo indicador de aptid?o parassimp?tica. |
| `icu_hr_zone_times` | Array[ZoneTime] | Tempo detalhado (segundos e %) em cada zona card?aca do perfil. |
| `polarization_index` | Float | **?ndice de Polariza??o**: Mede se a distribui??o seguiu o modelo polarizado (80/20) ou piramidal. |

### 2.3. Din?mica de Corrida e T?cnica
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `average_cadence` | Float (spm) | Cad?ncia m?dia (passos por minuto - ppm/spm). Crucial para avaliar efici?ncia mec?nica (alvo comum: 165-180 ppm). |
| `max_cadence` | Float (spm) | Cad?ncia m?xima atingida. |
| `average_stride` / `stride_length` | Float (m) | Comprimento m?dio da passada em metros. |
| `average_vertical_oscillation` | Float (cm) | **Oscila??o Vertical**: Deslocamento vertical do centro de massa. Valores baixos indicam menor desperd?cio de energia. |
| `average_ground_contact_time` | Float (ms) | **Tempo de Contacto com o Solo (GCT)**: Milissegundos em que o p? permanece no ch?o. Corredores de elite t?m tempos menores (< 220ms). |
| `ground_contact_balance` | Float (%) | **Equil?brio de Tempo de Contacto (E/D)**: Simetria entre o p? esquerdo e direito (ex: 50.2% / 49.8%). Desvios apontam para compensa??es e risco de les?o. |
| `vertical_ratio` | Float (%) | **R?cio Vertical**: Rela??o percentual entre a oscila??o vertical e o comprimento da passada. |

### 2.4. Pot?ncia e Curvas de Esfor?o
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `average_watts` | Float (W) | Pot?ncia m?dia em Watts (se usado sensor Stryd, Garmin Running Power ou sensor de bike). |
| `icu_weighted_avg_watts` / `np` | Float (W) | **Normalized Power (NP)**: M?dia ponderada de pot?ncia que reflete o custo fisiol?gico real das varia??es de ritmo. |
| `power_curve` | Object | **Curva de Pot?ncia da Sess?o**: Pot?ncia m?xima sustentada para 1s, 5s, 1min, 5min, 20min, 60min. |
| `hr_curve` | Object | **Curva de FC**: FC m?xima sustentada por janela de tempo. |
| `pace_curve` | Object | **Curva de Pace**: Melhor pace sustentado por dist?ncia (400m, 1km, 5km, 10km, etc.). |
| `w_prime` / `w_bal` | Float (J) | Capacidade anaer?bia de trabalho acima do limiar cr?tico (W'). Mostra o "esgotamento da bateria anaer?bia". |

### 2.5. Condi??es Meteorol?gicas e Ambientais (`ActivityWeatherSummary`)
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `temp` / `apparent_temp` | Float (?C) | Temperatura real e sensa??o t?rmica durante a corrida. |
| `humidity` | Float (%) | Humidade relativa do ar (impacta diretamente a regula??o t?rmica e FC). |
| `wind_speed` / `wind_dir` | Float | Velocidade (km/h) e dire??o do vento (graus/rosa dos ventos). |
| `precipitation` / `rain` | Float (mm) | Precipita??o durante a sess?o. |
| `headwind_percentage` | Float (%) | Percentagem do percurso feita com vento de frente vs. vento de cauda. |

### 2.6. Intervalos, Laps e Melhores Esfor?os
* **Endpoint:** `GET /api/v1/activity/{id}/intervals`
* **Campos do Lap:**
  - `type`: `WORK` (bloco de esfor?o), `RECOVERY` (pausa ativa), `REST` (parado), `WARMUP`, `COOLDOWN`.
  - `distance`, `elapsed_time`, `moving_time`.
  - `average_heartrate`, `max_heartrate`.
  - `average_speed`, `average_pace`, `gap`.
  - `average_cadence`, `average_stride`.
  - `average_watts`, `weighted_average_watts`.
  - `label`: Nome/texto atribu?do ao intervalo (ex: "Rep 1 - 1000m").

### 2.7. Streams Brutas de Sensores
* **Endpoint:** `GET /api/v1/activity/{id}/streams?types=time,distance,heartrate,cadence,velocity_smooth,altitude,watts,temp,grade_smooth`
* Permite gerar gr?ficos segundo-a-segundo de:
  - Sobreposi??o FC vs. Pace vs. Declive.
  - An?lise de picos pontuais, paragens e transi??es entre blocos.

---

## 3. Wellness e M?tricas Di?rias de Sa?de (`Wellness`)

O endpoint `/api/v1/athlete/{id}/wellness` re?ne o registo di?rio de sa?de, biometria e recupera??o.

### 3.1. Recupera??o, Sono e Sistema Nervoso Aut?nomo
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `id` / `date` | String | Data do registo (formato `YYYY-MM-DD`). |
| `restingHR` | Int (bpm) | Frequ?ncia Card?aca de Repouso matinal (FCR). |
| `hrv` | Float (ms) | **HRV rMSSD**: M?dia do quadrado das diferen?as entre batimentos sucessivos. Principal marcador do t?nus parassimp?tico. |
| `hrvSDNN` | Float (ms) | **HRV SDNN**: Desvio padr?o de intervalos NN (vis?o global do SNA). |
| `sleepSecs` | Int (s) | Dura??o total de sono em segundos (convert?vel para horas). |
| `sleepScore` | Float (0-100) | Pontua??o agregada da qualidade do sono gerada pelo Garmin/Oura/Whoop. |
| `sleepQuality` | Int (1-5) | Avalia??o subjetiva da qualidade de sono. |
| `readiness` / `recovery` | Float (0-100 ou 1-10) | **?ndice de Prontid?o (Readiness)**: Estimativa combinada de prontid?o para treinar. |
| `deepSleepSecs` | Int (s) | Sono profundo (fase crucial para repara??o muscular e GH). |
| `remSleepSecs` | Int (s) | Sono REM (consolida??o de mem?ria e recupera??o cognitiva). |
| `lightSleepSecs` | Int (s) | Sono leve. |
| `sleepConsistency` | Float | Regularidade dos hor?rios de dormir/acordar. |

### 3.2. Estado Subjetivo do Atleta
| Campo | Escala | Descri??o |
| :--- | :--- | :--- |
| `fatigue` | 1 (?tima) - 5 (Exausto) | Sensa??o subjetiva de fadiga acumulada. |
| `soreness` | 1 (Nenhuma) - 5 (Muito dorido) | Dor muscular de in?cio tardio (DOMS). |
| `stress` | 1 (Muito baixo) - 5 (Muito alto) | N?vel de stress psicol?gico/di?rio extra-treino. |
| `mood` | 1 (P?ssimo) - 5 (Excelente) | Estado de humor e ?nimo geral. |
| `motivation` | 1 (Nenhuma) - 5 (Alt?ssima) | Vontade e motiva??o para treinar no dia. |
| `injury` | 1 (Sem limita??o) - 5 (Incapacitado) | Presen?a e grau de dores articulares ou les?es ativas. |
| `sickness` | 1 (Saud?vel) - 5 (Doente) | Sintomas de infe??o ou indisposi??o (gripe, constipa??o, etc.). |
| `menstrualPhase` | String / Enum | Fase do ciclo menstrual (Folicular, Ovula??o, L?tea, Menstrua??o), relevante para toler?ncia ao calor e carga. |

### 3.3. Carga Cr?nica, Aguda e Forma (CTL / ATL / TSB)
| Campo | Tipo | Descri??o & Significado |
| :--- | :--- | :--- |
| `ctl` | Float | **Chronic Training Load (Fitness)**: M?dia ponderada da carga nos ?ltimos 42 dias. Representa a capacidade de base instalada. |
| `atl` | Float | **Acute Training Load (Fatigue)**: M?dia ponderada da carga nos ?ltimos 7 dias. Representa a fadiga recente. |
| `tsb` / `form` | Float | **Training Stress Balance (Forma)**: `TSB = CTL - ATL`. <br>? **> +15:** Transi??o / destreinamento.<br>? **-10 a +10:** Zona ideal de prova (Peak/Taper).<br>? **-10 a -30:** Zona ?tima de treino e adapta??o produtiva.<br>? **< -30:** Alto risco de sobrecarga/overreaching n?o funcional. |
| `rampRate` | Float | Taxa de aumento de CTL por semana. Se > 5-7 pts/semana indica progress?o agressiva com risco de les?o. |
| `ctlLoad` / `atlLoad` | Float | Valores brutos di?rios utilizados nos c?lculos de decay. |

### 3.4. Biometria, Sa?de e Nutri??o
| Campo | Tipo | Descri??o |
| :--- | :--- | :--- |
| `weight` | Float (kg) | Peso corporal matinal. |
| `bodyFat` | Float (%) | Percentagem de massa gorda. |
| `vo2max` | Float (ml/kg/min) | Estimativa de VO2max atualizada pelo Garmin/Apple. |
| `steps` | Int | Passos di?rios totais (atividade n?o estruturada / NEAT). |
| `respiration` | Float (rpm) | Frequ?ncia respirat?ria noturna em repouso (subidas indicam infe??o/fadiga). |
| `spo2` | Float (%) | Satura??o de oxig?nio no sangue. |
| `systolic` / `diastolic` | Int (mmHg) | Press?o arterial sist?lica e diast?lica. |
| `hydration` / `water` | Float (L) | Ingest?o de l?quidos di?ria. |
| `caloriesConsumed` | Int (kcal) | Calorias consumidas. |
| `carbs` / `protein` / `fat` | Float (g) | Macros consumidos (Hidratos, Prote?na, L?pidos). |
| `bloodGlucose` | Float (mg/dL) | Glicemia em jejum ou m?dia de CGM. |

---

## 4. Perfil, Zonas e Fisiologia do Atleta (`Athlete` & `SportSettings`)

### 4.1. Limiares e Frequ?ncia Card?aca
* `icu_max_hr`: FC m?xima global registada.
* `icu_resting_hr`: FC de repouso de refer?ncia.
* `icu_lthr`: Frequ?ncia Card?aca no Limiar de Lactato (Anaerobic Threshold). Ponto divisor entre Z4 (Limiar) e Z5 (VO2max).
* `icu_hr_zones`: Array de limites superiores de cada zona card?aca (bpm).

### 4.2. Zonas de Ritmo (Pace Zones) e Pot?ncia
* `threshold_pace` / `lthr_pace` (m/s): Pace no limiar anaer?bio (Critical Speed / vVO2max / Threshold Pace).
* `pace_zones`: Zonas de ritmo (Z1 Recupera??o, Z2 Aer?bio Leve, Z3 Tempo, Z4 Limiar, Z5 VO2max, Z6 Anaer?bio).
* `ftp` (Watts): Functional Threshold Power para corrida/ciclismo.
* `power_zones`: Zonas de pot?ncia baseadas em % FTP.

### 4.3. Defini??es Espec?ficas por Desporto (`SportSettings`)
O Intervals.icu permite configura??es isoladas para `Run`, `TrailRun`, `VirtualRun`, `Ride`, `Swim`:
* Zonas card?acas diferentes para corrida vs. ciclismo.
* M?todos de carga distintos (ex: carga por Frequ?ncia Card?aca na corrida, por Pot?ncia na bicicleta).
* Zonas personalizadas com nomes pr?prios (ex: "Z2 Rodagem", "Z4 Maratona").

---

## 5. Calend?rio, Eventos e Planeamento (`Event` & `Workout`)

* **Endpoints:** `GET /api/v1/athlete/{id}/events` & `/api/v1/athlete/{id}/workouts`

### 5.1. Competi??es e Objetivos
| Campo | Tipo | Descri??o |
| :--- | :--- | :--- |
| `category` | Enum | `RACE` (Competi??o), `WORKOUT` (Treino), `NOTE` (Nota), `HOLIDAY` (F?rias/Descanso). |
| `target` | Enum | Prioridade da prova: `TARGET_A` (Objetivo principal do ano), `TARGET_B` (Preparat?ria), `TARGET_C` (Treino com dorsal). |
| `name` | String | Nome do evento (ex: "Maratona de Sevilha", "Meia de Lisboa"). |
| `start_date_local` | String | Data e hora marcada para o evento. |
| `plan_applied` | Boolean | Se o evento faz parte de um plano estruturado aplicado. |

### 5.2. Treinos Estruturados e Prescri??es
| Campo | Descri??o |
| :--- | :--- |
| `description` | Sintaxe estruturada do Intervals.icu (ex: `- 15m 65% HR
- 5x 1km 3:50-3:55
  - 400m rec
- 10m Z1`). |
| `steps` | JSON decomposto com dura??o, alvo de pace/FC/pot?ncia de cada bloco de treino. |
| `moving_time` / `distance` | Estimativa planeada de tempo e quilometragem. |
| `icu_training_load` | Carga de treino TSS prevista para a sess?o. |

---

## 6. Equipamento e Cal?ado (`Gear`)

* **Endpoint:** `GET /api/v1/athlete/{id}/gear`
* **Campos Principais:**
  - `id`, `name`: Nome do modelo (ex: "Nike Vaporfly 3", "Asics Novablast 4").
  - `type`: `SHOES`, `BIKE`, etc.
  - `distance`: Quil?metros acumulados em tempo real no par de sapatilhas.
  - `retired`: Se o cal?ado foi descontinuado.
  - `reminders`: Alertas autom?ticos (ex: avisar ao atingir 600 km ou 800 km para prevenir les?es por desgaste de espuma).

---

## 7. Rotas e Percursos (`Route`)

* **Endpoint:** `GET /api/v1/athlete/{id}/routes`
* Permite obter mapas GPX, eleva??o detalhada, subidas categorizadas e comparar a mesma rota percorrida em datas diferentes para verificar a evolu??o do atleta no mesmo segmento.

---

## 8. Matriz de Prioridade para Implementa??o Futura

| Fase | Dom?nio | M?tricas / Funcionalidades | Impacto no Atleta AI Coach |
| :---: | :--- | :--- | :--- |
| **Fase 1 (Pr?xima)** | **Fadiga & Forma (CTL/ATL/TSB)** | Importar `ctl`, `atl`, `tsb` di?rios da API de Wellness e exibir curva de forma no dashboard. | O Coach AI sabe se o atleta est? em sobrecarga (`TSB < -25`) ou em taper antes de sugerir treinos chave. |
| **Fase 1 (Pr?xima)** | **Decoupling & Deriva (Aerobic Decoupling)** | Extrair `decoupling` (`hr_drift`) e `efficiency_factor` de cada corrida. | Detetar se o ritmo aer?bio do atleta j? ? sustent?vel ou se h? quebra cardiovascular ao fim de 45-60 min. |
| **Fase 2** | **Din?mica de Corrida (Running Dynamics)** | Extrair cad?ncia (`average_cadence`), oscila??o vertical e tempo de contacto com o solo (`GCT`). | Dar feedback t?cnico sobre efici?ncia da passada e economia de corrida nas sess?es longas e de ritmo. |
| **Fase 2** | **Condi??es Meteorol?gicas (Weather)** | Associar temperatura, humidade e vento ?s corridas. | Explicar varia??es de FC e pace causadas por calor ou vento contra, evitando diagn?sticos errados de quebra f?sica. |
| **Fase 3** | **Eventos & Periodiza??o (A/B Races)** | Sincronizar calend?rio de provas (`category=RACE`, prioridade A/B/C) do Intervals. | O planeamento semanal assistido por AI estrutura o microciclo em fun??o da contagem decrescente para o dia da prova. |
| **Fase 3** | **Gest?o de Sapatilhas (Gear Tracker)** | Monitorizar km por par de sapatilhas e sugerir rota??o de cal?ado. | Preven??o de les?es e recomenda??o de cal?ado adequado para treinos de velocidade vs. rodagem. |
| **Fase 4** | **Streams em Alta Resolu??o (1 Hz)** | An?lise detalhada de subidas/descidas e transi??es em gr?ficos interativos. | Visualiza??o profunda para treinos de pista, repeti??es de rampas ou trail. |

---

*Documento gerado e catalogado a partir do contrato OpenAPI v1.0.0 oficial do Intervals.icu.*
