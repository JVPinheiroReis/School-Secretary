from rest_framework import serializers

from school.models import (
    Subject,
)
from school.serializers import GroupCompactSerializer, SubjectCompactSerializer

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


class StudentCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "full_name", "cpf", "phone_number"]


class GuardianCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ["id", "full_name", "cpf", "phone_number"]


class GradeCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "value", "year", "bimester"]


class PresenceCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ["id", "date", "presence"]


class GuardianSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)

    class Meta:
        model = Guardian
        exclude = ["user"]
        extra_kwargs = {"user": {"read_only": True}}


class ContractSerializer(serializers.ModelSerializer):
    guardian_details = GuardianCompactSerializer(source="guardian", read_only=True)
    student_details = StudentCompactSerializer(source="student", read_only=True)

    class Meta:
        model = Contract
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)
    subject_details = SubjectCompactSerializer(source="subject", read_only=True)

    class Meta:
        model = Grade
        fields = "__all__"


class PresenceSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)

    class Meta:
        model = Presence
        fields = "__all__"


class WarningSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.name", read_only=True)

    class Meta:
        model = Warning
        fields = "__all__"


class SuspensionSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.name", read_only=True)

    class Meta:
        model = Suspension
        fields = "__all__"


class TuitionSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)

    class Meta:
        model = Tuition
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    student_details = StudentCompactSerializer(source="student", read_only=True)
    group_details = GroupCompactSerializer(source="group", read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    group_details = GroupCompactSerializer(source="group", read_only=True)
    grades_details = serializers.SerializerMethodField()
    presence_details = PresenceSerializer(source="presence", many=True, read_only=True)
    guardians_details = GuardianSerializer(
        source="guardians", many=True, read_only=True
    )
    warnings_details = WarningSerializer(source="warnings", many=True, read_only=True)
    suspensions_details = SuspensionSerializer(
        source="suspensions", many=True, read_only=True
    )

    class Meta:
        model = Student
        exclude = ["user"]
        extra_kwargs = {"user": {"read_only": True}}

    def get_grades_details(self, obj):
        grades_details_list = []
        all_subjects = Subject.objects.all()
        bimester_index = {"1B": 0, "2B": 1, "3B": 2, "4B": 3}

        grades_by_subject = {}
        for grade in obj.grade.all():
            if grade.subject_id not in grades_by_subject:
                grades_by_subject[grade.subject_id] = [None] * 4
            idx = bimester_index.get(grade.bimester)
            if idx is not None:
                grades_by_subject[grade.subject_id][idx] = grade.value

        for subject in all_subjects:
            grades_for_subject = grades_by_subject.get(subject.id, [None] * 4)
            grades_details_list.append(
                {"subject": subject.full_name, "grades": list(grades_for_subject)}
            )

        return grades_details_list
