from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import IsProfessor, IsStaff
from utils.pdfgen import pdfgen
from utils.reports import (
    generate_efficiency_analysis,
    generate_financial_report,
    generate_student_academic_report,
    identify_students_needing_notification,
)
from utils.subject_utils import get_subject_names

from .models import (
    Contract,
    Enrollment,
    Grade,
    Guardian,
    Presence,
    Student,
    Suspension,
    Tuition,
    Warning,
)
from .serializers import (
    ContractSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    GuardianSerializer,
    PresenceSerializer,
    StudentSerializer,
    SuspensionSerializer,
    TuitionSerializer,
    WarningSerializer,
)


def _filter_student_related_queryset(queryset, user, allow_professor=True):
    if user.is_staff or user.is_superuser:
        return queryset
    role = getattr(user, "role", None)
    if allow_professor and role == "PROFESSOR":
        return queryset
    if role == "STUDENT":
        return queryset.filter(student__user=user)
    if role == "GUARDIAN":
        return queryset.filter(student__guardians__user=user).distinct()
    return queryset.none()


class StudentViewSet(viewsets.ModelViewSet):
    queryset = (
        Student.objects.select_related("group", "group__itinerary", "user")
        .prefetch_related(
            "grade",
            "presence",
            "guardians",
            "warnings__issued_by",
            "suspensions__issued_by",
        )
        .all()
        .order_by("full_name")
    )
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "full_name",
        "registration_number",
        "phone_number",
        "email",
        "cpf",
        "birthday",
        "address",
        "group__full_name",
        "group__short_name",
        "group__itinerary__full_name",
        "group__itinerary__short_name",
        "created_at",
    ]

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "download_grades_pdf",
            "download_presence_pdf",
            "academic_report",
            "download_academic_report",
        ]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["students_needing_attention", "efficiency_analysis"]:
            self.permission_classes = [IsProfessor]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, "role", None) == "PROFESSOR":
            return queryset
        if getattr(user, "role", None) == "STUDENT":
            return queryset.filter(user=user)
        if getattr(user, "role", None) == "GUARDIAN":
            return queryset.filter(guardians__user=user).distinct()
        return queryset.none()

    @action(detail=True, methods=["get"], url_path="download-grades")
    def download_grades_pdf(self, request, pk=None):
        student = self.get_object()
        subjects = get_subject_names()
        current_year = timezone.now().year
        all_grades = Grade.objects.filter(
            student=student, year=current_year
        ).select_related("subject")

        grades_by_subject = {}
        for grade in all_grades:
            if not grade.subject or not grade.bimester:
                continue
            subject_name = grade.subject.full_name
            if subject_name not in grades_by_subject:
                grades_by_subject[subject_name] = [None, None, None, None]
            try:
                bimester_num = int(grade.bimester[0])
                if 1 <= bimester_num <= 4:
                    grades_by_subject[subject_name][bimester_num - 1] = grade.value
            except (ValueError, IndexError):
                continue

        data = {
            subject: grades_by_subject.get(subject, [None, None, None, None])
            for subject in subjects
        }
        return pdfgen(
            "grades.html",
            {"student": student, "data": data},
            f"Grades_{student.full_name}.pdf",
        )

    @action(detail=True, methods=["get"], url_path="download-presence")
    def download_presence_pdf(self, request, pk=None):
        student = self.get_object()
        current_year = timezone.now().year
        presence_records = Presence.objects.filter(
            student=student, date__year=current_year
        ).order_by("date")
        return pdfgen(
            "presence.html",
            {"student": student, "data": presence_records},
            f"Presence_{student.full_name}.pdf",
        )

    @action(detail=True, methods=["get"], url_path="academic-report")
    def academic_report(self, request, pk=None):
        """Generate comprehensive academic report for student"""
        student = self.get_object()
        report = generate_student_academic_report(student)
        return Response(report)

    @action(detail=True, methods=["get"], url_path="download-academic-report")
    def download_academic_report(self, request, pk=None):
        """Download comprehensive academic report PDF"""
        current_year = timezone.now().year
        student = self.get_object()
        report = generate_student_academic_report(student, year=current_year)

        context = {
            "student": student,
            "grades": report["grades"],
            "attendance": report["attendance"],
            "discipline": report["discipline"],
            "now": timezone.now(),
        }

        return pdfgen(
            "academic_report.html",
            context,
            f"Relatorio_Academico_{student.full_name}.pdf",
        )

    @action(detail=False, methods=["get"], url_path="students-needing-attention")
    def students_needing_attention(self, request):
        """Identify students needing notifications"""
        notifications = identify_students_needing_notification()
        return Response(notifications)

    @action(detail=False, methods=["get"], url_path="efficiency-analysis")
    def efficiency_analysis(self, request):
        """Generate efficiency analysis (approval and dropout rates) for all students"""
        year = request.query_params.get("year", None)
        if year is not None:
            try:
                year = int(year)
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid year parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        analysis = generate_efficiency_analysis(None, year)
        return Response(analysis)


class GradeViewSet(viewsets.ModelViewSet):
    queryset = (
        Grade.objects.select_related("student", "subject")
        .all()
        .order_by("student__full_name", "subject__full_name", "year", "bimester")
    )
    serializer_class = GradeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "student__full_name",
        "student__registration_number",
        "subject__full_name",
        "subject__short_name",
        "year",
        "bimester",
        "value",
        "created_at",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsProfessor]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=True
        )


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = (
        Guardian.objects.select_related("student", "user").all().order_by("full_name")
    )
    serializer_class = GuardianSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "full_name",
        "student__full_name",
        "student__registration_number",
        "phone_number",
        "cpf",
        "email",
        "birthday",
        "address",
        "created_at",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, "role", None) == "PROFESSOR":
            return queryset
        if getattr(user, "role", None) == "GUARDIAN":
            return queryset.filter(user=user)
        if getattr(user, "role", None) == "STUDENT":
            return queryset.filter(student__user=user)
        return queryset.none()


