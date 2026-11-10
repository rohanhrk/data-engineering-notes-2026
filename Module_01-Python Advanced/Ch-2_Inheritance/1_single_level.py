class Company:
    title:str = "consultancy"

    def __init__(self, company_name:str):
        self.company_name:str = company_name
    
    def info(self):
        print(f"Company Name: {self.company_name}")
        return f"Company Name: {self.company_name}"

class Employee(Company):
    def __init__(self, employee_name:str, company_name:str):
        self.employee_name = employee_name
        self.company_name = company_name
    
    def employee_info(self):
        response = Company.info(self)
        print(f"The employee: {self.employee_name}, {response}")

obj = Employee("John Doe", "Tech Solutions")
obj.employee_info()