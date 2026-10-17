from django.db import models
from django.utils import timezone
from utils.date import get_today
from utils.validators import cep_validator, cpf_validator, phone_validator

DAY_CHOICES = [
    (0, "Domingo"),
    (1, "Segunda"),
    (2, "Terça"),
    (3, "Quarta"),
    (4, "Quinta"),
    (5, "Sexta"),
    (6, "Sábado"),
]

LESSONS_PER_DAY = 6


class Subject(models.Model):
    short_name = models.CharField(
        verbose_name="Nome curto",
        max_length=200,
        unique=True,
        blank=False,
        null=True,
    )

    full_name = models.CharField(
        verbose_name="Nome completo",
        max_length=200,
        unique=True,
        blank=False,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Matéria"
        verbose_name_plural = "Matérias"


class Itinerary(models.Model):
    full_name = models.CharField(
        verbose_name="Nome completo",
        max_length=200,
        unique=True,
        blank=False,
        null=True,
    )

    short_name = models.CharField(
        verbose_name="Nome curto",
        max_length=200,
        unique=True,
        blank=False,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Itinerário"
        verbose_name_plural = "Itinerários"


class Group(models.Model):
    full_name = models.CharField(
        verbose_name="Nome completo",
        max_length=200,
        unique=True,
        null=True,
    )

    short_name = models.CharField(
        verbose_name="Nome curto",
        max_length=200,
        unique=True,
        null=True,
    )

    itinerary = models.ForeignKey(
        "school.Itinerary",
        on_delete=models.SET_NULL,
        verbose_name="Itinerário",
        related_name="group",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"


class Professor(models.Model):
    from django.conf import settings

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Usuário",
        on_delete=models.CASCADE,
        related_name="professor_profile",
    )
    full_name = models.CharField(verbose_name="Nome completo", max_length=200)
    phone_number = models.CharField(
        verbose_name="Telefone (XX) XXXXX-XXXX",
        max_length=15,
        validators=[phone_validator],
    )
    cpf = models.CharField(
        verbose_name="CPF", max_length=11, unique=True, validators=[cpf_validator]
    )
    birthday = models.DateField(verbose_name="Data de nascimento")
    address = models.CharField(
        verbose_name="CEP", max_length=100, validators=[cep_validator]
    )
    subject = models.ForeignKey(
        "Subject",
        verbose_name="Matéria",
        on_delete=models.SET_NULL,
        related_name="professors",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em", default=timezone.now, editable=False
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"


class SchoolRecord(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        verbose_name="Estudante",
        related_name="school_record",
        blank=False,
        null=True,
    )

    description = models.TextField(
        verbose_name="Descrição",
        blank=False,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name = "Registro Escolar"
        verbose_name_plural = "Registros Escolares"


class Book(models.Model):
    name = models.CharField(
        verbose_name="Nome",
        max_length=100,
        blank=False,
        null=True,
    )
    tenant = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        verbose_name="Locatário",
        related_name="alugated_book",
        blank=True,
        null=True,
    )

    author = models.CharField(
        verbose_name="Autor",
        max_length=100,
        blank=False,
        null=True,
    )

    summary = models.TextField(
        verbose_name="Resumo",
        max_length=200,
        blank=False,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"


class Lesson(models.Model):
    group = models.ForeignKey(
        "school.Group",
        on_delete=models.SET_NULL,
        verbose_name="Turma",
        related_name="lessons",
        null=True,
        blank=False,
    )

    professor = models.ForeignKey(
        "school.Professor",
        on_delete=models.SET_NULL,
        verbose_name="Professor",
        related_name="lessons",
        null=True,
        blank=False,
    )
    subject = models.ForeignKey(
        "school.Subject",
        on_delete=models.SET_NULL,
        verbose_name="Disciplina",
        related_name="lessons",
        null=True,
        blank=False,
    )
    time = models.IntegerField(
        verbose_name="Horário (1 a 6)",
        null=True,
    )
    day = models.IntegerField(
        verbose_name="Dia",
        choices=DAY_CHOICES,
        null=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return f"{self.professor} - {self.subject} - {self.get_day_display()} - {self.time}"

    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"


class AgendaItem(models.Model):
    title = models.CharField(verbose_name="Título", max_length=200)
    subject = models.ForeignKey(
        "school.Subject",
        on_delete=models.SET_NULL,
        verbose_name="Matéria",
        related_name="agenda_item",
        null=True,
        blank=False,
    )
    description = models.TextField(verbose_name="Descrição", blank=True, null=True)
    date = models.DateField(verbose_name="Data")
    time = models.TimeField(verbose_name="Hora", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Item da Agenda"
        verbose_name_plural = "Itens da Agenda"
        ordering = ["date", "time"]

    def __str__(self):
        return self.title


class WeeklyLessonPlan(models.Model):
    """Weekly lesson planning for professors"""

    professor = models.ForeignKey(
        "school.Professor",
        on_delete=models.CASCADE,
        verbose_name="Professor",
        related_name="weekly_plans",
    )
    lesson = models.ForeignKey(
        "school.Lesson",
        on_delete=models.CASCADE,
        verbose_name="Aula",
        related_name="weekly_plans",
    )
    week_start_date = models.DateField(verbose_name="Início da semana")
    planning_content = models.TextField(
        verbose_name="Planejamento", help_text="Conteúdo programado para a semana"
    )
    objectives = models.TextField(
        verbose_name="Objetivos",
        blank=True,
        null=True,
        help_text="Objetivos de aprendizagem da semana",
    )
    resources_needed = models.TextField(
        verbose_name="Recursos necessários",
        blank=True,
        null=True,
        help_text="Materiais e recursos necessários",
    )
    notes = models.TextField(
        verbose_name="Observações",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(verbose_name="Criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Planejamento Semanal"
        verbose_name_plural = "Planejamentos Semanais"
        ordering = ["-week_start_date"]
        unique_together = ["lesson", "week_start_date"]

    def __str__(self):
        return f"{self.professor.full_name} - {self.lesson} - Semana de {self.week_start_date}"


class Event(models.Model):
    title = models.CharField(verbose_name="Título", max_length=200)
    description = models.TextField(verbose_name="Descrição", blank=True, null=True)
    location = models.CharField(
        verbose_name="Local", max_length=200, blank=True, null=True
    )
    start_date = models.DateField(verbose_name="Data de início", default=get_today)
    end_date = models.DateField(
        verbose_name="Data de término",
        default=get_today,
        blank=True,
        null=True,
    )
    start_time = models.TimeField(verbose_name="Hora de início", blank=True, null=True)
    end_time = models.TimeField(verbose_name="Hora de término", blank=True, null=True)
    allow_registration = models.BooleanField(
        verbose_name="Permitir inscrição",
        default=False,
    )
    max_participants = models.IntegerField(
        verbose_name="Máximo de participantes",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(verbose_name="Criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["start_date", "start_time"]

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="Evento",
        related_name="registrations",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        verbose_name="Estudante",
        related_name="event_registrations",
    )
    registration_date = models.DateTimeField(
        verbose_name="Data de inscrição",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Inscrição em Evento"
        verbose_name_plural = "Inscrições em Eventos"
        unique_together = ["event", "student"]

    def __str__(self):
        return f"{self.student.full_name} - {self.event.title}"


ROOM_TYPE_CHOICES = [
    ("CLASSROOM", "Sala de aula"),
    ("LABORATORY", "Laboratório"),
    ("AUDITORIUM", "Auditório"),
    ("GYM", "Ginásio"),
    ("OTHER", "Outro"),
]


class Room(models.Model):
    name = models.CharField(verbose_name="Nome", max_length=200)
    room_type = models.CharField(
        verbose_name="Tipo",
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
    )
    capacity = models.IntegerField(verbose_name="Capacidade")
    description = models.TextField(
        verbose_name="Descrição",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"


class RoomReservation(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name="Sala",
        related_name="reservations",
    )
    reserved_by = models.ForeignKey(
        "school.Professor",
        on_delete=models.CASCADE,
        verbose_name="Reservado por",
        related_name="room_reservations",
    )
    purpose = models.CharField(verbose_name="Finalidade", max_length=200)
    date = models.DateField(verbose_name="Data")
    start_time = models.TimeField(verbose_name="Hora de início")
    end_time = models.TimeField(verbose_name="Hora de término")
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name = "Reserva de Sala"
        verbose_name_plural = "Reservas de Salas"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError(
                "A hora de término deve ser posterior à hora de início."
            )
        if self.room_id and self.date and self.start_time and self.end_time:
            overlapping = RoomReservation.objects.filter(
                room_id=self.room_id,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError(
                    "Esta sala já possui uma reserva conflitante neste horário."
                )

    def __str__(self):
        return f"{self.room.name} - {self.date} - {self.reserved_by.full_name}"


NOTIFICATION_TYPE_CHOICES = [
    ("GRADE", "Nota"),
    ("ABSENCE", "Falta"),
    ("WARNING", "Advertência"),
    ("SUSPENSION", "Suspensão"),
    ("EVENT", "Evento"),
    ("ASSIGNMENT", "Trabalho"),
    ("EXAM", "Prova"),
    ("PAYMENT", "Pagamento"),
    ("GENERAL", "Geral"),
]


class Notification(models.Model):
    from django.conf import settings

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Destinatário",
        related_name="notifications",
    )
    notification_type = models.CharField(
        verbose_name="Tipo",
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
    )
    title = models.CharField(verbose_name="Título", max_length=200)
    message = models.TextField(verbose_name="Mensagem")
    read = models.BooleanField(verbose_name="Lida", default=False)
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.recipient}"
