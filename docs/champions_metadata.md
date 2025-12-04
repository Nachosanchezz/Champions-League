# Champions League RAG – Contexto de Metadata

Este documento resume todos los datasets incluidos en el proyecto de la Champions League. Está diseñado para servir como metadata para un sistema de *Retrieval-Augmented Generation* (RAG) y ayudará a proporcionar contexto global sobre la información disponible, su estructura y el significado de cada dataset.

---

## 1. PARTIDOS (Fuentes de GitHub)

Resultados de partidos temporada por temporada desde **1992/93 hasta 2024/25**.

📁 Carpeta: `data/partidos/`

📄 Formato: Un CSV por temporada  
`champions_YYYY_YY.csv`

Cada archivo suele contener:
- Fecha  
- Equipo local  
- Equipo visitante  
- Resultado  
- Ronda (Grupo, Octavos, Cuartos, Semifinal, Final)  
- Estadio  
- Notas adicionales (penaltis, resultado global, etc.)

Permiten responder preguntas como:
- “¿Cuántos goles marcó el Barcelona en la Champions 2009?”  
- “¿Contra quién jugó el Real Madrid en semifinales de 1998?”  
- “Lista todos los partidos de eliminatoria con prórroga.”

---

## 2. DATOS DE TRANSFERMARKT

📁 Carpeta: `data/transfermarkt/`

### 📄 Archivos:
- `tfmkt_alltime_club_table.csv`  
  Clasificación histórica de clubes (puntos, partidos, victorias, goles).

- `tfmkt_champions_finals_alltime.csv`  
  Todas las finales de la UCL + metadata.

- `tfmkt_cl_fairplay_1992_2025.csv`  
  Ranking de fair play por temporada.

- `tfmkt_cl_goals_assists_1992_2025.csv`  
  Goles y asistencias por temporada (por jugador).

- `tfmkt_cl_goalscorers_1992_2025.csv`  
  Máximos goleadores por temporada.

- `tfmkt_goals_per_match_alltime.csv`  
  Promedio histórico de goles por partido.

- `tfmkt_most_appearances_alltime.csv`  
  Jugadores con más apariciones en Champions.

- `tfmkt_topscorers_alltime.csv`  
  Máximos goleadores históricos (ej. Ronaldo, Messi).

Permiten responder:
- “Top 10 jugadores con más goles en Champions.”  
- “¿Cuál ha sido el promedio de goles por partido en los últimos 20 años?”  
- “Jugadores con más apariciones históricas.”

---

## 3. ESTADÍSTICAS OFICIALES DE UEFA

📁 Carpeta: `data/uefa/`

Dos grandes grupos: **estadísticas de clubes** y **estadísticas de jugadores**.  
Cada categoría contiene datasets desde **1992–2025**.

### 📊 ESTADÍSTICAS DE CLUBES:
- `ucl_clubs_attacking_stats_1992_2025.csv`  
- `ucl_clubs_attempts_stats_1992_2025.csv`  
- `ucl_clubs_defending_stats_1992_2025.csv`  
- `ucl_clubs_disciplinary_stats_1992_2025.csv`  
- `ucl_clubs_distribution_stats_1992_2025.csv`  
- `ucl_clubs_goalkeeping_stats_1992_2025 csv`  
- `ucl_clubs_goals_stats_1992_2025.csv`  
- `ucl_clubs_key_stats_1992_2025.csv`  

Incluyen métricas como:
- xG / xGA  
- Tiros, ataques, construcciones de jugada  
- Entradas, interceptaciones  
- Pases + precisión  
- Paradas, PSxG, acciones del portero  
- Goles totales por club y temporada  

---

### 🧍 ESTADÍSTICAS DE JUGADORES:
- `ucl_players_attacking_stats_1992_2025.csv`  
- `ucl_players_attempts_stats_1992_2025.csv`  
- `ucl_players_defending_stats_1992_2025.csv`  
- `ucl_players_disciplinary_stats_1992_2025.csv`  
- `ucl_players_distribution_stats_1992_2025.csv`  
- `ucl_players_goalkeeping_stats_1992_2025.csv`  
- `ucl_players_goals_stats_1992_2025.csv`  
- `ucl_players_key_stats_1992_2025.csv`  

Incluyen:
- Goles, asistencias, generación de tiros  
- Métricas defensivas (entradas, bloqueos)  
- Disciplina (amarillas/rojas)  
- Rangos de pase  
- Rendimiento de porteros  

Permiten responder:
- “¿Quién fue el líder en xG en 2004?”  
- “Comparar estadísticas de Modric vs Gerrard.”  
- “¿Qué portero tuvo el mejor % de paradas en 2017?”

---

## 4. PARTIDOS DE WIKIPEDIA (Archivo Final Limpio)

📄 `ucl_matches_wikipedia_final.csv`

Contiene:
- Fecha  
- Local / Visitante  
- Resultado  
- Ronda  
- Estadio  
- Temporada  

Útil para:
- Verificación de campeones  
- Contrastar estructura de temporada  

---

## 5. RESUMEN PARA PIPELINE DE RAG EMBEDDING

Estrategia de unificación:
- Todos los CSV serán cargados como **dataframes**.  
- Convertir a **CSV en UTF-8** (ya válido).  
- Construir metadata textual para cada dataset (este archivo).  
- Unir todos los resúmenes + descripción de columnas en un `.md` único.  
- Aplicar *chunking* (1000 caracteres, solapamiento 200).  
- Usar FAISS para crear el índice vectorial.  

Esto garantiza:
- Que el sistema RAG comprenda cada dataset.  
- Que entienda el significado de columnas y dónde está cada tipo de información.  
- Que pueda dirigir correctamente las consultas (partidos, clubes, jugadores, historia…).  

---

## 6. CONTEXTO EXTRA (para facilitar el razonamiento del RAG)

Incluir hechos generales sobre la Champions League:
- Evolución del formato (antes de 2003 existía segunda fase de grupos).  
- Cambios de reglas (se eliminó el valor doble de goles fuera de casa en 2021).  
- Equipos con más títulos (Real Madrid, Milan, Bayern, Barcelona, Liverpool).  
- Grandes narrativas históricas (era Cruyff, Guardiola, Mourinho…).  
- Antes de 1992 el torneo era la “Copa de Europa”.  

Esto ayuda al modelo a evitar alucinaciones.

---

## FIN DEL DOCUMENTO DE METADATA
