from company.models import Company

class CompanyService:
    @staticmethod
    def create_company(data: dict) -> Company:
        return Company.objects.create(**data)

    @staticmethod
    def list_companies():
        return Company.objects.all()

    @staticmethod
    def update_company(cid: str, data: dict) -> Company:
        company = Company.objects.get(cid=cid)
        for key, value in data.items():
            setattr(company, key, value)
        company.save()
        return company

    @staticmethod
    def get_company(cid: str) -> Company:
        return Company.objects.get(cid=cid)
