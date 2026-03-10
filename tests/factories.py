import factory
from factory.django import DjangoModelFactory

from src.accounts.models import Company, User
from src.companies.models import Company as CRMCompany
from src.companies.models import CompanyContact
from src.pipeline.models import ClientCompany, Deal


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = "adnp"
    legal_name = factory.LazyAttribute(lambda o: f"{o.name.upper()} s.r.o.")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda o: f"{o.username}@nekosvan.cz")
    role = User.Role.MARTIN


class AdamFactory(UserFactory):
    username = factory.Sequence(lambda n: f"adam{n}" if n else "adam")
    first_name = "Adam"
    role = User.Role.ADAM


class VadimFactory(UserFactory):
    username = factory.Sequence(lambda n: f"vadim{n}" if n else "vadim")
    first_name = "Vadim"
    role = User.Role.VADIM


class MartinFactory(UserFactory):
    username = factory.Sequence(lambda n: f"martin{n}" if n else "martin")
    first_name = "Martin"
    role = User.Role.MARTIN


class NekoSvanFactory(UserFactory):
    username = factory.Sequence(lambda n: f"nekosvan{n}" if n else "nekosvan")
    first_name = "Neko"
    last_name = "Svan"
    role = User.Role.NEKOSVAN


class ClientCompanyFactory(DjangoModelFactory):
    class Meta:
        model = ClientCompany

    name = factory.Sequence(lambda n: f"Client Corp {n}")
    contact_name = factory.Faker("name")
    email = factory.LazyAttribute(lambda o: f"info@{o.name.lower().replace(' ', '')}.cz")
    ico = factory.Sequence(lambda n: f"{10000000 + n}")


class DealFactory(DjangoModelFactory):
    class Meta:
        model = Deal

    client_company = factory.Sequence(lambda n: f"Test Corp {n}")
    client_contact_name = factory.Faker("name")
    client_email = factory.LazyAttribute(lambda o: f"contact@{o.client_company.lower().replace(' ', '')}.cz")
    phase = Deal.Phase.LEAD
    status = Deal.Status.ACTIVE


class CRMCompanyFactory(DjangoModelFactory):
    """Factory for companies.Company (CRM companies, not accounts.Company)"""

    class Meta:
        model = CRMCompany

    name = factory.Sequence(lambda n: f"Test Company {n}")
    ico = factory.Sequence(lambda n: f"{10000000 + n}")
    status = "active"


class CRMCompanyContactFactory(DjangoModelFactory):
    """Factory for companies.CompanyContact"""

    class Meta:
        model = CompanyContact

    company = factory.SubFactory(CRMCompanyFactory)
    name = factory.Faker("name")
    email = factory.Faker("email")
