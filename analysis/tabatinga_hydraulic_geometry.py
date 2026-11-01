"""Hydraulic geometry and 2023 drought ranking from an ANA HidroWeb station archive.

Usage:
    python analysis/tabatinga_hydraulic_geometry.py $FINESST_DATA_ROOT/raw/ana/Estacao_10100000_TXT_*.zip

The archive is the TXT download from HidroWeb. It holds ResumoDescarga (discharge measurements), Vazoes
(daily discharge, one row per month) and Cotas (daily stage). Works for any station code.
"""
import io
import sys
import zipfile

import numpy as np
import pandas as pd


def read_ana(z, suffix):
    name = next(n for n in z.namelist() if n.endswith(suffix))
    lines = z.read(name).decode("latin-1").splitlines()
    head = next(i for i, line in enumerate(lines) if line.startswith("EstacaoCodigo"))
    df = pd.read_csv(io.StringIO("\n".join(lines[head:])), sep=";", decimal=",", dtype=str)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
    return df


def daily_discharge(z):
    """Unpack the month-per-row Vazoes table; prefer consisted (level 2) rows over raw (level 1)."""
    v = read_ana(z, "_Vazoes.txt")
    v["lvl"] = v.NivelConsistencia.astype(int)
    v = v.sort_values(["Data", "lvl"]).drop_duplicates("Data", keep="last")
    rows = []
    for _, r in v.iterrows():
        for day in range(1, 32):
            cell = r.get(f"Vazao{day:02d}")
            if isinstance(cell, str) and cell.strip():
                try:
                    rows.append((r.Data.replace(day=day), float(cell.replace(",", ".")), r.lvl))
                except ValueError:  # day 31 in a 30-day month
                    pass
    q = pd.DataFrame(rows, columns=["date", "q", "lvl"]).set_index("date").sort_index()
    return q[~q.index.duplicated(keep="last")]


def main(path):
    z = zipfile.ZipFile(path)

    m = read_ana(z, "_ResumoDescarga.txt")
    for c in ["Cota", "Vazao", "AreaMolhada", "Largura", "VelMedia", "Profundidade"]:
        m[c] = pd.to_numeric(m[c].str.replace(",", "."), errors="coerce")
    m = m.dropna(subset=["Vazao", "Profundidade", "VelMedia", "Largura"])
    print(f"{len(m)} discharge measurements, {m.Data.min().date()} to {m.Data.max().date()}")
    lq = np.log(m.Vazao)
    for col, label in [("Profundidade", "depth"), ("VelMedia", "velocity"), ("Largura", "width")]:
        slope = np.polyfit(lq, np.log(m[col]), 1)[0]
        print(f"  {label:8s} ~ Q^{slope:.2f}  (r = {np.corrcoef(lq, np.log(m[col]))[0, 1]:.2f})")
    slope = np.polyfit(m.Cota / 100, m.Profundidade, 1)[0]
    print(f"  mean depth vs stage: {slope:.2f} m per m (r = {np.corrcoef(m.Cota, m.Profundidade)[0, 1]:.2f})")
    print(m[m.Data.dt.month.isin([9, 10, 11])].sort_values("Data")
          [["Data", "Cota", "Vazao", "Largura", "VelMedia", "Profundidade"]].tail(8).to_string(index=False))

    q = daily_discharge(z)
    base = q[(q.index.year >= 1995) & (q.index.year <= 2022)].q
    print(f"\nDaily discharge 1995-2022: mean {base.mean():,.0f} m3/s")
    print("Monthly medians:", base.groupby(base.index.month).median().round(-2).astype(int).to_dict())
    full = q.q.groupby(q.index.year).count() > 300
    annual_min = q.q.groupby(q.index.year).min()[full].sort_values()
    print("Lowest annual minima:", annual_min.head(5).round(0).to_dict())
    october = q.q[q.index.month == 10]
    print("Lowest October means:", october.groupby(october.index.year).mean().sort_values().head(5).round(0).to_dict())
    y23 = q.loc["2023"]
    if len(y23):
        doy = np.minimum(y23.q.idxmin().dayofyear, 365)
        clim_med = base.groupby(np.minimum(base.index.dayofyear, 365)).median().rolling(7, center=True, min_periods=1).mean()
        print(f"2023 minimum {y23.q.min():,.0f} on {y23.q.idxmin().date()}; median for that date {clim_med.loc[doy]:,.0f}; "
              f"consistency levels {y23.lvl.value_counts().to_dict()}")


if __name__ == "__main__":
    main(sys.argv[1])
