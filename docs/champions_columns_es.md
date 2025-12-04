# Diccionario de columnas – Proyecto Champions League

Este documento detalla **las columnas más importantes** de tus ficheros CSV y cómo se relacionan entre sí. No es necesario listar absolutamente todas las métricas avanzadas, pero sí entender la estructura básica para que el RAG tenga contexto sobre *qué significa cada campo*.

---

## 1. Ficheros de partidos – `data/partidos/`

### 1.1. `champions_AAAA_BB.csv` (uno por temporada)

Columnas:

- `Stage`  
  Fase de la competición. Ejemplos típicos:  
  - `Qualification` / `Qualifying` – rondas previas.  
  - `Group Stage` – fase de grupos.  
  - `Round of 16`, `Quarter-finals`, `Semi-finals`, `Final`.  

- `Date`  
  Fecha del partido en texto. Suele venir en inglés con día abreviado (`Tue 10/03/2009` o similar).  
  Para análisis numérico conviene transformarla a tipo fecha (`YYYY-MM-DD`).

- `HomeTeam` / `AwayTeam`  
  Nombres de los equipos local y visitante.  
  Estos nombres se usan para enlazar, de forma aproximada, con `Team`/`Club` de los otros ficheros (UEFA y Transfermarkt). Puede haber pequeñas diferencias de nomenclatura (“Paris Saint-Germain” vs “PSG”).

- `HomeTeamCountry` / `AwayTeamCountry`  
  País del club (si viene en la fuente de origen). Útil para estadísticas por país.

- `Score`  
  Marcador final en texto, por ejemplo `2–1` o `1:1`.  
  Si quieres análisis numérico, puedes separar en `HomeGoals` y `AwayGoals` con un split.

Relación con otros ficheros:

- `Season` implícita en el nombre del fichero (`champions_2008_09.csv` → temporada 2008‑09).  
- Se puede relacionar con:
  - `ucl_matches_wikipedia_final.csv` (UEFA) por `Season` + `Date` + equipos.
  - Estadísticas por club/jugador usando `HomeTeam`/`AwayTeam` ≈ `Team`.

---

## 2. Transfermarkt – `data/transfermarkt/`

### 2.1. `tfmkt_alltime_club_table.csv`

Columnas principales (algunas pueden variar ligeramente):

- `Rank` – posición del club en la tabla histórica.
- `Club` – nombre del club.
- `Matches` – partidos jugados en Champions.
- `Wins`, `Draws`, `Losses` – partidos ganados, empatados y perdidos.
- `GoalsFor`, `GoalsAgainst` – goles marcados y recibidos.
- `GoalDifference` – diferencia de goles (`GF - GA`).
- `Points` – puntos acumulados según el criterio de la web.

Claves / relaciones:

- `Club` puede conectarse con `Team` (UEFA) y `HomeTeam`/`AwayTeam` (partidos).

### 2.2. `tfmkt_champions_finals_alltime.csv`

Columnas típicas:

- `Season` – temporada (`1998-99`, `2013-14`, etc.).
- `Date` – fecha de la final.
- `HomeTeam`, `AwayTeam` – finalistas (a veces solo `Team1`, `Team2`).
- `Score` – resultado final.
- `Stadium`, `City`, `Country` – sede de la final.
- `Winner`, `RunnerUp` – campeón y subcampeón.

Relaciones:

- `Season` enlaza con:
  - Estadísticas por temporada de UEFA (`Season`).
  - Ficheros de partidos para localizar esa final concreta.

### 2.3. `tfmkt_cl_fairplay_1992_2025.csv`

Columnas habituales:

- `Season` / `Season_id` – temporada.
- `Club` – equipo.
- `YellowCards` – amarillas.
- `SecondYellow` – dobles amarillas.
- `RedCards` – rojas directas.
- `ExpulsionsTotal` – `SecondYellow + RedCards` (si existe).
- `Points` – puntos de fair play (según normativa Transfermarkt).

Relaciones:

- `Season` + `Club` enlazan con estadísticas UEFA de disciplina (`ucl_clubs_disciplinary_stats_...`).

### 2.4. `tfmkt_cl_goalscorers_1992_2025.csv`

Columnas (confirmadas):

- `Season_id` – año de comienzo de la temporada (1992, 1993, …).
- `Season` – formato corto (`92/93`, `93/94`, …).
- `Rank` – posición del goleador dentro de su temporada.
- `Player` – nombre del jugador.
- `Player_url` – enlace a su perfil Transfermarkt.
- `Position` – posición en el campo (Delantero centro, Mediocentro…).
- `Nationalities` – lista de nacionalidades (texto).
- `Age` – edad en esa temporada.
- `Club` – club para el que jugó esa Champions.
- `Club_url` – enlace al club.
- `Matches` – partidos jugados.
- `Goals` – goles marcados.

### 2.5. `tfmkt_cl_goals_assists_1992_2025.csv`

Columnas:

- `Season` – temporada (`92/93`, `93/94`, …).
- `Rank` – posición en el ranking de esa temporada.
- `Player`, `Player_url`, `Position`, `Nationalities`, `Age`, `Club`, `Club_url` – igual que arriba.
- `Matches` – partidos jugados.
- `Goals` – goles.
- `Assists` – asistencias.
- `Goals_Assists` – suma de goles y asistencias.

Relación entre ambos ficheros:

- Mismas temporadas y jugadores, pero el de `goals_assists` añade información de asistencias y suma total. Puedes usarlos juntos para enriquecer respuestas.

### 2.6. Otros ficheros Transfermarkt

