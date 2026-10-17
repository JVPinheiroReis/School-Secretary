from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from students.models import Student, Guardian, Contract, Grade, Presence
from school.models import Group, Subject


class StudentModelsTest(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.user_student = self.User.objects.create_user(
            email="student_user@example.com", password="password123"
        )
        self.user_guardian = self.User.objects.create_user(
            email="guardian_user@example.com", password="password123"
        )
        self.group = Group.objects.create(full_name="Test Group", short_name="TG")
        self.subject = Subject.objects.create(full_name="Test Subject", short_name="TS")

        self.student = Student.objects.create(
            user=self.user_student,
            full_name="Student Test",
            registration_number="STU001",
            phone_number="(86) 98870-1869",
            cpf="64382979099",
            birthday="2005-01-01",
            address="71880729",
            group=self.group,
        )
        self.guardian = Guardian.objects.create(
            user=self.user_guardian,
            full_name="Guardian Test",
            student=self.student,
            phone_number="(86) 98870-1869",
            cpf="35603513080",
            birthday="1980-01-01",
            address="71880729",
        )

    def test_student_creation(self):
        self.assertEqual(self.student.full_name, "Student Test")
        self.assertEqual(self.student.user, self.user_student)
        self.assertEqual(self.student.registration_number, "STU001")
        self.assertIsNotNone(self.student.created_at)

    def test_guardian_creation(self):
        self.assertEqual(self.guardian.full_name, "Guardian Test")
        self.assertEqual(self.guardian.user, self.user_guardian)
        self.assertEqual(self.guardian.student, self.student)
        self.assertIsNotNone(self.guardian.created_at)

    def test_contract_creation(self):
        contract = Contract.objects.create(guardian=self.guardian, student=self.student)
        self.assertEqual(contract.guardian, self.guardian)
        self.assertEqual(contract.student, self.student)
        self.assertIsNotNone(contract.created_at)

    def test_grade_creation(self):
        grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            year=2024,
            bimester="1B",
            value=8.5,
        )
        self.assertEqual(grade.student, self.student)
        self.assertEqual(grade.subject, self.subject)
        self.assertEqual(grade.year, 2024)
        self.assertEqual(grade.bimester, "1B")
        self.assertEqual(grade.value, 8.5)
        self.assertIsNotNone(grade.created_at)

    def test_presence_creation(self):
        presence = Presence.objects.create(
            student=self.student, date=timezone.now().date(), presence=True
        )
        self.assertEqual(presence.student, self.student)
        self.assertEqual(presence.date, timezone.now().date())
        self.assertTrue(presence.presence)
        self.assertIsNotNone(presence.created_at)

    def test_contract_str_handles_none_relations(self):
        contract = Contract.objects.create(guardian=None, student=None)
        self.assertIn("SEM RESPONSÁVEL", str(contract))
        self.assertIn("SEM ESTUDANTE", str(contract))
