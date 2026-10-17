from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaff

from .models import Resource, ResourceLoan
from .serializers import ResourceLoanSerializer, ResourceSerializer


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all().order_by("name")
    serializer_class = ResourceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "resource_type", "status"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsStaff]
        return super().get_permissions()


class ResourceLoanViewSet(viewsets.ModelViewSet):
    queryset = (
        ResourceLoan.objects.select_related("resource", "student")
        .all()
        .order_by("-loan_date")
    )
    serializer_class = ResourceLoanSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "resource__name",
        "student__full_name",
        "student__registration_number",
        "loan_date",
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
        if getattr(user, "role", None) == "STUDENT":
            return queryset.filter(student__user=user)
        if getattr(user, "role", None) == "GUARDIAN":
            return queryset.filter(student__guardians__user=user).distinct()
        return queryset.none()
