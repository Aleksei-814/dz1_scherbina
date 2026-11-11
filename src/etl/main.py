from __future__ import annotations
import argparse
import sys
from pathlib import Path
from .extract import URL, default_raw_path, extract_df
from .load import (target_db, rows, name,
    load_dataset, make_engine, read_creds, verify, write_to_db)
from .transform import convert_df, default_parquet_path, parquet_saving
from .validate import ValidationError, validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="etl", description="ETL-пайплайн: закалка и отпуск стали")
    parser.add_argument("command", choices=["run", "extract", "transform", "validate", "load"], help="Команда пайплайна")
    parser.add_argument("--raw-path", type=Path, default=None, help="Путь к сырому CSV")
    parser.add_argument("--processed-path", type=Path, default=None, help="Путь к parquet")
    parser.add_argument("--creds-path", type=Path, default=None, help="Путь к файлу с кредами")
    parser.add_argument("--db-name", default=target_db, help="Название базы данных")
    parser.add_argument("--schema", default="public", help="Схема PostgreSQL")
    parser.add_argument("--table", default=name, help="Название таблицы БД")
    parser.add_argument("--rows", type=int, default=rows, help="Сколько строк загрузить в БД")
    parser.add_argument("--source-url", default=URL, help="URL на гугл диск с CSV")
    parser.add_argument("--force-download", action="store_true", help="Скачать датасет заново")
    parser.add_argument("--if-exists", choices=["replace", "append", "fail"], default="replace", help="Поведение to_sql при существующей таблице")
    return parser


def print_validation_report(report: dict) -> None:
    print(f"Валидация пройдена: строк {report['rows']}")
    for name, count in report["checks"].items():
        print(f"  {name}: {count}")
    for w in report["warnings"]:
        print(f"  WARNING: {w}")


def _raw_path(args) -> Path:
    return args.raw_path or default_raw_path()


def _parquet_path(args) -> Path:
    return args.processed_path or default_parquet_path()


def do_extract(args):
    df = extract_df(csv_path=_raw_path(args), url=args.source_url, force=args.force_download)
    print(f"Сырых строк: {len(df)}")
    print(df.head(10).to_string())
    return df


def do_transform(args):
    df_raw = extract_df(csv_path=_raw_path(args), url=args.source_url, force=args.force_download)
    df = convert_df(df_raw)
    print(df.dtypes)
    parquet_saving(df, _parquet_path(args))
    return df


def do_validate(args):
    df_raw = extract_df(csv_path=_raw_path(args), url=args.source_url, force=args.force_download)
    df = convert_df(df_raw)
    report = validate(df)
    print_validation_report(report)
    return df


def do_load(args):
    df = load_dataset(parquet_path=_parquet_path(args), rows=args.rows)
    creds = read_creds(args.creds_path, args.db_name)
    engine = make_engine(creds)
    inserted = write_to_db(df, engine, schema=args.schema, table=args.table, if_exists=args.if_exists)
    verify(df, engine, schema=args.schema, table=args.table, rows=len(df))
    print(f"\nУспешно загружено {inserted} строк в {creds['db_name']}.{args.schema}.{args.table}")
    return inserted


def do_run(args):
    df_raw = extract_df(csv_path=_raw_path(args), url=args.source_url, force=args.force_download)
    print(f"Сырых строк: {len(df_raw)}")
    df = convert_df(df_raw)
    print("После convert_df:")
    print(df.dtypes)
    parquet_saving(df, _parquet_path(args))
    report = validate(df)
    print_validation_report(report)
    df_load = load_dataset(parquet_path=_parquet_path(args), rows=args.rows)
    creds = read_creds(args.creds_path, args.db_name)
    engine = make_engine(creds)
    inserted = write_to_db(df_load, engine, schema=args.schema, table=args.table, if_exists=args.if_exists)
    verify(df_load, engine, schema=args.schema, table=args.table, rows=len(df_load))
    print(f"\nУспешно загружено {inserted} строк в {creds['db_name']}.{args.schema}.{args.table}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not 1 <= args.rows <= 100:
        parser.error("--rows должен быть от 1 до 100")
    try:
        if args.command == "extract": do_extract(args)
        elif args.command == "transform": do_transform(args)
        elif args.command == "validate": do_validate(args)
        elif args.command == "load": do_load(args)
        elif args.command == "run": do_run(args)
    except (ValidationError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
