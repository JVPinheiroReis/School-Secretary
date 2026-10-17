"""
Utility functions for generating comprehensive academic reports
"""

from datetime import timedelta

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from school.models import Subject
from students.models import (
    Enrollment,
    Grade,
    Presence,
    Student,
    Suspension,
    Tuition,
    Warning,
)


def generate_student_academic_report(student, year=None):
    """Generate comprehensive academic report for a single student"""
    if year is None:
        year = timezone.now().year

    grades_by_subject = {}
    all_subjects = Subject.objects.all()
    student_grades = Grade.objects.filter(student=student, year=year).order_by(
        "bimester"
    )
    grades_map = {}
    for grade in student_grades:
        if grade.subject_id not in grades_map:
            grades_map[grade.subject_id] = {"1B": None, "2B": None, "3B": None, "4B": None}
        if grade.bimester in grades_map[grade.subject_id]:
            grades_map[grade.subject_id][grade.bimester] = grade.value

    for subject in all_subjects:
        bimester_grades = grades_map.get(
            subject.id, {"1B": None, "2B": None, "3B": None, "4B": None}
        )
        valid_grades = [g for g in bimester_grades.values() if g is not None]
        average = sum(valid_grades) / len(valid_grades) if valid_grades else None

        grades_by_subject[subject.full_name] = {
            "grades": bimester_grades,
            "average": round(average, 2) if average is not None else None,
        }

    # Get attendance statistics in a single aggregate query
    attendance_stats = Presence.objects.filter(student=student, date__year=year).aggregate(
        total_days=Count("id"),
        presences=Count("id", filter=Q(presence=True)),
        absences=Count("id", filter=Q(presence=False)),
    )
    total_days = attendance_stats["total_days"] or 0
    presences = attendance_stats["presences"] or 0
    absences = attendance_stats["absences"] or 0
    absence_rate = (absences / total_days * 100) if total_days > 0 else 0

    # Get disciplinary records
    warnings_qs = Warning.objects.filter(student=student, date__year=year).select_related(
        "issued_by"
    )
    suspensions_qs = Suspension.objects.filter(
        student=student, start_date__year=year
    ).select_related("issued_by")

    warnings_count = warnings_qs.count()
    suspensions_count = suspensions_qs.count()

    recent_warnings = warnings_qs.order_by("-date")[:5]
    recent_suspensions = suspensions_qs.order_by("-start_date")[:5]

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "registration_number": student.registration_number,
        "group": student.group.full_name if student.group else None,
        "grades": grades_by_subject,
        "attendance": {
            "total_days": total_days,
            "presences": presences,
            "absences": absences,
            "absence_rate": round(absence_rate, 2),
            "needs_attention": absence_rate > 25,
        },
        "discipline": {
            "warnings_count": warnings_count,
            "suspensions_count": suspensions_count,
            "recent_warnings": [
                {
                    "date": w.date.isoformat(),
                    "reason": w.reason,
                    "issued_by": w.issued_by.name if w.issued_by else None,
                }
                for w in recent_warnings
            ],
            "recent_suspensions": [
                {
                    "start_date": s.start_date.isoformat(),
                    "end_date": s.end_date.isoformat(),
                    "reason": s.reason,
                    "issued_by": s.issued_by.name if s.issued_by else None,
                }
                for s in recent_suspensions
            ],
        },
    }


