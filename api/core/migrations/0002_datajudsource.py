from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataJudSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_processo", models.CharField(max_length=64)),
                ("tribunal", models.CharField(max_length=32)),
                ("grau", models.CharField(max_length=32)),
                ("data_ajuizamento", models.CharField(blank=True, max_length=64)),
                ("data_ultima_atualizacao", models.CharField(blank=True, max_length=64)),
                ("source_id", models.CharField(blank=True, max_length=128)),
                ("assuntos", models.JSONField(default=list)),
                ("movimentos", models.JSONField(default=list)),
                ("raw_source", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "datajud_sources",
            },
        ),
        migrations.AddConstraint(
            model_name="datajudsource",
            constraint=models.UniqueConstraint(
                fields=("numero_processo", "tribunal", "grau"),
                name="uniq_datajud_numero_tribunal_grau",
            ),
        ),
    ]
