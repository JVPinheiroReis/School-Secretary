from rest_framework.test import APITestCase
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, UserProfileSerializer
from students.models import Student, Guardian
from school.models import Professor
import datetime


class UserSerializersTest(APITestCase):

    def setUp(self):
        self.User = get_user_model()
        self.student_user = self.User.objects.create_user(
            email="student_profile@example.com",
            password="password123",
            name="Student Profile",
        )
        self.student_instance = Student.objects.create(
            user=self.student_user,
            full_name="Student Profile Name",
            registration_number="STU001",
            phone_number="(86) 98870-1869",
            cpf="90240742079",
            birthday="2000-01-01",
            address="71880729",
        )
        self.guardian_user = self.User.objects.create_user(
            email="guardian_profile@example.com",
            password="password123",
            name="Guardian Profile",
            role=self.User.Role.GUARDIAN,
        )
        self.professor_user = self.User.objects.create_user(
            email="professor_profile@example.com",
            password="password123",
            name="Professor Profile",
            role=self.User.Role.PROFESSOR,
        )

        self.student_profile_data = {
            "full_name": "Student Profile Name",
            "registration_number": "STU003",
            "phone_number": "(86) 98870-1869",
            "cpf": "61096985047",
            "birthday": "2000-01-01",
            "address": "71880729",
        }
        self.guardian_profile_data = {
            "full_name": "Guardian Profile Name",
            "phone_number": "(86) 98870-1869",
            "cpf": "01226222005",
            "birthday": "1970-01-01",
            "address": "71880729",
        }
        self.professor_profile_data = {
            "full_name": "Professor Profile Name",
            "phone_number": "(86) 98870-1869",
            "cpf": "47063393081",
            "birthday": "1960-01-01",
            "address": "71880729",
            "subject": None,  # Assuming subject can be null for basic test
        }

    def test_user_serializer_create_student(self):
        data = {
            "email": "newstudent@example.com",
            "password": "password123",
            "name": "New Student",
            "role": self.User.Role.STUDENT,
            "profile": {
                "full_name": "New Student Name",
                "registration_number": "STU002",
                "phone_number": "(86) 98870-1870",
                "cpf": "97348459005",
                "birthday": "2001-01-01",
                "address": "71880730",
            },
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, "newstudent@example.com")
        self.assertEqual(user.role, self.User.Role.STUDENT)
        self.assertIsNotNone(user.student_profile)
        self.assertEqual(user.student_profile.full_name, "New Student Name")

    def test_user_serializer_create_guardian(self):
        data = {
            "email": "newguardian@example.com",
            "password": "password123",
            "name": "New Guardian",
            "role": self.User.Role.GUARDIAN,
            "profile": self.guardian_profile_data,
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, "newguardian@example.com")
        self.assertEqual(user.role, self.User.Role.GUARDIAN)
        self.assertIsNotNone(user.guardian_profile)
        self.assertEqual(user.guardian_profile.full_name, "Guardian Profile Name")

    def test_user_serializer_create_professor(self):
        data = {
            "email": "newprofessor@example.com",
            "password": "password123",
            "name": "New Professor",
            "role": self.User.Role.PROFESSOR,
            "profile": self.professor_profile_data,
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, "newprofessor@example.com")
        self.assertEqual(user.role, self.User.Role.PROFESSOR)
        self.assertIsNotNone(user.professor_profile)
        self.assertEqual(user.professor_profile.full_name, "Professor Profile Name")

    def test_user_profile_serializer_student(self):
        serializer = UserProfileSerializer(self.student_user)
        self.assertEqual(serializer.data["email"], "student_profile@example.com")
        self.assertEqual(serializer.data["role"], self.User.Role.STUDENT)
        self.assertIsNotNone(serializer.data["profile_details"])
        self.assertEqual(
            serializer.data["profile_details"]["full_name"], "Student Profile Name"
        )

    def test_user_profile_serializer_guardian(self):
        guardian_instance = Guardian.objects.create(
            user=self.guardian_user, student=self.student_instance, **self.guardian_profile_data
        )
        serializer = UserProfileSerializer(self.guardian_user)
        self.assertEqual(serializer.data["email"], "guardian_profile@example.com")
        self.assertEqual(serializer.data["role"], self.User.Role.GUARDIAN)
        self.assertIsNotNone(serializer.data["profile_details"])
        self.assertEqual(
            serializer.data["profile_details"]["full_name"], "Guardian Profile Name"
        )

    def test_user_profile_serializer_professor(self):
        professor_instance = Professor.objects.create(
            user=self.professor_user, **self.professor_profile_data
        )
        serializer = UserProfileSerializer(self.professor_user)
        self.assertEqual(serializer.data["email"], "professor_profile@example.com")
        self.assertEqual(serializer.data["role"], self.User.Role.PROFESSOR)
        self.assertIsNotNone(serializer.data["profile_details"])
        self.assertEqual(
            serializer.data["profile_details"]["full_name"], "Professor Profile Name"
        )

    def test_user_profile_serializer_no_profile(self):
        user_no_profile = self.User.objects.create_user(
            email="no_profile@example.com",
            password="password123",
            name="No Profile User",
            role=self.User.Role.STAFF,
        )
        serializer = UserProfileSerializer(user_no_profile)
        self.assertEqual(serializer.data["email"], "no_profile@example.com")
        self.assertEqual(serializer.data["role"], self.User.Role.STAFF)
        self.assertIsNone(serializer.data["profile_details"])

    def test_user_serializer_prevents_non_staff_role_escalation(self):
        from types import SimpleNamespace

        request = SimpleNamespace(user=self.student_user)
        serializer = UserSerializer(
            instance=self.student_user,
            data={"role": self.User.Role.SUPERUSER},
            partial=True,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)