class ContractViewSet(viewsets.ModelViewSet):
    queryset = (
        Contract.objects.select_related("guardian", "student")
        .all()
        .order_by("-created_at")
    )
    serializer_class = ContractSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "guardian__full_name",
        "guardian__cpf",
        "student__full_name",
        "student__registration_number",
        "created_at",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "download_contract_pdf"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=False
        )

    @action(detail=True, methods=["get"], url_path="download-contract")
    def download_contract_pdf(self, request, pk=None):
        contract = self.get_object()
        guardian_name = (
            contract.guardian.full_name if contract.guardian else "Responsavel"
        )
        student_name = contract.student.full_name if contract.student else "Estudante"
        return pdfgen(
            "contract.html",
            {"data": contract},
            f"Contract_{contract.id}_{guardian_name}-{student_name}.pdf",
        )


class PresenceViewSet(viewsets.ModelViewSet):
    queryset = (
        Presence.objects.select_related("student")
        .all()
        .order_by("student__full_name", "date")
    )
    serializer_class = PresenceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "student__full_name",
        "student__registration_number",
        "date",
        "presence",
        "created_at",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsProfessor]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=True
        )

    @action(detail=False, methods=["get"], url_path="absence-report")
    def absence_report(self, request):
        """Generate absence report and identify students with >25% absences"""
        students_stats = (
            Student.objects.annotate(
                total_days=Count("presence"),
                absences=Count("presence", filter=Q(presence__presence=False)),
            )
            .filter(total_days__gt=0)
            .order_by("full_name")
        )

        students_with_absences = []
        for student in students_stats:
            absence_rate = (student.absences / student.total_days) * 100
            students_with_absences.append(
                {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "total_days": student.total_days,
                    "absences": student.absences,
                    "absence_rate": round(absence_rate, 2),
                    "needs_notification": absence_rate > 25,
                }
            )

        return Response(students_with_absences)


class WarningViewSet(viewsets.ModelViewSet):
    queryset = (
        Warning.objects.select_related("student", "issued_by")
        .all()
        .order_by("-date")
    )
    serializer_class = WarningSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "student__full_name",
        "student__registration_number",
        "reason",
        "date",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=True
        )


class SuspensionViewSet(viewsets.ModelViewSet):
    queryset = (
        Suspension.objects.select_related("student", "issued_by")
        .all()
        .order_by("-start_date")
    )
    serializer_class = SuspensionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "student__full_name",
        "student__registration_number",
        "reason",
        "start_date",
        "end_date",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=True
        )


class TuitionViewSet(viewsets.ModelViewSet):
    queryset = (
        Tuition.objects.select_related("student").all().order_by("-due_date")
    )
    serializer_class = TuitionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "student__full_name",
        "student__registration_number",
        "status",
        "due_date",
        "reference_month",
    ]

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "payment_history",
            "financial_report",
            "download_financial_report",
        ]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=False
        )

    def _resolve_target_student(self, request):
        student_id = request.query_params.get("student_id")
        user = request.user
        allowed_students = Student.objects.all()
        if not (user.is_staff or user.is_superuser):
            role = getattr(user, "role", None)
            if role == "STUDENT":
                allowed_students = allowed_students.filter(user=user)
            elif role == "GUARDIAN":
                allowed_students = allowed_students.filter(guardians__user=user)
            else:
                allowed_students = allowed_students.none()

        if student_id:
            try:
                student_id_int = int(student_id)
            except (ValueError, TypeError):
                return None, Response(
                    {"error": "Invalid student_id parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            student = get_object_or_404(allowed_students, id=student_id_int)
            return student, None

        if not (user.is_staff or user.is_superuser):
            student = allowed_students.first()
            if not student:
                return None, Response(
                    {"error": "Student not found for current user"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return student, None

        return None, None

    @action(detail=False, methods=["get"], url_path="payment-history")
    def payment_history(self, request):
        """Get payment history for accessible students"""
        student, error_response = self._resolve_target_student(request)
        if error_response:
            return error_response

        tuitions = self.get_queryset().order_by("-reference_month")
        if student:
            tuitions = tuitions.filter(student=student)

        serializer = self.get_serializer(tuitions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="financial-report")
    def financial_report(self, request):
        """Generate financial report"""
        student, error_response = self._resolve_target_student(request)
        if error_response:
            return error_response
        report = generate_financial_report(student)
        return Response(report)

    @action(detail=False, methods=["get"], url_path="download-financial-report")
    def download_financial_report(self, request):
        """Download financial report PDF"""
        current_year = timezone.now().year
        student, error_response = self._resolve_target_student(request)
        if error_response:
            return error_response
        report = generate_financial_report(student, year=current_year)

        context = {
            "student": student,
            "summary": report["summary"],
            "payment_history": report["payment_history"],
            "now": timezone.now(),
        }

        filename = (
            f"Relatorio_Financeiro_{student.full_name}.pdf"
            if student
            else "Relatorio_Financeiro_Geral.pdf"
        )

        return pdfgen(
            "financial_report.html",
            context,
            filename,
        )


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = (
        Enrollment.objects.select_related("student", "group")
        .all()
        .order_by("-year", "-enrollment_date")
    )
    serializer_class = EnrollmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "student__full_name",
        "student__registration_number",
        "group__full_name",
        "year",
        "status",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()

    def get_queryset(self):
        return _filter_student_related_queryset(
            super().get_queryset(), self.request.user, allow_professor=True
        )
