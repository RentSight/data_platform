# scripts/publish_to_db.py
from __future__ import annotations

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "data" / "gold"

PG_CONN = "postgresql+psycopg2://rentsight:rentsight@localhost:5432/rentsight"

TABLES = {
    "gold_price_by_neighbourhood_roomtype": GOLD_DIR / "gold_price_by_neighbourhood_roomtype.parquet",
    "gold_availability_by_neighbourhood_roomtype": GOLD_DIR / "gold_availability_by_neighbourhood_roomtype.parquet",
    "gold_reviews_by_neighbourhood": GOLD_DIR / "gold_reviews_by_neighbourhood.parquet",
    "gold_cost_benefit_ranking": GOLD_DIR / "gold_cost_benefit_ranking.parquet",
}

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_price_neigh_room ON gold_price_by_neighbourhood_roomtype(neighbourhood, room_type_simulated);",
    "CREATE INDEX IF NOT EXISTS idx_avail_neigh_room ON gold_availability_by_neighbourhood_roomtype(neighbourhood, room_type_simulated);",
    "CREATE INDEX IF NOT EXISTS idx_reviews_neigh ON gold_reviews_by_neighbourhood(neighbourhood);",
    "CREATE INDEX IF NOT EXISTS idx_cb_neigh_room ON gold_cost_benefit_ranking(neighbourhood, room_type_simulated);",
]

def main():
    engine = create_engine(PG_CONN)

    for table, parquet_file in TABLES.items():
        if not parquet_file.exists():
            raise FileNotFoundError(f"Não encontrei {parquet_file}. Rode scripts/run_pipeline.py primeiro.")

        df = pd.read_parquet(parquet_file)
        df.to_sql(table, engine, if_exists="replace", index=False)
        print(f"[publish_to_db] OK -> {table} ({len(df)} linhas)")

    with engine.begin() as conn:
        for stmt in INDEXES_SQL:
            conn.execute(text(stmt))

    print("\n✅ Banco pronto: backend pode consumir via Postgres.")

if __name__ == "__main__":
    main()
