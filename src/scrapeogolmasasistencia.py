import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

BASE_URL = "https://www.transfermarkt.es/uefa-champions-league/scorerliste/pokalwettbewerb/CL"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def to_int(text: str):
    """Convierte '12' o '1.234' -> int, None si no puede."""
    if not text:
        return None
    text = text.strip().replace(".", "").replace(",", "")
    return int(text) if text.isdigit() else None


def season_label_from_year(year: int) -> str:
    """
    1992 -> '92/93'
    1999 -> '99/00'
    2000 -> '00/01'
    2025 -> '25/26'
    """
    a = year % 100
    b = (year + 1) % 100
    return f"{a:02d}/{b:02d}"


def get_last_page_for_season(season_id: int) -> int:
    """
    Mira la primera página de esa temporada y detecta
    cuál es la última página de la paginación en 'scorerliste'.
    """
    url = f"{BASE_URL}/saison_id/{season_id}/page/1"
    print(f"   🔎 Buscando nº de páginas en: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=20)
    if resp.status_code != 200:
        print(f"   ❗ Status {resp.status_code}, asumimos 1 página.")
        return 1

    soup = BeautifulSoup(resp.text, "lxml")

    last_page = 1
    ul_tm = soup.find("ul", class_="tm-pagination")
    if not ul_tm:
        print("   ℹ️ No hay paginador: asumimos 1 página.")
        return 1

    for a in ul_tm.find_all("a"):
        txt = (a.get_text(strip=True) or "").strip()
        if txt.isdigit():
            last_page = max(last_page, int(txt))

    print(f"   ℹ️ Última página detectada para saison_id={season_id}: {last_page}")
    return last_page


def scrape_scorerlist_season(season_id: int) -> pd.DataFrame:
    """
    Scrapea TODOS los registros de 'Más goles y asistencias'
    para UNA temporada concreta.
    Columnas (en la web): 
    [Rank, Jugador, Club, Nac., Edad, Partidos, Goles, Asistencias, Puntos]
    """
    season_str = season_label_from_year(season_id)
    print(f"\n🌍 Temporada {season_str} (saison_id={season_id})")

    try:
        last_page = get_last_page_for_season(season_id)
    except Exception as e:
        print(f"   ❗ No se pudo determinar la última página: {e}")
        return pd.DataFrame()

    all_records = []

    for page in range(1, last_page + 1):
        url = f"{BASE_URL}/saison_id/{season_id}/page/{page}"
        print(f"   ▶ Page {page}/{last_page}: {url}")

        resp = requests.get(url, headers=HEADERS, timeout=20)
        print("      Status code:", resp.status_code)
        if resp.status_code != 200:
            print("      ⚠️ Página no disponible, la salto.")
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", class_="items")
        if table is None:
            print("      ❌ No hay tabla 'items' en esta página, la salto.")
            continue

        tbody = table.find("tbody")
        rows = tbody.find_all("tr", class_=["odd", "even"])
        if not rows:
            print("      ❌ Sin filas de datos en esta página, la salto.")
            continue

        page_records = []

        for row in rows:
            tds = row.find_all("td", recursive=False)
            if len(tds) < 9:
                # necesitamos las 9 columnas
                continue

            # 0: rank
            rank = to_int(tds[0].get_text(strip=True))

            # 1: jugador (inline-table con nombre + posición)
            player_cell = tds[1]

            # El <a> a veces NO tiene title, así que:
            name_tag = player_cell.find("a")
            if not name_tag:
                continue

            player_name = (name_tag.get("title") or name_tag.get_text(strip=True)).strip()
            player_url = "https://www.transfermarkt.es" + name_tag.get("href", "")

            # posición (segunda fila del inline-table), opcional
            position = None
            inline_table = player_cell.find("table", class_="inline-table")
            if inline_table:
                sub_rows = inline_table.find_all("tr")
                if len(sub_rows) >= 2:
                    pos_td = sub_rows[1].find("td")
                    if pos_td:
                        position = pos_td.get_text(strip=True)

            # 2: club
            club_cell = tds[2]
            club_link = club_cell.find("a", href=True)
            if club_link:
                club_name = club_link.get("title") or club_link.get_text(strip=True)
                club_url = "https://www.transfermarkt.es" + club_link["href"]
            else:
                club_name = None
                club_url = None

            # 3: nacionalidad
            nat_imgs = tds[3].find_all("img")
            nationalities = [img.get("title") for img in nat_imgs if img.get("title")]
            nat_str = ", ".join(nationalities) if nationalities else None

            # 4: edad
            age = to_int(tds[4].get_text(strip=True))

            # 5: partidos
            matches = to_int(tds[5].get_text(strip=True))

            # 6: goles
            goals = to_int(tds[6].get_text(strip=True))

            # 7: asistencias
            assists = to_int(tds[7].get_text(strip=True))

            # 8: puntos (goles + asistencias)
            points = to_int(tds[8].get_text(strip=True))

            page_records.append({
                "Season_id": season_id,
                "Season": season_str,
                "Rank": rank,
                "Player": player_name,
                "Player_url": player_url,
                "Position": position,
                "Club": club_name,
                "Club_url": club_url,
                "Nationalities": nat_str,
                "Age": age,
                "Matches": matches,
                "Goals": goals,
                "Assists": assists,
                "Points": points,
            })

        print(f"      ✔ Registros en esta página: {len(page_records)}")
        all_records.extend(page_records)
        time.sleep(0.5)  # para no achicharrar el servidor

    if not all_records:
        print(f"   ⚠️ Sin datos para la temporada {season_str}")
        return pd.DataFrame()

    df = pd.DataFrame(all_records)
    df = df.dropna(subset=["Player"]).reset_index(drop=True)
    print(f"   ✅ Total registros temporada {season_str}: {df.shape[0]}")
    return df


def scrape_scorerlist_1992_to_now(start_year: int = 1992, end_year: int = 2025) -> pd.DataFrame:
    """
    Scrapea 'Más goles y asistencias' de Champions desde start_year (92/93) hasta end_year (25/26).
    """
    all_seasons = []

    for year in range(start_year, end_year + 1):
        try:
            df_season = scrape_scorerlist_season(year)
            if not df_season.empty:
                all_seasons.append(df_season)
        except Exception as e:
            print(f"   ❗ Error en temporada {season_label_from_year(year)}: {e}")
        time.sleep(0.5)

    if not all_seasons:
        return pd.DataFrame()

    df_all = pd.concat(all_seasons, ignore_index=True)
    # Ordenamos por temporada y puntos (más puntos arriba dentro de cada año)
    df_all = df_all.sort_values(
        ["Season_id", "Points", "Goals", "Assists", "Matches"],
        ascending=[True, False, False, False, True]
    ).reset_index(drop=True)
    return df_all


if __name__ == "__main__":
    print("📊 Scrapeando GOLES + ASISTENCIAS Champions 92/93–actualidad...")

    os.makedirs("data", exist_ok=True)

    # Para probar primero, puedes hacer:
    # df = scrape_scorerlist_1992_to_now(start_year=2024, end_year=2025)
    df = scrape_scorerlist_1992_to_now(start_year=1992, end_year=2025)

    if not df.empty:
        out = "data/tfmkt_cl_goals_assists_1992_2025.csv"
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"\n✅ Archivo creado: {out}")
        print("   Registros totales:", df.shape[0])
        print("   Columnas:", list(df.columns))
        print("\nEjemplo primeras filas:\n", df.head(10))
    else:
        print("❌ No se obtuvo ningún dato.")
