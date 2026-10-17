from django.contrib.auth import get_user_model
from rest_framework import serializers
from school.serializers import ProfessorSerializer
from students.serializers import GuardianSerializer, StudentSerializer


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "name", "password", "role", "profile"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_role(self, value):
        request = self.context.get("request")
        if self.instance and request and hasattr(request, "user"):
            user = request.user
            if not (user.is_staff or user.is_superuser) and value != self.instance.role:
                raise serializers.ValidationError(
                    "Apenas administradores podem alterar o cargo do usuário."
                )
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)
        user = get_user_model().objects.create_user(**validated_data)

        if profile_data is not None:
            if user.role == get_user_model().Role.STUDENT:
                profile_serializer = StudentSerializer(data=profile_data)
            elif user.role == get_user_model().Role.GUARDIAN:
                profile_serializer = GuardianSerializer(data=profile_data)
            elif user.role == get_user_model().Role.PROFESSOR:
                profile_serializer = ProfessorSerializer(data=profile_data)
            else:
                profile_serializer = None

            if profile_serializer:
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save(user=user)

        return user

    def update(self, instance, validated_data):
        validated_data.pop("profile", None)
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    profile_details = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "name",
            "role",
            "is_staff",
            "is_superuser",
            "profile_details",
        ]

    def get_profile_details(self, obj):
        profile = obj.profile
        if profile:
            if obj.role == get_user_model().Role.STUDENT:
                from students.serializers import StudentSerializer

                return StudentSerializer(profile, context=self.context).data
            elif obj.role == get_user_model().Role.GUARDIAN:
                from students.serializers import GuardianSerializer

                return GuardianSerializer(profile, context=self.context).data
            elif obj.role == get_user_model().Role.PROFESSOR:
                from school.serializers import ProfessorSerializer

                return ProfessorSerializer(profile, context=self.context).data
        return None
