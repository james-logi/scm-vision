"""
inspection_log.py — 검사 이력 공용 모듈

모든 페이지에서 import해서 사용:
  from inspection_log import InspectionLog

저장 형식: data/inspection_log.csv
  timestamp, date, sku_id, sku_name, verdict, quantity, confidence,
  elapsed, image_name, source
"""

import os
import csv
import pandas as pd
from datetime import datetime

LOG_PATH = "data/inspection_log.csv"
COLUMNS = [
    "timestamp", "date", "sku_id", "sku_name",
    "verdict", "quantity", "confidence", "elapsed",
    "image_name", "source",
]


class InspectionLog:

    @staticmethod
    def save(result: dict, image_name: str = "", elapsed: float = 0.0):
        """검사 결과를 CSV에 저장"""
        os.makedirs("data", exist_ok=True)
        now = datetime.now()
        row = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "sku_id": result.get("sku_id") or "UNKNOWN",
            "sku_name": result.get("sku_name", "미분류"),
            "verdict": result.get("verdict", "UNCLASSIFIED"),
            "quantity": result.get("primary_count", 0),
            "confidence": result.get("confidence", 0),
            "elapsed": round(elapsed, 2),
            "image_name": image_name,
            "source": result.get("source", "unknown"),
        }
        file_exists = os.path.exists(LOG_PATH)
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    @staticmethod
    def load() -> pd.DataFrame:
        """전체 이력 로드"""
        if not os.path.exists(LOG_PATH):
            return pd.DataFrame(columns=COLUMNS)
        df = pd.read_csv(LOG_PATH, encoding="utf-8")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = pd.to_datetime(df["date"])
        return df

    @staticmethod
    def daily_summary() -> pd.DataFrame:
        """날짜 × SKU별 수량 집계 (다른 페이지용)"""
        df = InspectionLog.load()
        if df.empty:
            return pd.DataFrame(columns=["date", "sku_name", "total_qty", "ok_count", "ng_count"])
        ok_df = df[df["verdict"] == "OK"]
        summary = ok_df.groupby(["date", "sku_name"]).agg(
            total_qty=("quantity", "sum"),
            ok_count=("verdict", "count"),
        ).reset_index()
        ng_df = df[df["verdict"] == "NG"].groupby(["date", "sku_name"]).agg(
            ng_count=("verdict", "count")
        ).reset_index()
        result = summary.merge(ng_df, on=["date", "sku_name"], how="left")
        result["ng_count"] = result["ng_count"].fillna(0).astype(int)
        result["date"] = pd.to_datetime(result["date"])
        return result.sort_values("date", ascending=False)

    @staticmethod
    def sku_daily_qty(sku_name: str = None) -> pd.DataFrame:
        """특정 SKU의 날짜별 수량 (Page 2 등에서 사용)"""
        df = InspectionLog.load()
        if df.empty:
            return pd.DataFrame()
        ok_df = df[df["verdict"] == "OK"]
        if sku_name:
            ok_df = ok_df[ok_df["sku_name"] == sku_name]
        return ok_df.groupby(["date", "sku_name"])["quantity"].sum().reset_index()
