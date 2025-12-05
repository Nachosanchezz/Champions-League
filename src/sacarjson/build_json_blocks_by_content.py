import json
from pathlib import Path

import pandas as pd

# ==== CONFIGURACIÓN DE RUTAS ====
BASE_DIR = Path("data") / "csv"   # ajusta si tu carpeta es distinta
OUT_DIR = Path("data") / "json"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ==== DEFINIMOS LOS BLOQUES POR CONTENIDO ====
BLOCKS = {
    # 1) PARTIDOS (todas las temporadas)
    "ucl_block_partidos": [
        BASE_DIR / "partidos" / "champions_*.csv",          # todos los champions_YYYY_YY.csv
        BASE_DIR / "uefa" / "ucl_matches_wikipedia_final.csv",  # también es info de partidos
    ],

    # 2) FINALES Y PALMARÉS
    "ucl_block_finales": [
        BASE_DIR / "transfermarkt" / "tfmkt_champions_finals_alltime.csv",
        BASE_DIR / "uefa" / "ucl_matches_wikipedia_final.csv",
    ],

    # 3) GOLEADORES / ASISTENCIAS / RÉCORDS DE GOLES
    "ucl_block_goleadores": [
        BASE_DIR / "transfermarkt" / "tfmkt_cl_goalscorers_1992_2025.csv",
        BASE_DIR / "transfermarkt" / "tfmkt_cl_goals_assists_1992_2025.csv",
        BASE_DIR / "transfermarkt" / "tfmkt_topscorers_alltime.csv",
    ],

    # 4) ESTADÍSTICAS DE JUGADORES
    "ucl_block_jugadores_stats": [
        BASE_DIR / "uefa" / "ucl_players_attacking_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_attempts_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_defending_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_disciplinary_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_distribution_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_goalkeeping_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_goals_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_players_key_stats_1992_2025.csv",
        BASE_DIR / "transfermarkt" / "tfmkt_most_appearances_alltime.csv",
    ],

    # 5) ESTADÍSTICAS DE CLUBES
    "ucl_block_clubes_stats": [
        BASE_DIR / "uefa" / "ucl_clubs_attacking_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_attempts_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_defending_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_disciplinary_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_distribution_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_goalkeeping_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_goals_stats_1992_2025.csv",
        BASE_DIR / "uefa" / "ucl_clubs_key_stats_1992_2025.csv",
        BASE_DIR / "transfermarkt" / "tfmkt_alltime_club_table.csv",
        BASE_DIR / "transfermarkt" / "tfmkt_cl_fairplay_1992_2025.csv",
        BASE_DIR / "transfermarkt" / "tfmkt_goals_per_match_alltime.csv",
    ],
}

def detect_provider(path: Path) -> str:
    """Devuelve 'uefa', 'transfermarkt' o 'partidos' según la ruta."""
    parent = path.parent.name.lower()
    if "transfermarkt" in parent:
        return "transfermarkt"
    if "uefa" in parent:
        return "uefa"
    if "partidos" in parent:
        return "partidos"
    return parent

def csvs_from_pattern(pattern_path: Path):
    """Dado algo tipo BASE_DIR/'partidos'/'champions_*.csv' devuelve la lista real de ficheros."""
    if "*" in str(pattern_path):
        return sorted(pattern_path.parent.glob(pattern_path.name))
    else:
        return [pattern_path] if pattern_path.exists() else []

def build_block(block_name: str, patterns):
    out_file = OUT_DIR / f"{block_name}.jsonl"
    print(f"\n🧱 Generando {out_file} ...")
    n_rows_total = 0

    with out_file.open("w", encoding="utf-8") as f_out:
        for pattern in patterns:
            for csv_path in csvs_from_pattern(pattern):
                provider = detect_provider(csv_path)
                print(f"  · Leyendo {csv_path} [{provider}]")
                try:
                    df = pd.read_csv(csv_path, encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(csv_path, encoding="latin-1")
                df = df.fillna("")  # para que JSON no tenga NaN

                for _, row in df.iterrows():
                    record = {
                        "block": block_name,
                        "source_file": str(csv_path),
                        "provider": provider,
                        "data": row.to_dict(),
                    }
                    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    n_rows_total += 1

    print(f"✅ {block_name}: {n_rows_total} filas embebidas en {out_file}")

def main():
    for block_name, patterns in BLOCKS.items():
        build_block(block_name, patterns)

if __name__ == "__main__":
    main()
