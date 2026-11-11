from __future__ import annotations
import pandas as pd

# смотрим ошибки валидации данных
class ValidationError(RuntimeError):
    pass

key_col= ["Steel type", "Tempering time (s)", "Tempering temperature (ºC)"]

def validate(df: pd.DataFrame) -> dict:
    if df.empty: raise ValidationError("Датафрейм пустой")
    errors: list[str] = []
    warnings: list[str] = []
# проверка данных на пропуски
    miss = df.isna().sum()     
    initial_na = int(miss.get("Initial hardness (HRC) - post quenching", 0))
    if initial_na:
        pct = initial_na / len(df) * 100
        warnings.append(f"Initial hardness (HRC) - post quenching: пропусков {initial_na} ({pct:.3f}%)")
    for col in key_col + ["Final hardness (HRC) - post tempering"]:
        n = int(df[col].isna().sum())
        if n: errors.append(f"{col}: пропусков {n}")
# проверка данных на дубликаты
    dupl_key = int(df.duplicated(subset=key_col).sum())   
    if dupl_key:
        warnings.append(
            f"Повторений по (Steel type, Tempering time, "
            f"Tempering temperature): {dupl_key}")

# проверка данных на логичность
    checks = {"Tempering time <= 0": int((df["Tempering time (s)"] <= 0).sum()),
        "Tempering temperature < 0": int((df["Tempering temperature (ºC)"] < 0).sum()),
        "Tempering temperature > 1000": int((df["Tempering temperature (ºC)"] > 1000).sum()),
        "Final hardness вне [0, 70]": int(
            ((df["Final hardness (HRC) - post tempering"] < 0)
                | (df["Final hardness (HRC) - post tempering"] > 70)).sum()),
        "Отрицательный химсостав": int(df.filter(like="%wt").lt(0).any(axis=1).sum()),
        "Сумма элементов > 100%": int(df.filter(like="%wt").sum(axis=1).gt(100).sum())}
    for name, count in checks.items():
        if count:
            errors.append(f"{name}: {count}")
    if errors:
        raise ValidationError("\n".join(errors))

    return {"rows": len(df), "warnings": warnings, "checks": checks}
