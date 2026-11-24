# Generated manually for the academic project.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="ContactRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="nome")),
                ("email", models.EmailField(max_length=254, verbose_name="e-mail")),
                ("message", models.TextField(verbose_name="mensagem")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ], options={"verbose_name": "registro de contato", "verbose_name_plural": "registros de contato", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="nome")),
                ("description", models.TextField(verbose_name="descrição")),
                ("date", models.DateField(verbose_name="data")),
                ("time", models.TimeField(verbose_name="horário")),
                ("location", models.CharField(max_length=180, verbose_name="local")),
                ("responsible", models.CharField(max_length=120, verbose_name="responsável")),
                ("status", models.CharField(choices=[("PLANEJADO", "Planejado"), ("CONFIRMADO", "Confirmado"), ("CANCELADO", "Cancelado"), ("FINALIZADO", "Finalizado")], default="PLANEJADO", max_length=15, verbose_name="status")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ], options={"verbose_name": "evento", "verbose_name_plural": "eventos", "ordering": ["date", "time"]},
        ),
    ]