- `tfmkt_goals_per_match_alltime.csv` – suele contener columnas del tipo `Season`, `Matches`, `Goals`, `GoalsPerMatch`.
- `tfmkt_most_appearances_alltime.csv` – `Player`, `Matches`, `Clubs`, etc.
- `tfmkt_topscorers_alltime.csv` – `Rank`, `Player`, `Goals`, `Matches`, `GoalsPerMatch`…

---

## 3. UEFA – `data/uefa/`

La estructura de UEFA es muy homogénea: casi todos los ficheros tienen un bloque de identificación y luego muchas métricas específicas.

### 3.1. Identificación común (clubes)

En los ficheros `ucl_clubs_*_stats_1992_2025.csv` suele haber siempre algo parecido a:

- `Season` – temporada (`1992-1993`, `2014-2015`, etc.).
- `Season_id` – año de inicio (`1992`, `2014`, …).
- `Team` – nombre del club.
- `Country` o `Association` – país o federación del club.
- A veces: `StageReached` – última fase alcanzada por el equipo.

Estos campos permiten unir estadísticas entre sí y con Transfermarkt / partidos:

- Clave aproximada: `Season_id` + `Team`.

### 3.2. Identificación común (jugadores)

En los ficheros `ucl_players_*_stats_1992_2025.csv` aparecen típicamente:

- `Season`, `Season_id` – temporada.
- `Player` – nombre.
- `Team` – equipo en el que juega.
- `Position` – rol (DF, MF, FW, GK… o texto detallado).
- `Age` – edad en esa temporada.
- `Nationality` – país principal (a veces solo uno).

Clave de unión: `Season_id` + `Player` (y opcionalmente `Team`).

### 3.3. Tipos de estadísticas por club

A grandes rasgos:

- `ucl_clubs_attacking_stats_...`  
  - Goles a favor, goles en jugada, de penalti, de falta, dentro/fuera del área…  
  - Posesión en campo rival, toques en área, etc.

- `ucl_clubs_attempts_stats_...`  
  - Tiros totales, a puerta, fuera, bloqueados.  
  - Tiros dentro/fuera del área, xG de los tiros, etc.

- `ucl_clubs_defending_stats_...`  
  - Entradas, despejes, intercepciones, duelos ganados.  
  - Goles encajados, ocasiones concedidas…

- `ucl_clubs_goalkeeping_stats_...`  
  - Paradas, tiros recibidos, % de paradas.  
  - Goles encajados, penaltis parados, salidas…

- `ucl_clubs_disciplinary_stats_...`  
  - Faltas cometidas/recibidas, tarjetas amarillas, rojas, etc.

- `ucl_clubs_distribution_stats_...`  
  - Pases totales, completados, % acierto, pases largos, progresivos…

- `ucl_clubs_goals_stats_...`  
  - Goles minuto a minuto, por parte, por tipo de jugada, etc.

- `ucl_clubs_key_stats_...`  
  - Resumen de varias métricas clave (goles, tiros, posesión, xG, etc.).

### 3.4. Tipos de estadísticas por jugador

Análogo a lo anterior pero a nivel individual:

- `ucl_players_attacking_stats_...` – goles, asistencias, acciones ofensivas.
- `ucl_players_attempts_stats_...` – remates del jugador, xG individual, tiros a puerta.
- `ucl_players_defending_stats_...` – entradas, despejes, duelos defensivos.
- `ucl_players_goalkeeping_stats_...` – estadísticas de porteros.
- `ucl_players_disciplinary_stats_...` – faltas, tarjetas.
- `ucl_players_distribution_stats_...` – pases realizados por el jugador.
- `ucl_players_goals_stats_...` – desglose de goles (tipo, zona, minuto).
- `ucl_players_key_stats_...` – resumen general (minutos, goles, asistencias, etc.).

Para el RAG, no es necesario explicar cada métrica (“ShotsOnTarget”, “xGChain”, etc.), pero sí que estos ficheros contienen estadísticas **granulares** que permiten justificar respuestas tipo:

> “Según las estadísticas oficiales de la UEFA, en la temporada 2019‑20 Messi registró X tiros a puerta y Y goles en Champions.”

### 3.5. `ucl_matches_wikipedia_final.csv`

Columnas típicas (a confirmar en el CSV real):

- `Season`
- `Date`
- `HomeTeam`
- `AwayTeam`
- `Score`
- `Stage`
- `Stadium`
- `City`
- `Country`

Funciona como un **catálogo consolidado de partidos** que se puede relacionar con:

- `data/partidos/champions_AAAA_BB.csv` (por temporada, fecha y equipos).
- Estadísticas por equipo/jugador (por temporada y equipo).

---

## 4. Recomendaciones para el RAG

1. **Mantener los CSV tal cual**  
   No es obligatorio unificar columnas ahora, mientras tú sepas qué guarda cada fichero. El RAG trabajará sobre texto (resúmenes, tablas renderizadas, etc.).

2. **Usar este diccionario como documento de contexto**  
   Igual que el fichero de metadatos general, este `.md` debe cargarse en la base vectorial. De esta forma, cuando preguntes algo como “¿Qué significa la columna `Goals_Assists`?”, el modelo podrá recuperar esta explicación.

3. **Posibles mejoras futuras**  
   - Crear una tabla “maestra” por temporada con:
     - Partidos (`Stage`, `Date`, equipos, resultado).
     - Goles/asistencias principales.
     - Estadísticas básicas por club.  
   - A partir de esa tabla maestra, generar descripciones en lenguaje natural que el RAG pueda usar como contexto narrativo.
