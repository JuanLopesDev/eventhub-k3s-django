from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANEJADO", "Planejado"
        CONFIRMED = "CONFIRMADO", "Confirmado"
        CANCELLED = "CANCELADO", "Cancelado"
        FINISHED = "FINALIZADO", "Finalizado"

    name = models.CharField("nome", max_length=150)
    description = models.TextField("descrição")
    date = models.DateField("data")
    time = models.TimeField("horário")
    location = models.CharField("local", max_length=180)
    responsible = models.CharField("responsável", max_length=120)
    status = models.CharField("status", max_length=15, choices=Status.choices, default=Status.PLANNED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]
        verbose_name = "evento"
        verbose_name_plural = "eventos"

    def __str__(self):
        return self.name


class ContactRecord(models.Model):
    name = models.CharField("nome", max_length=120)
    email = models.EmailField("e-mail")
    message = models.TextField("mensagem")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "registro de contato"
        verbose_name_plural = "registros de contato"

    def __str__(self):
        return f"{self.name} <{self.email}>"

