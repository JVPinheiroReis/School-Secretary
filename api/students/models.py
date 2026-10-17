from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from utils.date import get_current_year, get_today
from utils.validators import cep_validator, cpf_validator, phone_validator

BIMESTER_CHOICES = [
    ("1B", "1º Bimestre"),
    ("2B", "2º Bimestre"),
    ("3B", "3º Bimestre"),
    ("4B", "4º Bimestre"),
]


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Usuário",
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    full_name = models.CharField(verbose_name="Nome completo", max_length=200)
    registration_number = models.CharField(
        verbose_name="Número de matrícula", max_length=6, unique=True
    )
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
    group = models.ForeignKey(
        "school.Group",
        verbose_name="Turma",
        on_delete=models.SET_NULL,
        related_name="students",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em", default=timezone.now, editable=False
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Estudante"
        verbose_name_plural = "Estudantes"


class Guardian(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Usuário",
        on_delete=models.CASCADE,
        related_name="guardian_profile",
    )
    full_name = models.CharField(verbose_name="Nome completo", max_length=200)
    student = models.ForeignKey(
        Student,
        verbose_name="Estudante",
        on_delete=models.SET_NULL,
        related_name="guardians",
        null=True,
        blank=True,
    )
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
    created_at = models.DateTimeField(
        verbose_name="Criado em", default=timezone.now, editable=False
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"


class Contract(models.Model):
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.SET_NULL,
        verbose_name="Responsável",
        related_name="contract",
        blank=False,
        null=True,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        verbose_name="Estudante",
        related_name="contract",
        blank=False,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        guardian_name = (
            self.guardian.full_name.upper() if self.guardian else "SEM RESPONSÁVEL"
        )
        student_name = (
            self.student.full_name.upper() if self.student else "SEM ESTUDANTE"
        )
        return f"Contract: {guardian_name} e {student_name}"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"


class Grade(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        verbose_name="Estudante",
        related_name="grade",
        blank=False,
        null=True,
    )

    subject = models.ForeignKey(
        "school.Subject",
        on_delete=models.SET_NULL,
        verbose_name="Matéria",
        related_name="grade",
        blank=False,
        null=True,
    )

    year = models.IntegerField(
        verbose_name="Ano", blank=False, null=True, default=get_current_year
    )

    bimester = models.CharField(
        verbose_name="Bimestre",
        max_length=20,
        choices=BIMESTER_CHOICES,
        blank=False,
        null=True,
    )

    value = models.FloatField(
        verbose_name="Valor",
        blank=False,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )

    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        if self.student:
            return f"{self.student.full_name}'s Bulletin"
        return "Grade (sem estudante)"

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        unique_together = ["student", "subject", "year", "bimester"]


class Presence(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        verbose_name="Estudante",
        related_name="presence",
        blank=False,
        null=True,
    )
    date = models.DateField(verbose_name="Data", default=get_today)
    presence = models.BooleanField(verbose_name="Presença")
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return f"Presence_{self.student}"

    class Meta:
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"


class Warning(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Estudante",
        related_name="warnings",
    )
    reason = models.TextField(verbose_name="Motivo")
    date = models.DateField(verbose_name="Data", default=get_today)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Emitido por",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return f"Advertência - {self.student.full_name} - {self.date}"

    class Meta:
        verbose_name = "Advertência"
        verbose_name_plural = "Advertências"


class Suspension(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Estudante",
        related_name="suspensions",
    )
    reason = models.TextField(verbose_name="Motivo")
    start_date = models.DateField(verbose_name="Data de início", default=get_today)
    end_date = models.DateField(verbose_name="Data de término")
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Emitido por",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return f"Suspensão - {self.student.full_name} - {self.start_date} a {self.end_date}"

    class Meta:
        verbose_name = "Suspensão"
        verbose_name_plural = "Suspensões"


PAYMENT_STATUS_CHOICES = [
    ("PENDING", "Pendente"),
    ("PAID", "Pago"),
    ("OVERDUE", "Atrasado"),
    ("CANCELLED", "Cancelado"),
]


class Tuition(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Estudante",
        related_name="tuitions",
    )
    amount = models.DecimalField(
        verbose_name="Valor",
        max_digits=10,
        decimal_places=2,
    )
    due_date = models.DateField(verbose_name="Data de vencimento")
    payment_date = models.DateField(
        verbose_name="Data de pagamento",
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING",
    )
    reference_month = models.DateField(verbose_name="Mês de referência")
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return f"Mensalidade - {self.student.full_name} - {self.reference_month}"

    class Meta:
        verbose_name = "Mensalidade"
        verbose_name_plural = "Mensalidades"


ENROLLMENT_STATUS_CHOICES = [
    ("PENDING", "Pendente"),
    ("APPROVED", "Aprovado"),
    ("REJECTED", "Rejeitado"),
]


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Estudante",
        related_name="enrollments",
    )
    group = models.ForeignKey(
        "school.Group",
        on_delete=models.CASCADE,
        verbose_name="Turma",
    )
    year = models.IntegerField(
        verbose_name="Ano",
        default=get_current_year,
    )
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=ENROLLMENT_STATUS_CHOICES,
        default="PENDING",
    )
    enrollment_date = models.DateField(
        verbose_name="Data de matrícula",
        default=get_today,
    )
    is_reenrollment = models.BooleanField(
        verbose_name="É rematrícula",
        default=False,
    )
    created_at = models.DateTimeField(
        verbose_name="Criado em",
        default=timezone.now,
        editable=False,
    )

    def __str__(self):
        return f"Matrícula - {self.student.full_name} - {self.year}"

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
