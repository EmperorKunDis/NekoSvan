from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.accounts.permissions import IsInternalUser
from src.pipeline.serializers import DealSerializer

from . import services
from .models import Communication, Company, CompanyContact, CompanyDocument
from .serializers import (
    CommunicationSerializer,
    CompanyContactSerializer,
    CompanyCreateDealSerializer,
    CompanyCreateSerializer,
    CompanyDetailSerializer,
    CompanyDocumentSerializer,
    CompanyListSerializer,
)


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company CRUD and filtering."""

    permission_classes = [IsInternalUser]
    filterset_fields = ("status", "sector")
    search_fields = ("name", "ico", "dic", "email", "city")
    ordering_fields = ("created_at", "updated_at", "name")

    def get_queryset(self):
        status_filter = self.request.query_params.get("status")
        sector_filter = self.request.query_params.get("sector")
        search = self.request.query_params.get("search")
        return services.get_company_queryset(
            status=status_filter,
            sector=sector_filter,
            search=search,
        )

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        elif self.action == "create":
            return CompanyCreateSerializer
        return CompanyDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = services.create_company(serializer.validated_data, created_by=request.user)
        return Response(CompanyDetailSerializer(company).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        company = self.get_object()
        serializer = self.get_serializer(company, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        company = services.update_company(company, serializer.validated_data)
        return Response(CompanyDetailSerializer(company).data)

    @action(detail=True, methods=["post"])
    def create_deal(self, request, pk=None):
        """Create a deal from this company."""
        company = self.get_object()
        serializer = CompanyCreateDealSerializer(data=request.data, context={"company": company, "request": request})
        serializer.is_valid(raise_exception=True)
        deal = serializer.save()
        return Response(DealSerializer(deal).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        """Get all contacts for this company."""
        company = self.get_object()
        contacts = company.contacts.all()
        serializer = CompanyContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def communications(self, request, pk=None):
        """Get all communications for this company."""
        company = self.get_object()
        communications = company.communications.all()
        serializer = CommunicationSerializer(communications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        """Get all documents for this company."""
        company = self.get_object()
        documents = company.documents.all()
        serializer = CompanyDocumentSerializer(documents, many=True)
        return Response(serializer.data)


class CompanyContactViewSet(viewsets.ModelViewSet):
    """ViewSet for CompanyContact (nested under company)."""

    serializer_class = CompanyContactSerializer
    permission_classes = [IsInternalUser]

    def get_queryset(self):
        company_id = self.request.query_params.get("company")
        if company_id:
            return CompanyContact.objects.filter(company_id=company_id)
        return CompanyContact.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = Company.objects.get(pk=serializer.validated_data["company"].id)
        contact_data = {k: v for k, v in serializer.validated_data.items() if k != "company"}
        contact = services.create_contact(company, contact_data)
        return Response(CompanyContactSerializer(contact).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        contact = self.get_object()
        serializer = self.get_serializer(contact, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        contact = services.update_contact(contact, serializer.validated_data)
        return Response(CompanyContactSerializer(contact).data)


class CommunicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Communication (nested under company)."""

    serializer_class = CommunicationSerializer
    permission_classes = [IsInternalUser]

    def get_queryset(self):
        company_id = self.request.query_params.get("company")
        if company_id:
            return Communication.objects.filter(company_id=company_id)
        return Communication.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CompanyDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for CompanyDocument (nested under company)."""

    serializer_class = CompanyDocumentSerializer
    permission_classes = [IsInternalUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        company_id = self.request.query_params.get("company")
        if company_id:
            return CompanyDocument.objects.filter(company_id=company_id)
        return CompanyDocument.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = Company.objects.get(pk=serializer.validated_data["company"].id)
        document = services.upload_document(
            company=company,
            file=serializer.validated_data["file"],
            name=serializer.validated_data["name"],
            document_type=serializer.validated_data.get("document_type", ""),
            uploaded_by=request.user,
        )
        return Response(CompanyDocumentSerializer(document).data, status=status.HTTP_201_CREATED)
