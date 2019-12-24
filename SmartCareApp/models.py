from django.db import models

# Create your models here.



class CallCentre(models.Model):
    Service_Order = models.CharField(max_length=10)
    Location = models.CharField(max_length=10)
    First_Name = models.CharField(max_length=30)
    Last_Name = models.CharField(max_length=30)
    Product = models.CharField(max_length=10)
    Fault = models.CharField(max_length=10)
    Address = models.CharField(max_length=100,default='')
    City = models.CharField(max_length=50,default='')
    Mobile_No = models.CharField(max_length=10)
    Pin_Code = models.CharField(max_length=10)
    Status = models.CharField(max_length=10)
    Reported_Date = models.CharField(max_length=10)
    Reported_Time = models.CharField(max_length=10)

    def __str__(self):
        return self.Service_Order

class Planning(models.Model):
    Service_Order = models.CharField(max_length=10)
    Appointment_Date = models.CharField(max_length=30)
    Appointment_Time = models.CharField(max_length=30)
    Technician = models.CharField(max_length=10)
    Technician_Name = models.CharField(max_length=50)
    Execution_Date= models.CharField(max_length=10)
    Execution_Time = models.CharField(max_length=100,default='')
    End_Time = models.CharField(max_length=50,default='')
    
    def __str__(self):
        return self.Service_Order

class Location_Details(models.Model):
    Location = models.CharField(max_length=30)
    Product = models.CharField(max_length=30)
    Cust_Type = models.CharField(max_length=30,default="")
    Product_Code = models.CharField(max_length=10)
    Serial_No = models.CharField(max_length=50)
    Bill_No = models.CharField(max_length=20)
    DOP= models.CharField(max_length=10)
    Expiry = models.CharField(max_length=100,default='')
    Contract_No = models.CharField(max_length=100,default='-')
    Effective_Date = models.CharField(max_length=100,default='-')
    Effective_Expiry = models.CharField(max_length=100,default='-')

    def __str__(self):
        return self.Location

class Details(models.Model):
    Service_Order = models.CharField(max_length=10,default='-')
    Location = models.CharField(max_length=30)
    Product = models.CharField(max_length=30)
    Cust_Type = models.CharField(max_length=30,default="")
    Product_Code = models.CharField(max_length=10)
    Serial_No = models.CharField(max_length=50)
    Bill_No = models.CharField(max_length=20)
    DOP= models.CharField(max_length=10)
    Expiry = models.CharField(max_length=100,default='')
    Contract_No = models.CharField(max_length=100,default='-')
    Effective_Date = models.CharField(max_length=100,default='-')
    Effective_Expiry = models.CharField(max_length=100,default='-')

    def __str__(self):
        return self.Service_Order

class Technician(models.Model):
    Name = models.CharField(max_length=50)
    Code = models.CharField(max_length=30)
    Mobile = models.CharField(max_length=30)
    
    def __str__(self):
        return self.Name

class Contract(models.Model):
    Location = models.CharField(max_length=30)
    Contract_No = models.CharField(max_length=30)
    Product_Code = models.CharField(max_length=10)
    Serial_No = models.CharField(max_length=50)
    Start_Date = models.CharField (max_length=100)
    End_Date = models.CharField(max_length=100)
    Amount = models.CharField(max_length=30)

    def __str__(self):
        return self.Contract_No

class Amount(models.Model):
    Product = models.CharField(max_length=50)
    Year = models.CharField(max_length=30)
    Amount = models.CharField(max_length=30)
    
    def __str__(self):
        return self.Amount

class VisitDetail(models.Model):
    Service_Order = models.CharField(max_length=10)
    Location = models.CharField(max_length=10)
    Technician = models.CharField(max_length=30)
    Technician_Name = models.CharField(max_length=50)
    Product_Code = models.CharField(max_length=10)
    Serial_No = models.CharField(max_length=10)
    Warranty = models.CharField(max_length=30,default='')
    Contract_No = models.CharField(max_length=50,default='')
    Visit_Date = models.CharField(max_length=10)
    Start_Time = models.CharField(max_length=10)
    End_Time = models.CharField(max_length=10)
    Work_Done = models.CharField(max_length=50)
    Action = models.CharField(max_length=10)
    Remark = models.CharField(max_length=100)
    UDate = models.CharField(max_length=100,default='')
    UTime = models.CharField(max_length=100,default='')

    def __str__(self):
        return self.Service_Order

class Royalty(models.Model):
    Service_Order = models.CharField(max_length=10)
    Location = models.CharField(max_length=10)
    Technician = models.CharField(max_length=30)
    Technician_Name = models.CharField(max_length=50,default='')
    Service_Charge = models.CharField(max_length=50)
    Category1 = models.CharField(max_length=10,default='')
    Category2 = models.CharField(max_length=10,default='')
    Category3 = models.CharField(max_length=10,default='')
    Part_Name1 = models.CharField(max_length=10,default='')
    Part_Name2 = models.CharField(max_length=10,default='')
    Part_Name3 = models.CharField(max_length=10,default='')
    Part_Amount1 = models.CharField(max_length=10,default='')
    Part_Amount2 = models.CharField(max_length=10,default='')
    Part_Amount3 = models.CharField(max_length=10,default='')
    Total = models.CharField(max_length=50,default='')
    RDate = models.CharField(max_length=50,default='')
    RTime = models.CharField(max_length=50,default='')
    
    def __str__(self):
        return self.Service_Order

class Rating(models.Model):
    Service_Order = models.CharField(max_length=10)
    Name = models.CharField(max_length=100)
    Technician = models.CharField(max_length=30)
    Technician_Name = models.CharField(max_length=50)
    Product = models.CharField(max_length=10)
    Work_Done = models.CharField(max_length=10)
    Behaviour = models.CharField(max_length=10,default='')
    Service = models.CharField(max_length=50,default='')
    
    def __str__(self):
        return self.Service_Order