def generate_group_performance_report(group):
    """Generate performance report for an entire group/class"""

    students = Student.objects.filter(group=group)
    total_students = students.count()

    # Get average grade per subject in a single aggregated query
    subject_stats = (
        Grade.objects.filter(student__group=group, subject__isnull=False)
        .values("subject__full_name")
        .annotate(
            avg_grade=Avg("value"),
            students_evaluated=Count("student", distinct=True),
        )
        .order_by("subject__full_name")
    )

    subjects_performance = [
        {
            "subject": stat["subject__full_name"],
            "average_grade": round(stat["avg_grade"], 2)
            if stat["avg_grade"] is not None
            else None,
            "students_evaluated": stat["students_evaluated"],
        }
        for stat in subject_stats
    ]

    # Attendance statistics
    attendance_stats = Presence.objects.filter(student__group=group).aggregate(
        total_presences=Count("id"),
        absences_count=Count("id", filter=Q(presence=False)),
    )
    total_presences_count = attendance_stats["total_presences"] or 0
    absences_count = attendance_stats["absences_count"] or 0

    group_absence_rate = (
        (absences_count / total_presences_count * 100)
        if total_presences_count > 0
        else 0
    )

    # Students with high absence rate in a single annotated query
    annotated_students = students.annotate(
        total_days=Count("presence"),
        absences=Count("presence", filter=Q(presence__presence=False)),
    ).filter(total_days__gt=0)

    high_absence_students = []
    for student in annotated_students:
        absence_rate = (student.absences / student.total_days) * 100
        if absence_rate > 25:
            high_absence_students.append(
                {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "absence_rate": round(absence_rate, 2),
                }
            )

    warnings_count = Warning.objects.filter(student__group=group).count()
    suspensions_count = Suspension.objects.filter(student__group=group).count()

    return {
        "group": group.full_name,
        "total_students": total_students,
        "subjects_performance": subjects_performance,
        "attendance": {
            "overall_absence_rate": round(group_absence_rate, 2),
            "students_with_high_absences": high_absence_students,
            "total_absences": absences_count,
        },
        "discipline": {
            "total_warnings": warnings_count,
            "total_suspensions": suspensions_count,
        },
    }


def generate_financial_report(student=None, year=None):
    """Generate financial report for tuition payments"""
    if year is None:
        year = timezone.now().year

    tuitions = Tuition.objects.select_related("student").filter(
        reference_month__year=year
    )
    if student:
        tuitions = tuitions.filter(student=student)
    tuitions = tuitions.order_by("-reference_month")

    stats = tuitions.aggregate(
        total_pending=Count("id", filter=Q(status="PENDING")),
        total_paid=Count("id", filter=Q(status="PAID")),
        total_overdue=Count("id", filter=Q(status="OVERDUE")),
        amount_pending=Sum("amount", filter=Q(status="PENDING")),
        amount_paid=Sum("amount", filter=Q(status="PAID")),
    )

    payment_history = []
    for tuition in tuitions[:20]:
        payment_history.append(
            {
                "student_name": tuition.student.full_name if student is None else None,
                "amount": float(tuition.amount),
                "due_date": tuition.due_date.isoformat(),
                "payment_date": tuition.payment_date.isoformat()
                if tuition.payment_date
                else None,
                "status": tuition.status,
                "reference_month": tuition.reference_month.isoformat(),
            }
        )

    return {
        "summary": {
            "total_pending": stats["total_pending"] or 0,
            "total_paid": stats["total_paid"] or 0,
            "total_overdue": stats["total_overdue"] or 0,
            "amount_pending": float(stats["amount_pending"] or 0),
            "amount_paid": float(stats["amount_paid"] or 0),
        },
        "payment_history": payment_history,
    }


def identify_students_needing_notification():
    """Identify students that need notifications based on various criteria"""

    notifications_needed = []

    students_with_attendance = (
        Student.objects.prefetch_related("guardians")
        .annotate(
            total_days=Count("presence"),
            absences=Count("presence", filter=Q(presence__presence=False)),
        )
        .filter(total_days__gt=0)
    )

    for student in students_with_attendance:
        absence_rate = (student.absences / student.total_days) * 100
        if absence_rate > 25:
            notifications_needed.append(
                {
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "guardians": [g.full_name for g in student.guardians.all()],
                    "reason": "HIGH_ABSENCE_RATE",
                    "details": f"Taxa de faltas: {round(absence_rate, 2)}%",
                    "priority": "HIGH",
                }
            )

    students_with_low_grades = (
        Student.objects.prefetch_related("guardians")
        .annotate(avg_grade=Avg("grade__value"))
        .filter(avg_grade__isnull=False, avg_grade__lt=6.0)
    )

    for student in students_with_low_grades:
        notifications_needed.append(
            {
                "student_id": student.id,
                "student_name": student.full_name,
                "guardians": [g.full_name for g in student.guardians.all()],
                "reason": "LOW_GRADES",
                "details": f"Média geral: {round(student.avg_grade, 2)}",
                "priority": "MEDIUM",
            }
        )

    overdue_tuitions = (
        Tuition.objects.filter(status="OVERDUE")
        .select_related("student")
        .prefetch_related("student__guardians")
    )

    for tuition in overdue_tuitions:
        notifications_needed.append(
            {
                "student_id": tuition.student.id,
                "student_name": tuition.student.full_name,
                "guardians": [g.full_name for g in tuition.student.guardians.all()],
                "reason": "OVERDUE_PAYMENT",
                "details": f"Mensalidade de {tuition.reference_month.strftime('%m/%Y')} vencida",
                "priority": "HIGH",
            }
        )

    return notifications_needed


