from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from school.models import (
    Subject,
    Itinerary,
    Group,
    Professor,
    SchoolRecord,
    Book,
    Lesson,
    AgendaItem,
    Event,
)
from students.models import Student
import datetime


class SchoolModelsTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.student = Student.objects.create(
            user=self.User.objects.create_user(
                email="student@example.com", password="password123"
            ),
            full_name="Test Student",
            registration_number="STU004",
            phone_number="(86) 98870-1869",
            cpf="68588002043",
            birthday="2000-01-01",
            address="71880729",
        )

    def test_subject_creation(self):
        subject = Subject.objects.create(short_name="MATH", full_name="Mathematics")
        self.assertEqual(subject.short_name, "MATH")
        self.assertEqual(subject.full_name, "Mathematics")
        self.assertIsNotNone(subject.created_at)

    def test_itinerary_creation(self):
        itinerary = Itinerary.objects.create(short_name="FUND", full_name="Fundamental")
        self.assertEqual(itinerary.short_name, "FUND")
        self.assertEqual(itinerary.full_name, "Fundamental")
        self.assertIsNotNone(itinerary.created_at)

    def test_group_creation(self):
        itinerary = Itinerary.objects.create(short_name="MED", full_name="Médio")
        group = Group.objects.create(
            short_name="A1", full_name="Group A1", itinerary=itinerary
        )
        self.assertEqual(group.short_name, "A1")
        self.assertEqual(group.full_name, "Group A1")
        self.assertEqual(group.itinerary, itinerary)
        self.assertIsNotNone(group.created_at)

    def test_professor_creation(self):
        subject = Subject.objects.create(short_name="PHY", full_name="Physics")
        professor = Professor.objects.create(
            user=self.user,
            full_name="Test Professor",
            phone_number="(86) 98870-1869",
            cpf="56526047009",
            birthday="1980-05-10",
            address="71880729",
            subject=subject,
        )
        self.assertEqual(professor.full_name, "Test Professor")
        self.assertEqual(professor.user, self.user)
        self.assertEqual(professor.subject, subject)
        self.assertIsNotNone(professor.created_at)

    def test_school_record_creation(self):
        school_record = SchoolRecord.objects.create(
            student=self.student, description="Good behavior"
        )
        self.assertEqual(school_record.student, self.student)
        self.assertEqual(school_record.description, "Good behavior")
        self.assertIsNotNone(school_record.created_at)

    def test_book_creation(self):
        book = Book.objects.create(
            name="The Great Book",
            tenant=self.student,
            author="Author Name",
            summary="A summary of the book.",
        )
        self.assertEqual(book.name, "The Great Book")
        self.assertEqual(book.tenant, self.student)
        self.assertEqual(book.author, "Author Name")
        self.assertEqual(book.summary, "A summary of the book.")
        self.assertIsNotNone(book.created_at)

    def test_lesson_creation(self):
        group = Group.objects.create(short_name="B1", full_name="Group B1")
        subject = Subject.objects.create(short_name="CHEM", full_name="Chemistry")
        professor_user = self.User.objects.create_user(
            email="prof2@example.com", password="password123"
        )
        professor = Professor.objects.create(
            user=professor_user,
            full_name="Another Professor",
            phone_number="(86) 98870-1869",
            cpf="77808109096",
            birthday="1975-01-01",
            address="71880729",
            subject=subject,
        )
        lesson = Lesson.objects.create(
            group=group, professor=professor, subject=subject, time=1, day=1
        )
        self.assertEqual(lesson.group, group)
        self.assertEqual(lesson.professor, professor)
        self.assertEqual(lesson.subject, subject)
        self.assertEqual(lesson.time, 1)
        self.assertEqual(lesson.day, 1)
        self.assertIsNotNone(lesson.created_at)

    def test_agenda_item_creation(self):
        subject = Subject.objects.create(short_name="BIO", full_name="Biology")
        agenda_item = AgendaItem.objects.create(
            title="Homework",
            subject=subject,
            description="Read chapter 5",
            date=timezone.now().date(),
            time=timezone.now().time(),
        )
        self.assertEqual(agenda_item.title, "Homework")
        self.assertEqual(agenda_item.subject, subject)
        self.assertEqual(agenda_item.description, "Read chapter 5")
        self.assertEqual(agenda_item.date, timezone.now().date())
        self.assertEqual(
            agenda_item.time.hour, timezone.now().time().hour
        )  # Compare hours as time might differ by seconds
        self.assertIsNotNone(agenda_item.created_at)
        self.assertIsNotNone(agenda_item.updated_at)

    def test_event_creation(self):
        event = Event.objects.create(
            title="School Play",
            description="Annual school play performance",
            location="School Auditorium",
            start_date=datetime.date(2024, 10, 26),
            end_date=datetime.date(2024, 10, 26),
            start_time=datetime.time(18, 0),
            end_time=datetime.time(20, 0),
        )
        self.assertEqual(event.title, "School Play")
        self.assertEqual(event.description, "Annual school play performance")
        self.assertEqual(event.location, "School Auditorium")
        self.assertEqual(event.start_date, datetime.date(2024, 10, 26))
        self.assertEqual(event.end_date, datetime.date(2024, 10, 26))
        self.assertEqual(event.start_time, datetime.time(18, 0))
        self.assertEqual(event.end_time, datetime.time(20, 0))
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.updated_at)

    def test_room_reservation_conflict_validation(self):
        from django.core.exceptions import ValidationError
        from school.models import Room, RoomReservation

        room = Room.objects.create(
            name="Lab 1", room_type="LABORATORY", capacity=30
        )
        subject = Subject.objects.create(short_name="INF", full_name="Informatics")
        prof_user = self.User.objects.create_user(
            email="prof_room@example.com", password="password123"
        )
        professor = Professor.objects.create(
            user=prof_user,
            full_name="Room Professor",
            phone_number="(86) 98870-1869",
            cpf="56526047009",
            birthday="1980-05-10",
            address="71880729",
            subject=subject,
        )
        RoomReservation.objects.create(
            room=room,
            reserved_by=professor,
            purpose="Class 1",
            date=datetime.date(2025, 5, 10),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
        )
        conflicting = RoomReservation(
            room=room,
            reserved_by=professor,
            purpose="Class 2",
            date=datetime.date(2025, 5, 10),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(13, 0),
        )
        with self.assertRaises(ValidationError):
            conflicting.clean()
