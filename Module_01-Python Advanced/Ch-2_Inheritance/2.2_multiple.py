class Company:
    title:str = "consultancy"

    def __init__(self, company_name:str):
        self.company_name:str = company_name
    
    def info(self):
        print(f"Company Name: {self.company_name}")
        return f"Company Name: {self.company_name}"

class ClientCompany:
    title:str = "client company"

    def __init__(self, client_company_name:str):
        self.client_company_name:str = client_company_name
    
    def info(self):
        print(f"Client Company Name: {self.client_company_name}")
        return f"Client Company Name: {self.client_company_name}"

class Employee(Company, ClientCompany):
    def __init__(self, employee_name: str, company_name: str, client_company_name: str):
        self.employee_name = employee_name
        self.company_name = company_name
        self.client_company_name = client_company_name
    
    def info(self):
        response1 = Company.info(self)
        response2 = ClientCompany.info(self)
        print(f"The employee: {self.employee_name}, {response1}, {response2}")
        return f"The employee: {self.employee_name}, {response1}, {response2}"
    
obj = Employee("John Doe", "Tech Solutions", "Client Corp")
obj.info()