def calculate_approval_rate(group=None, year=None):
    """
    Calculate approval rate (Taxa de aprovação) for students
    A student is considered approved if their average grade >= 6.0
    """
    if year is None:
        year = timezone.now().year

    students_query = Student.objects.all()
    if group:
        students_query = students_query.filter(group=group)

    total_students = students_query.count()
    if total_students == 0:
        return {
            "total_students": 0,
            "approved_students": 0,
            "failed_students": 0,
            "approval_rate": 0,
            "year": year,
            "group": group.full_name if group else "All groups",
        }

    annotated_students = students_query.annotate(
        avg_grade=Avg("grade__value", filter=Q(grade__year=year))
    ).filter(avg_grade__isnull=False)

    approved_count = 0
    failed_count = 0

    for student in annotated_students:
        if student.avg_grade >= 6.0:
            approved_count += 1
        else:
            failed_count += 1

    approval_rate = (approved_count / total_students * 100) if total_students > 0 else 0

    return {
        "total_students": total_students,
        "approved_students": approved_count,
        "failed_students": failed_count,
        "approval_rate": round(approval_rate, 2),
        "year": year,
        "group": group.full_name if group else "All groups",
    }


def calculate_dropout_rate(group=None, year=None):
    """
    Calculate dropout/evasion rate (Taxa de evasão)
    A student is considered to have dropped out if:
    - They have an enrollment in the specified year but no recent presence records
    - Or they have an absence rate > 75% in recent months
    """
    if year is None:
        year = timezone.now().year

    enrollments_query = Enrollment.objects.filter(year=year, status="APPROVED")
    if group:
        enrollments_query = enrollments_query.filter(group=group)

    total_enrolled = enrollments_query.count()
    if total_enrolled == 0:
        return {
            "total_enrolled": 0,
            "active_students": 0,
            "dropout_students": 0,
            "dropout_rate": 0,
            "year": year,
            "group": group.full_name if group else "All groups",
        }

    cutoff_date = timezone.now().date() - timedelta(days=30)
    annotated_enrollments = enrollments_query.annotate(
        recent_total=Count(
            "student__presence", filter=Q(student__presence__date__gte=cutoff_date)
        ),
        recent_absences=Count(
            "student__presence",
            filter=Q(
                student__presence__date__gte=cutoff_date,
                student__presence__presence=False,
            ),
        ),
    )

    dropout_count = 0
    active_count = 0

    for enrollment in annotated_enrollments:
        if enrollment.recent_total == 0:
            dropout_count += 1
        else:
            absence_rate = (enrollment.recent_absences / enrollment.recent_total) * 100
            if absence_rate > 75:
                dropout_count += 1
            else:
                active_count += 1

    dropout_rate = (dropout_count / total_enrolled * 100) if total_enrolled > 0 else 0

    return {
        "total_enrolled": total_enrolled,
        "active_students": active_count,
        "dropout_students": dropout_count,
        "dropout_rate": round(dropout_rate, 2),
        "year": year,
        "group": group.full_name if group else "All groups",
    }


def generate_efficiency_analysis(group=None, year=None):
    """
    Generate comprehensive efficiency analysis including approval and dropout rates
    """
    approval_data = calculate_approval_rate(group, year)
    dropout_data = calculate_dropout_rate(group, year)

    return {
        "approval_analysis": approval_data,
        "dropout_analysis": dropout_data,
        "summary": {
            "year": year or timezone.now().year,
            "group": group.full_name if group else "All groups",
            "total_students_evaluated": approval_data["total_students"],
            "approval_rate": approval_data["approval_rate"],
            "dropout_rate": dropout_data["dropout_rate"],
            "retention_rate": round(100 - dropout_data["dropout_rate"], 2),
        },
    }
