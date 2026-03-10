import pytest
from rest_framework.test import APIClient

from tests.factories import CRMCompanyFactory, UserFactory


@pytest.mark.django_db
class TestCompanyAPI:
    def test_list_companies(self, api_client, internal_user):
        """Test GET /api/v1/companies/companies/"""
        CRMCompanyFactory.create_batch(3)
        api_client.force_authenticate(user=internal_user)
        response = api_client.get("/api/v1/companies/companies/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_create_company(self, api_client, internal_user):
        """Test POST /api/v1/companies/companies/"""
        api_client.force_authenticate(user=internal_user)
        response = api_client.post(
            "/api/v1/companies/companies/",
            {
                "name": "Nová Firma s.r.o.",
                "ico": "12345678",
                "status": "lead",
            },
        )
        assert response.status_code == 201
        assert response.data["name"] == "Nová Firma s.r.o."

    def test_filter_by_status(self, api_client, internal_user):
        """Test filtering companies by status"""
        CRMCompanyFactory(status="lead")
        CRMCompanyFactory(status="active")
        CRMCompanyFactory(status="active")
        api_client.force_authenticate(user=internal_user)
        response = api_client.get("/api/v1/companies/companies/?status=active")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_create_deal_from_company(self, api_client, internal_user):
        """Test POST /api/v1/companies/companies/{id}/create-deal/"""
        company = CRMCompanyFactory()
        api_client.force_authenticate(user=internal_user)
        response = api_client.post(
            f"/api/v1/companies/companies/{company.id}/create-deal/",
            {"title": "Nový deal z firmy"},
        )
        assert response.status_code == 201
        assert response.data["company"] == company.id

    def test_unauthenticated_access_denied(self, api_client):
        """Test that unauthenticated requests are rejected"""
        response = api_client.get("/api/v1/companies/companies/")
        assert response.status_code == 401
