import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load LeandroRibeiro/JurisTCU from HuggingFace and write docs/qrels/queries tables to the configured SQLite database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo",
            default="LeandroRibeiro/JurisTCU",
            help="HuggingFace dataset repository (default: LeandroRibeiro/JurisTCU)",
        )
        parser.add_argument(
            "--db",
            default=None,
            help="Path to the SQLite file. Defaults to the database configured in settings.",
        )
        parser.add_argument(
            "--if-exists",
            default="replace",
            choices=["replace", "append", "fail"],
            help="Behaviour when the table already exists (default: replace).",
        )

    def handle(self, *args, **options):
        try:
            from datasets import load_dataset
        except ImportError:
            self.stderr.write(self.style.ERROR("'datasets' is not installed. Run: uv add datasets"))
            return

        repo = options["repo"]
        if_exists = options["if_exists"]

        db_path = options["db"]
        if db_path is None:
            db_path = settings.DATABASES["default"]["NAME"]
        db_path = Path(db_path)

        self.stdout.write(f"Loading dataset from {repo} ...")

        tables = {
            "docs":    "doc.csv",
            "qrels":   "qrel.csv",
            "queries": "query.csv",
        }

        con = sqlite3.connect(db_path)

        for table_name, filename in tables.items():
            self.stdout.write(f"  [{filename}] → table '{table_name}' ...", ending="")
            ds = load_dataset(repo, data_files=filename, split="train")
            df = ds.to_pandas()
            df.to_sql(table_name, con, if_exists=if_exists, index=False)
            self.stdout.write(self.style.SUCCESS(f" {len(df)} rows"))

        con.close()
        self.stdout.write(self.style.SUCCESS(f"\nDone. Database saved to: {db_path}"))
