from rest_framework import serializers

from .models import (
    AgendaItem,
    Book,
    Event,
    EventRegistration,
    Group,
    Itinerary,
    Lesson,
    Notification,
    Professor,
    Room,
    RoomReservation,
    SchoolRecord,
    Subject,
    WeeklyLessonPlan,
)


class SubjectCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "short_name", "full_name"]


class ItineraryCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ["id", "short_name", "full_name"]


class GroupCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "short_name", "full_name"]


class ProfessorCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ["id", "full_name", "cpf", "phone_number"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    itinerary_details = ItineraryCompactSerializer(source="itinerary", read_only=True)

    class Meta:
        model = Group
        fields = "__all__"


class ProfessorSerializer(serializers.ModelSerializer):
    subject_details = SubjectCompactSerializer(source="subject", read_only=True)

    class Meta:
        model = Professor
        exclude = ["user"]
        extra_kwargs = {"user": {"read_only": True}}


class SchoolRecordSerializer(serializers.ModelSerializer):
    student_details = serializers.SerializerMethodField()

    class Meta:
        model = SchoolRecord
        fields = "__all__"

    def get_student_details(self, obj):
        if not obj.student:
            return None
        from students.serializers import StudentCompactSerializer

        return StudentCompactSerializer(obj.student).data


class BookSerializer(serializers.ModelSerializer):
    tenant_details = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = "__all__"

    def get_tenant_details(self, obj):
        if not obj.tenant:
            return None
        from students.serializers import StudentCompactSerializer

        return StudentCompactSerializer(obj.tenant).data


class LessonSerializer(serializers.ModelSerializer):
    group_details = GroupCompactSerializer(source="group", read_only=True)
    professor_details = ProfessorCompactSerializer(source="professor", read_only=True)
    subject_details = SubjectCompactSerializer(source="subject", read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class AgendaItemSerializer(serializers.ModelSerializer):
    subject_details = SubjectCompactSerializer(source="subject", read_only=True)

    class Meta:
        model = AgendaItem
        fields = "__all__"


class WeeklyLessonPlanSerializer(serializers.ModelSerializer):
    professor_details = ProfessorCompactSerializer(source="professor", read_only=True)
    lesson_details = LessonSerializer(source="lesson", read_only=True)

    class Meta:
        model = WeeklyLessonPlan
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    registrations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"

    def get_registrations_count(self, obj):
        if hasattr(obj, "registrations_count_annotated"):
            return obj.registrations_count_annotated
        return obj.registrations.count()


class EventRegistrationSerializer(serializers.ModelSerializer):
    event_details = EventSerializer(source="event", read_only=True)
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = EventRegistration
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class RoomReservationSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source="room", read_only=True)
    professor_name = serializers.CharField(
        source="reserved_by.full_name", read_only=True
    )

    class Meta:
        model = RoomReservation
        fields = "__all__"

    def validate(self, attrs):
        room = attrs.get("room") or getattr(self.instance, "room", None)
        date = attrs.get("date") or getattr(self.instance, "date", None)
        start_time = attrs.get("start_time") or getattr(
            self.instance, "start_time", None
        )
        end_time = attrs.get("end_time") or getattr(self.instance, "end_time", None)

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                "A hora de término deve ser posterior à hora de início."
            )
        if room and date and start_time and end_time:
            overlapping = RoomReservation.objects.filter(
                room=room,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError(
                    "Esta sala já possui uma reserva conflitante neste horário."
                )
        return attrs


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source="recipient.name", read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
