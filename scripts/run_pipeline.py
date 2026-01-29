# scripts/run_pipeline.py
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

RAW_CSV = ROOT / "data" / "raw" / "airbnb_RJ.csv"

BRONZE_DIR = ROOT / "data" / "bronze"
SILVER_DIR = ROOT / "data" / "silver"
GOLD_DIR = ROOT / "data" / "gold"

BRONZE_FILE = BRONZE_DIR / "listings_bronze_rj.parquet"
SILVER_FILE = SILVER_DIR / "listings_silver_rj.parquet"

GOLD_PRICE = GOLD_DIR / "gold_price_by_neighbourhood_roomtype.parquet"
GOLD_AVAIL = GOLD_DIR / "gold_availability_by_neighbourhood_roomtype.parquet"
GOLD_REVIEWS = GOLD_DIR / "gold_reviews_by_neighbourhood.parquet"
GOLD_COST_BENEFIT = GOLD_DIR / "gold_cost_benefit_ranking.parquet"


VALID_ROOM_TYPES = ["Entire home/apt", "Private room", "Shared room", "Hotel room"]


def ensure_dirs():
    for p in [BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def read_raw() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"RAW não encontrado: {RAW_CSV}. Rode scripts/download_data.py primeiro.")

    # Mantém tudo como string inicialmente para “imitar” o mundo real
    df = pd.read_csv(RAW_CSV, dtype=str)
    return df


def bronze(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Bronze: basicamente cópia em Parquet (com schema igual ao raw)
    df_raw.to_parquet(BRONZE_FILE, index=False)
    return df_raw


def safe_to_float(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("float64")


def safe_to_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def safe_to_date(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce").dt.date


def silver(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Seleciona exatamente suas colunas
    cols = [
        "id", "neighbourhood", "latitude", "longitude", "room_type", "price",
        "minimum_nights", "number_of_reviews", "last_review",
        "reviews_per_month", "availability_365"
    ]
    missing = [c for c in cols if c not in df_raw.columns]
    if missing:
        raise KeyError(f"Colunas ausentes no CSV: {missing}. Confere o arquivo RAW e o cabeçalho.")

    df = df_raw[cols].copy()

    # Ajuste no ID (row_number) como no notebook
    df["id"] = np.arange(1, len(df) + 1, dtype=np.int64)

    # Casts (equivalente ao try_cast)
    df["price"] = safe_to_float(df["price"])
    df["minimum_nights"] = safe_to_int(df["minimum_nights"])
    df["number_of_reviews"] = safe_to_int(df["number_of_reviews"])
    df["last_review"] = safe_to_date(df["last_review"])
    df["reviews_per_month"] = safe_to_float(df["reviews_per_month"])
    df["availability_365"] = safe_to_int(df["availability_365"])
    df["latitude"] = safe_to_float(df["latitude"])
    df["longitude"] = safe_to_float(df["longitude"])
    df["room_type"] = df["room_type"].astype("string")

    # Room type clean + simulate
    norm = df["room_type"].str.strip().str.lower()

    mapping = {
        "entire home/apt": "Entire home/apt",
        "private room": "Private room",
        "shared room": "Shared room",
        "hotel room": "Hotel room",
    }
    clean = norm.map(mapping)

    # Random (1 por linha) para simular
    rng = np.random.default_rng(42)
    r = rng.random(len(df))

    simulated = clean.copy()
    simulated = simulated.where(simulated.notna(), other=pd.Series(np.select(
        [r < 0.25, r < 0.50, r < 0.75],
        ["Entire home/apt", "Private room", "Shared room"],
        default="Hotel room"
    ), index=df.index))

    df["room_type_simulated"] = simulated.astype("string")

    # Drop original room_type (fica só o simulated)
    df = df.drop(columns=["room_type"])

    df.to_parquet(SILVER_FILE, index=False)
    return df


def gold(df_silver: pd.DataFrame) -> None:
    # Gold 1: Price por bairro e tipo
    df_price = df_silver[df_silver["price"].notna()].copy()
    gold_price = (
        df_price
        .groupby(["neighbourhood", "room_type_simulated"], dropna=False)
        .agg(
            listings_count=("id", "count"),
            avg_price=("price", "mean"),
            p50_price=("price", lambda x: float(np.nanpercentile(x, 50))),
            p90_price=("price", lambda x: float(np.nanpercentile(x, 90))),
        )
        .reset_index()
    )
    gold_price.to_parquet(GOLD_PRICE, index=False)

    # Gold 2: Availability por bairro e tipo
    df_av = df_silver[df_silver["availability_365"].notna()].copy()
    # availability_365 é Int64; converte pra float pra percentile
    av_float = df_av["availability_365"].astype("float64")
    df_av = df_av.assign(_availability_float=av_float)

    gold_avail = (
        df_av
        .groupby(["neighbourhood", "room_type_simulated"], dropna=False)
        .agg(
            listings_count=("id", "count"),
            avg_availability_365=("availability_365", lambda x: float(pd.to_numeric(x, errors="coerce").mean())),
            p50_availability_365=("_availability_float", lambda x: float(np.nanpercentile(x, 50))),
        )
        .reset_index()
    )
    gold_avail.to_parquet(GOLD_AVAIL, index=False)

    # Gold 3: Reviews por bairro
    gold_reviews = (
        df_silver
        .groupby(["neighbourhood"], dropna=False)
        .agg(
            listings_count=("id", "count"),
            avg_number_of_reviews=("number_of_reviews", lambda x: float(pd.to_numeric(x, errors="coerce").mean())),
            avg_reviews_per_month=("reviews_per_month", "mean"),
        )
        .reset_index()
    )
    gold_reviews.to_parquet(GOLD_REVIEWS, index=False)

    # Gold 4: Cost-benefit ranking (join price + avail)
    merged = gold_price.merge(
        gold_avail[["neighbourhood", "room_type_simulated", "p50_availability_365"]],
        on=["neighbourhood", "room_type_simulated"],
        how="inner",
    )
    merged["cost_benefit_score"] = merged["p50_price"] / (merged["p50_availability_365"] + 1.0)
    gold_cost_benefit = merged.sort_values("cost_benefit_score", ascending=True)
    gold_cost_benefit.to_parquet(GOLD_COST_BENEFIT, index=False)


def main():
    ensure_dirs()

    df_raw = read_raw()
    bronze(df_raw)

    df_silver = silver(df_raw)
    gold(df_silver)

    print("\n✅ Pipeline (pandas) concluída!")
    print(f"RAW:    {RAW_CSV}")
    print(f"BRONZE: {BRONZE_FILE}")
    print(f"SILVER: {SILVER_FILE}")
    print(f"GOLD:   {GOLD_DIR}")


if __name__ == "__main__":
    main()
