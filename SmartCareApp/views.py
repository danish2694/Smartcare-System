from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from SmartCareApp.models import CallCentre,Planning,Location_Details,Details,Technician,Contract,Amount,VisitDetail,Royalty,Rating,LoginDetail
from django.contrib.sessions.models import Session
import random
from datetime import date
import datetime
from datetime import datetime,timedelta			#First Screen
import time
import arrow
import pandas as pd
from functools import reduce
from tika import parser



# Create your views here.

def smartcare(request):
    return render(request,'login.html')

def login(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 0:
            return HttpResponseRedirect('/callcentre')
        elif request.session['is_logged'] == 1:
            return HttpResponseRedirect('/servicecentre')
    else:
        return render(request,'login.html')

def logging(request):
    if request.method=="POST":
        uname=request.POST.get('username')
        upass=request.POST.get('password')

    login_validate = LoginDetail.objects.filter(Username=uname,Password=upass)
    if login_validate:
        for account in login_validate:
            account_type = account.Account_Type
        request.session['is_logged'] = account_type
        if account_type == 0:
            return HttpResponseRedirect('/callcentre')
        elif account_type == 1:
            return HttpResponseRedirect('/servicecentre')
        else:
            return render(request,'login.html')
    else:
        error_msg = True
        return render(request,'login.html',{'error':error_msg})

def logout(request):
    if request.session.has_key('is_logged'):
        del request.session['is_logged']
        return HttpResponseRedirect('/login')
    return HttpResponseRedirect('/login')

def callcentre(request):
    if request.session.has_key('is_logged'):
        return render(request,'callcentre.html')
    else:
        return HttpResponseRedirect('/login')

def callregister(request):
    if request.session.has_key('is_logged'):
        return render(request,'callregister.html')
    else:
        return HttpResponseRedirect('/login')

def contract(request):
    return render(request,'contract.html')

def contractform(request):
    if request.method=="POST":
        locv=request.POST.get('locinput')
    obj0=CallCentre.objects.filter(Location=locv)
    pr=''
    if obj0:
        for e0 in obj0:
            pr=e0.Product
        obj=Amount.objects.filter(Product=pr)
        ep=ey=ea=''
        for e in obj:
            ep+=e.Product
            ey+=e.Year
            ea+=e.Amount
        params={'alldata':obj,'val':locv}
        return render(request,'contractform.html',params)
    else:
        params = {'msg':'Enter Valid Location'}
        return render(request,'contract.html',params)

def contractsave(request):
    if request.method=="POST":
        lno=request.POST.get('locno')
        cno=request.POST.get('conno')
        pc=request.POST.get('pcode')
        sn=request.POST.get('serno')
        amt=request.POST.get('amount')
    pr=lno[:2]           #product
    price=(amt[:4])      #amount
    time=(amt[7:8])      #year
#for amount and year
    obj0=Amount.objects.filter(Product=pr)
    ep=ey=ea=''
    for e0 in obj0:
        ep+=e0.Product
        ey+=e0.Year
        ea+=e0.Amount

    obj=Details.objects.filter(Location=lno,Product_Code=pc,Serial_No=sn)
    if obj:
        start_date=end_date=''
        for e in obj:
            end_date+=e.Expiry
        date1 = datetime.strptime(end_date, "%d/%m/%Y")  
        new_date1 = date1 +timedelta(days=1)
        new_sdate = datetime.strftime(new_date1, "%d/%m/%Y")

        if time=='1':
            new_date2 = new_date1 + timedelta(days=365)
        elif time=='2':
            new_date2 = new_date1 + timedelta(days=730)
        elif time=='3':
            new_date2 = new_date1 + timedelta(days=1095)
        elif time=='4':
            new_date2 = new_date1 + timedelta(days=1460)
        else:
            new_date2 = new_date1 + timedelta(days=1825)
    
        new_edate = datetime.strftime(new_date2, "%d/%m/%Y")

        for r in range(1):
            no = random.randint(111111,999999)
        cno = 'CN00' + str(no)

        params = {'val':lno,'contract':cno,'pcode':pc,'serial':sn,'stdt':new_sdate,'edt':new_edate,'price':amt}
        cn = Contract(Location=lno,Contract_No=cno,Product_Code=pc,Serial_No=sn,Start_Date=new_sdate,End_Date=new_edate,Amount=price)
        cn.save()
    else:
        params = {'val':lno,'error':'Enter Valid Serial Number','alldata':obj0}
    return render (request,'contractform.html',params)

def contractbook(request):
    return render(request,'contractbook.html')

def contractbooksave(request):
    if request.method=="POST":
        loc_no=request.POST.get('loc')
        cont=request.POST.get('contract')
    obj=Contract.objects.filter(Contract_No=cont,Location=loc_no)
    ln=cn=sn=st=ed=''
    if obj:
        for e in obj:
            ln+=e.Location
            cn+=e.Contract_No
            sn+=e.Serial_No
            st+=e.Start_Date
            ed+=e.End_Date
        obj1=Details.objects.filter(Serial_No=sn).update(Contract_No=cn,Effective_Date=st,Effective_Expiry=ed)
        params = {'lcn':ln,'cont':cn,'msg':'Contract Booked Successfully'}
        return render(request,'contractbook.html',params)
    else:
        params = {'lcn':ln,'cont':cn,'msg':'Enter Correct Loaction and Contract Number'}
        return render(request,'contractbook.html',params)

def custdetail(request):
    return render(request,'custdetail.html')
    
def detailsupdate(request):
    mb=''
    if request.method=="POST":
        mb=request.POST.get('loc')
    obj=CallCentre.objects.filter(Location=mb)
    lcn=fn=ln=ad=ct=ph=pc=''
    if obj:
        for e in obj:
            lcn=e.Location
            fn=e.First_Name
            ln=e.Last_Name
            ad=e.Address
            ct=e.City
            ph=e.Mobile_No
            pc=e.Pin_Code
        params = {'locn':lcn,'fname':fn,'lname':ln,'add':ad,'city':ct,'phone':ph,'code':pc}
        return render(request,'detailsupdate.html',params)
    else:
        params = {'msg':'Enter Valid Location'}
        return render(request,'custdetail.html',params)

def custdetailsave(request):
    if request.method=="POST":
        lcn=request.POST.get('loc')
        fn=request.POST.get('name1')
        ln=request.POST.get('name2')
        add=request.POST.get('address')
        ct=request.POST.get('cty')
        ph=request.POST.get('phno')
        pc=request.POST.get('pcode')
    params = {'locn':lcn,'fname':fn,'lname':ln,'add':add,'city':ct,'phone':ph,'code':pc}
    obj=CallCentre.objects.filter(Location=lcn).update(First_Name=fn,Last_Name=ln,Address=add,City=ct,Mobile_No=ph,Pin_Code=pc)
    return render(request,'detailsupdate.html',params)


def servicecentre(request):
    if request.session.has_key('is_logged'):
        return render(request,'servicecentre.html')
    else:
        return HttpResponseRedirect('/login')

def callsave(request):
    sno=lno=fnm=lnm=prdt=flt=add=cty=phno=pincode=er=fr=''
    params={}
    lt=[]
    if request.method=="POST":
       # sno=request.POST.get('sorder')
       # lno=request.POST.get('loc')
        fnm=request.POST.get('fname').capitalize()
        lnm=request.POST.get('lname').capitalize()
        prdt=request.POST.get('prod').upper()
        flt=request.POST.get('fault').title()
        add=request.POST.get('address').title()
        cty=request.POST.get('city').capitalize()
        phno=request.POST.get('mobile')
        pincode=request.POST.get('pin')
        sts='Free'
        dt=d=arrow.now().format('DD/MM/YYYY')
        t=time.strftime("%H%M")
        print(prdt)   
        if prdt=="--SELECT--" or fnm=='' or lnm=='' or flt=='' or add=='' or cty=='' or phno=='' or pincode=='':
            er='Please Fill All The Fields'
            params={'a':sno,'b':lno,'c':fnm,'d':lnm,'e':prdt,'f':flt,'g':add,'h':cty,'i':phno,'j':pincode,'error':er}
        else:
            er='Saved Successfully'
            if prdt=='AC':
                fr="AC00"
            elif prdt=='RF':
                fr='RF00'
            elif prdt=='WM':
                fr="WM00"
            else:
                fr="MW00"
            for j in range(1):
                ls=random.randint(1111,9999)        
                lno=str(fr+str(ls))
            for i in range(1):
                no=random.randint(333333,399999)
                sno=str(no)
            params={'a':sno,'b':lno,'c':fnm,'d':lnm,'e':prdt,'f':flt,'g':add,'h':cty,'i':phno,'j':pincode,'error':er}
            datasave = CallCentre(Service_Order=sno,Location=lno,First_Name=fnm,Last_Name=lnm,Product=prdt,Fault=flt,Address=add,City=cty,Mobile_No=phno,Pin_Code=pincode,Status=sts,Reported_Date=dt,Reported_Time=t)
            datasave.save()
            detailsave = Details(Service_Order=sno,Location='-',Product='-',Cust_Type='-',Product_Code='-',Serial_No='-',Bill_No='-',DOP='-',Expiry='-',Contract_No='-',Effective_Date='-',Effective_Expiry='-')
            detailsave.save()
    return render(request,'callregister.html',params) 

def search(request):
    return render(request,'search.html')

def searchorder(request):
    if request.method=="POST":
        so=request.POST.get('sorder')
    obj=CallCentre.objects.filter(Service_Order=so)
    if obj:
        es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
        for e in obj:
            es+=e.Service_Order
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            epr+=e.Product
            ef+=e.Fault
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
            ests+=e.Status
            edt+=e.Reported_Date
            etm+=e.Reported_Time
    
        context={'alldata':obj,'order':so}
        return render(request,'orderresult.html',context)
    else:
        context={'msg':'Enter Valid Service Order'}
        return render(request,'search.html',context)

def searchloc(request):
    if request.method=="POST":
        sm=request.POST.get('sloc')
    obj=CallCentre.objects.filter(Location=sm)
    if obj:
        el=efn=eln=eadd=ecty=emb=epn=''
        for e in obj:
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
        context={'alldata':obj,'location':sm}
        return render(request,'locationresult.html',context)
    else:
        context={'msg':'Enter Valid Location'}
        return render(request,'search.html',context)

def searchmob(request):
    if request.method=="POST":
        sm=request.POST.get('smob')
    obj=CallCentre.objects.filter(Mobile_No=sm)
    if obj:
        el=efn=eln=epr=eadd=ecty=emb=epn=''
        for e in obj:
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            epr+=e.Product
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
        context={'alldata':obj,'mobile':sm}
        return render(request,'mobileresult.html',context)
    else:
        context={'msg':'Enter Valid Mobile Number'}
        return render(request,'search.html',context)

def searchname(request):
    if request.method=="POST":
        sn=request.POST.get('sname')
    obj=CallCentre.objects.filter(First_Name=sn)
    if obj:
        el=efn=eln=epr=eadd=ecty=emb=epn=''
        for e in obj:
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            epr+=e.Product
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
        context={'alldata':obj}
        return render(request,'nameresult.html',context)
    else:
        context={'msg':'Enter Valid Name'}
        return render(request,'search.html',context)

def contractresult(request):
    if request.method=="POST":
        sc=request.POST.get('scontract')
    obj=Contract.objects.filter(Contract_No=sc)
    if obj:
        el=cn=epc=esn=est=eed=''
        for e in obj:
            el+=e.Location
            cn+=e.Contract_No
            epc+=e.Product_Code
            esn+=e.Serial_No
            est+=e.Start_Date
            eed+=e.End_Date
        context={'alldata':obj,'contract':sc}
        return render(request,'contractresult.html',context)
    else:
        context={'msg':'Enter Valid Contract Number'}
        return render(request,'search.html',context)

def ordershow(request,lno):
    obj=CallCentre.objects.filter(Location=lno)
    #context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
        epn+=e.Pin_Code
        ests+=e.Status
        edt+=e.Reported_Date
        etm+=e.Reported_Time
    context={'alldata':obj}
    return render(request,'orderresult.html',context)

def newcalls(request):
    t = datetime.now()
    w = t - timedelta(minutes=30)
    time_sub=str(w.strftime("%H%M"))
    date=str(t.strftime("%d/%m/%Y"))
    time=str(t.strftime("%H%M"))
    obj=CallCentre.objects.filter(Status='Free',Reported_Date=date,Reported_Time__range=(time_sub,time))
    context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
        epn+=e.Pin_Code
        ests+=e.Status
        edt+=e.Reported_Date
        etm+=e.Reported_Time
    context={'alldata':obj}
    return render(request,'newcalls.html',context)
     #lname = 'Doe'
  #  obj=CallCentre.objects.raw("SELECT * FROM SmartCareApp_CallCentre WHERE Reported_Date='%s' and Reported_Time BETWEEN '%s' AND '%s'", [date],[time_sub],[time])
  #  obj=CallCentre.objects.filter(Status='Free')

def freecalls(request):
    obj=CallCentre.objects.filter(Status='Free')
    context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
        epn+=e.Pin_Code
        ests+=e.Status
        edt+=e.Reported_Date
        etm+=e.Reported_Time
    context={'alldata':obj}
    return render(request,'freecalls.html',context)

def callplan(request):
    if request.method=="POST":
        ono=request.POST.get('ordradio')
        print(ono)
    if ono==None:
        obj=CallCentre.objects.filter(Status='Free')
        context={'alldata':obj}
        es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
        for e in obj:
            es+=e.Service_Order
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            epr+=e.Product
            ef+=e.Fault
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
            ests+=e.Status
            edt+=e.Reported_Date
            etm+=e.Reported_Time
            context = {'msg':'Choose A Service Order','alldata':obj}
            return render(request,'freecalls.html',context)
    else:
        obj=Technician.objects.all()
        context={'alldata':obj}
        en=ec=emb=''
        for e in obj:
            en+=e.Name
            ec+=e.Code
            emb+=e.Mobile
        ad=arrow.now().format('DD/MM/YYYY')
        t=time.strftime("%H%M")
        context={'alldata':obj,'sod':ono,'apdt':ad}
        return render(request,'callplan.html',context)    

def callplanning(request):
    if request.method=="POST":
        ordno=request.POST.get('sorder')
        ad=request.POST.get('apdt')
        at=request.POST.get('aptm')
        t=request.POST.get('tech')
        tc=t[:6]
        tn=t[9:]
        ed=request.POST.get('exdt')
        st=request.POST.get('extm')
        et=request.POST.get('entm')
    dt=arrow.now().format('DD/MM/YYYY')
    tm=time.strftime("%H%M")
    obj=Technician.objects.all()
    en=ec=emb=''
    for e in obj:
        en+=e.Name
        ec+=e.Code
        emb+=e.Mobile
    
    apdate = datetime.strptime(dt, "%d/%m/%Y")     #appointment date
    exdate = datetime.strptime(ed, "%d/%m/%Y")     #execution date

    if at<tm:
        context={'alldata':obj,'msg':'Appointment Time Should Be Greater Than Or Equal To Current Time','sod':ordno,'apdt':ad,'aptm':at,'tech':t,'exdt':ed,'extm':st,'entm':et}
        return render(request,'callplan.html',context)
    elif exdate<apdate:
        context={'alldata':obj,'msg':'Execution Date Should Be Greater Than Or Equal To Current Date','sod':ordno,'apdt':ad,'aptm':at,'tech':t,'exdt':ed,'extm':st,'entm':et}
        return render(request,'callplan.html',context)
    elif (exdate==apdate and st<tm) or (exdate==apdate and et<tm):
        context={'alldata':obj,'msg':'Start Time/End Time Should Be Greater Than Current Time','sod':ordno,'apdt':ad,'aptm':at,'tech':t,'exdt':ed,'extm':st,'entm':et}
        return render(request,'callplan.html',context)
    elif et<st:
        context={'alldata':obj,'msg':'Start Time Should Be Greater Than End Time','sod':ordno,'apdt':ad,'aptm':at,'tech':t,'exdt':ed,'extm':st,'entm':et}
        return render(request,'callplan.html',context)
    else:
        callplan = Planning(Service_Order=ordno,Appointment_Date=ad,Appointment_Time=at,Technician=tc,Technician_Name=tn,Execution_Date=ed,Execution_Time=st,End_Time=et)
        callplan.save()
        obj=CallCentre.objects.filter(Service_Order=ordno).update(Status='Blank')
        return HttpResponseRedirect('/freecalls/')

def blankcalls(request):
    obj=CallCentre.objects.filter(Status='Blank')
    context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
        epn+=e.Pin_Code
        ests+=e.Status
        edt+=e.Reported_Date
        etm+=e.Reported_Time
    context={'alldata':obj}
    return render(request,'blankcalls.html',context)

def viewplan(request):
    if request.method=="POST":
        bod=request.POST.get('blankord')
    print(bod)
    if bod==None:
        obj=CallCentre.objects.filter(Status='Blank')
        context={'alldata':obj}
        es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
        for e in obj:
            es+=e.Service_Order
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            epr+=e.Product
            ef+=e.Fault
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
            ests+=e.Status
            edt+=e.Reported_Date
            etm+=e.Reported_Time
        context = {'msg':'Choose A Service Order','alldata':obj}
        return render(request,'blankcalls.html',context)
    else:
        obj=Planning.objects.filter(Service_Order=bod)
        es=ead=eat=et=etn=eed=est=eet=''
        for e in obj:
            es=e.Service_Order
            ead=e.Appointment_Date
            eat=e.Appointment_Time
            et+=e.Technician
            etn+=e.Technician_Name
            eed+=e.Execution_Date
            est+=e.Execution_Time
            eet+=e.End_Time
        context={'alldata':obj}
        return render(request,'viewplan.html',context)

def pendingcalls(request):
    obj=CallCentre.objects.filter(Status='Pending')
    context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
        epn+=e.Pin_Code
        ests+=e.Status
        edt+=e.Reported_Date
        etm+=e.Reported_Time
    context={'alldata':obj}
    return render(request,'pendingcalls.html',context)

def viewvisit(request):
    if request.method=="POST":
        pdod=request.POST.get('pendingord')
    print(pdod)
    if pdod==None:
        obj=CallCentre.objects.filter(Status='Pending')
        es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
        for e in obj:
            es+=e.Service_Order
            el+=e.Location
            efn+=e.First_Name
            eln+=e.Last_Name
            epr+=e.Product
            ef+=e.Fault
            eadd+=e.Address
            ecty+=e.City
            emb+=e.Mobile_No
            epn+=e.Pin_Code
            ests+=e.Status
            edt+=e.Reported_Date
            etm+=e.Reported_Time
        context = {'msg':'Choose A Service Order','alldata':obj}
        return render(request,'pendingcalls.html',context)
    else:
        obj=VisitDetail.objects.filter(Service_Order=pdod)
        es=ead=eat=et=etn=eed=est=eet=vd=st=et=wd=ac=rm=''
        for e in obj:
            es=e.Service_Order
            ead=e.Location
            eat=e.Technician
            et+=e.Technician_Name
            etn+=e.Product_Code
            eed+=e.Serial_No
            est+=e.Warranty
            eet+=e.Contract_No
            vd+=e.Visit_Date
            st+=e.Start_Time
            et+=e.End_Time
            wd+=e.Work_Done
            ac+=e.Action
            rm+=e.Remark

        context={'alldata':obj}
        return render(request,'displayvisit.html',context)


def callupdate(request):
    return render(request,'callupdate.html')

def callupdation(request):
    if request.method=='POST':
        a=request.POST.get('sod')
    obj=CallCentre.objects.filter(Service_Order=a)
    if obj:
        odno=el=efn=eln=epr=ef=emb=ests=edt=etm=''
        for e in obj:
            odno+=e.Service_Order
            efn+=e.First_Name
            eln+=e.Last_Name
            ests+=e.Status
            el+=e.Location
            epr+=e.Product
            edt+=e.Reported_Date
            ef+=e.Fault
            etm+=e.Reported_Time
            emb+=e.Mobile_No
        obj1=Details.objects.filter(Service_Order=a)
        context1={'alldata1':obj1}
        epc=esn=''
        for e1 in obj1:
            epc+=e1.Product_Code
            esn+=e1.Serial_No
        params={'order':odno,'detail':epc+'-'+esn,'name':efn+' '+eln,'status':ests,'location':el,'product':epr,'repdate':edt,'fault':ef,'reptime':etm,'mobile':emb}
        return render(request,'callupdation.html',params)
    else:
        params={'error':'Please Enter Valid Service Order'}
        return render (request,'callupdate.html',params)

def calldetailsave(request,sno):
    obj0=Location_Details.objects.filter(Serial_No=sno)
    lno=pr=''
    for e0 in obj0:
        lno=e0.Location
        pr=e0.Product_Code

    obj1=CallCentre.objects.filter(Location=lno)
    so=''
    for e1 in obj1:
        so=e1.Service_Order

    obj=CallCentre.objects.filter(Service_Order=so)
    odno=el=efn=eln=epr=ef=emb=ests=edt=etm=''
    for e in obj:
        odno+=e.Service_Order
        efn+=e.First_Name
        eln+=e.Last_Name
        ests+=e.Status
        el+=e.Location
        epr+=e.Product
        edt+=e.Reported_Date
        ef+=e.Fault
        etm+=e.Reported_Time
        emb+=e.Mobile_No
    params={'order':odno,'detail':pr+'-'+sno,'name':efn+' '+eln,'status':ests,'location':el,'product':epr,'repdate':edt,'fault':ef,'reptime':etm,'mobile':emb}
    return render(request,'callupdation.html',params)


def callupdateshow(request):
    obj=''
    if request.method=='POST':
        a=request.POST.get('sod')
    obj=CallCentre.objects.filter(Service_Order=a)
    context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
    params={'visit':'Display Call Visits','detail':'Display Appliance Detail','maintain':'Maintain Call Detail','so':es}
    return render(request,'callupdate.html',params)

def orderdetailshow(request,so):
    obj=CallCentre.objects.filter(Service_Order=so)
    context={'alldata':obj}
    es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
        efn+=e.First_Name
        eln+=e.Last_Name
        epr+=e.Product
        ef+=e.Fault
        eadd+=e.Address
        ecty+=e.City
        emb+=e.Mobile_No
        epn+=e.Pin_Code
        ests+=e.Status
        edt+=e.Reported_Date
        etm+=e.Reported_Time
    
    context={'alldata':obj}
    return render(request,'orderresult.html',context)

def appdetailsadd(request,lno):
    obj=CallCentre.objects.filter(Location=lno)
    context={'alldata':obj}
    el=es=''
    for e in obj:
        es+=e.Service_Order
        el+=e.Location
    params={'loc':el}
    return render(request,'appdetailsadd.html',params)

def appdetailsave(request):
    if request.method=="POST":
        lno = request.POST.get('locno')
        cst = request.POST.get('cust')
        prd = request.POST.get('prdct').upper()
        sno = request.POST.get('serno').upper()
        bno = request.POST.get('billno').upper()
        dp = request.POST.get('dop')
    obj=CallCentre.objects.filter(Location=lno)
    context={'alldata':obj}
    es=ep=''
    for e in obj:
        es=e.Service_Order
        ep=e.Product
    if ep=='WM':
        date1 = datetime.strptime(dp, "%d/%m/%Y")  
        new_date = date1 +timedelta(days=1095)  # 3 years add
        new_date = datetime.strftime(new_date, "%d/%m/%Y") 
        print(new_date)
    elif ep=='RF':
        date1 = datetime.strptime(dp, "%d/%m/%Y")  
        new_date = date1 +timedelta(days=730)  # 2 years add
        new_date = datetime.strftime(new_date, "%d/%m/%Y") 
        print(new_date)
    else:
        date1 = datetime.strptime(dp, "%d/%m/%Y")  
        new_date = date1 +timedelta(days=365)  # 1 year add
        new_date = datetime.strftime(new_date, "%d/%m/%Y") 
        print(new_date)
    det = Location_Details(Location=lno,Product=ep,Cust_Type=cst,Product_Code=prd,Serial_No=sno,Bill_No=bno,DOP=dp,Expiry=new_date)
    det.save()
    params={'loc':lno,'code':prd,'sn':sno,'bill':bno,'dpp':dp,'msg':'Saved Successfully'}

    return render(request,'appdetailsadd.html',params)

def orderdetailsave(request):
    if request.method=="POST":
        od=request.POST.get('ordno')
        lno = request.POST.get('locno')
        detail = request.POST.get('det')
        nm = request.POST.get('name')
        st = request.POST.get('sts')
        rpdt = request.POST.get('rdate')
        flt = request.POST.get('ft')
        rptm = request.POST.get('rtime')
        mb = request.POST.get('mob')
    ser=detail[-10:]
    obj=Location_Details.objects.filter(Serial_No=ser)
    for e in obj:
        pr=e.Product
        pc=e.Product_Code
        cst=e.Cust_Type
        bl=e.Bill_No
        dp=e.DOP
        ex=e.Expiry
        cn=e.Contract_No
        efdt=e.Effective_Date
        efex=e.Effective_Expiry
    detsv = Details.objects.filter(Service_Order=od).update(Service_Order=od,Location=lno,Product=pr,Cust_Type=cst,Product_Code=pc,Serial_No=ser,Bill_No=bl,DOP=dp,Expiry=ex,Contract_No=cn,Effective_Date=efdt,Effective_Expiry=efex)
    params={'order':od,'detail':detail,'name':nm,'status':st,'location':lno,'product':pr,'repdate':rpdt,'fault':flt,'reptime':rptm,'mobile':mb,'msg':'Saved Successfully'}
    return render(request,'callupdation.html',params)
    
def appdetailshow(request,loc):
    obj=Location_Details.objects.filter(Location=loc)
    if obj:
        sod=es=el=et=epr=epc=esno=edp=exp=ecn=efd=eexp=''
        for e in obj:
            el=e.Location
            et=e.Cust_Type
            epr+=e.Product
            epc+=e.Product_Code
            esno+=e.Serial_No
            edp+=e.DOP
            exp+=e.Expiry
            ecn+=e.Contract_No
            efd+=e.Effective_Date
            eexp+=e.Effective_Expiry
        obj1=CallCentre.objects.filter(Location=loc)
        for e1 in obj1:
            sod=e1.Service_Order
        context={'alldata':obj,'sod':sod,'location':loc}
        return render(request,'appdetailshow.html',context)
    else:
        context={'msg':'No Details Found'}
        return render(request,'errorpage.html',context)

def callallot(request):
    if request.method=="POST":
        bod=request.POST.get('blankord')
        print(bod)
    return render(request,'callallot.html')

def viewplanning(request,sod):
    obj=Planning.objects.filter(Service_Order=sod)
    if obj:
        es=ead=eat=et=etn=eed=est=eet=''
        for e in obj:
            es=e.Service_Order
            ead=e.Appointment_Date
            eat=e.Appointment_Time
            et+=e.Technician
            etn+=e.Technician_Name
            eed+=e.Execution_Date
            est+=e.Execution_Time
            eet+=e.End_Time
        context={'alldata':obj}
        return render(request,'viewplanning.html',context)
    else:
        context={'msg':'No Plannings Found'}
        return render(request,'errorpage.html',context)

def visit(request,so):
    obj0 = CallCentre.objects.filter(Service_Order=so)
    for i in obj0:
        sts=i.Status
    if sts=='Free':
        params = {'msg':'Status is Free, Cannot Be Processed','order':so}
        return render (request,'callupdate.html',params)
    elif sts=='Audit':
        params = {'msg':'Call is Already in Call Centre Audit','order':so}
        return render(request,'callupdate.html',params)
    elif sts=='Closed':
        params = {'msg':'Call Is Already Closed','order':so}
        return render(request,'callupdate.html',params)
    else:
        obj=Details.objects.filter(Service_Order=so)
        if obj:
            ln=ct=pr=pc=sn=ws=we=cn=tn=tname=exdt=rp=ewe=''
            for e in obj:
                ln=e.Location
                ct=e.Cust_Type
                pr=e.Product
                pc=e.Product_Code
                sn=e.Serial_No
                ws=e.DOP
                we=e.Expiry
                cn=e.Contract_No
                ewe=e.Effective_Expiry
            obj1=Planning.objects.filter(Service_Order=so)
            for e1 in obj1:
                tn=e1.Technician
                tname=e1.Technician_Name
                exdt=e1.Execution_Date
            obj2=CallCentre.objects.filter(Service_Order=so)
            for e2 in obj2:
                rp=e2.Reported_Date
            if ct=='Dealer':
                wr='Dealer'
            else:
                if cn=='-':
                    rdate = datetime.strptime(rp, "%d/%m/%Y")     #reported date
                    edate = datetime.strptime(we, "%d/%m/%Y")  #expiry date
                    if edate>rdate:
                        wr='In Warranty'
                        #print('Warranty')
                    else:
                        wr='In Chargeable'
                        #print('ow')
                else:
                    rdate = datetime.strptime(rp, "%d/%m/%Y")     #reported date
                    edate = datetime.strptime(we, "%d/%m/%Y")  #expiry date
                    effdate = datetime.strptime(ewe, "%d/%m/%Y")  #effective expiry date
                    if edate>rdate:
                        wr='In Warranty'
                        #print('Warranty')
                    elif rdate>edate and rdate<effdate:
                        wr='In Protection'
                        #protection
                    elif rdate>effdate:
                        wr='In Chargeable'
                        #chargeable

            if pr=='AC':
                w = ['Accessories','Cabinet','Cooling Coil','Compressor','Control Card','Electrical Point','Earthing','IDU Fan Motor','ODU Fan Motor','Others','Sealed System','NWD']
            elif pr=='RF':
                w = ['Accessories','Cabinet','Cooling Coil','Compressor','Control Card','Door','Electrical Point','Earthing','Fan Motor','Fuse','Others','Sealed System','Shelf','NWD']
            elif pr=='WM':
                w = ['Accessories','Brake','Cabinet','Control Card','Electrical Point','Earthing','Fuse','Others','Pipe','Spin Motor','Wash Motor','NWD']
            elif pr=='MW':
                w = ['Accessories','Cabinet','Control Card','Door','Electrical Point','Earthing','Fuse','Magnetron','Lock','Others','Motor','NWD']

            a = ['Repaired','Pending','Replaced']
            params = {'order':so,'location':ln,'tech':tn,'pcode':pc,'serial':sn,'war':wr,'contract':cn,'visit':exdt,'alldata':w,'alldata1':a}
            return render(request,'visit.html',params)
        else:
            params = {'msg':'Please Maintain Appliance Details'}
            return render(request,'errorpage.html',params)

def visitsave(request):
    if request.method=="POST":
        sod=request.POST.get('sorder')
        lc=request.POST.get('loc')
        t=request.POST.get('tech')
        prd=request.POST.get('prodcode')
        ser_no=request.POST.get('serno')
        ws=request.POST.get('warsts')
        cnt=request.POST.get('cont')
        v_date=request.POST.get('vdate')
        st=request.POST.get('stime')
        et=request.POST.get('etime')
        wd=request.POST.get('work')
        act=request.POST.get('action')
        rem=request.POST.get('remark')
    dt=d=arrow.now().format('DD/MM/YYYY')
    tm=time.strftime("%H%M")
    today = datetime.strptime(dt, "%d/%m/%Y")           #current date
    vdt = datetime.strptime(v_date, "%d/%m/%Y")   #visit date
    pr=lc[0:2]
    a = ['Repaired','Pending','Replaced']
    if pr=='AC':
        w = ['Accessories','Cabinet','Cooling Coil','Compressor','Control Card','Electrical Point','Earthing','IDU Fan Motor','ODU Fan Motor','Others','Sealed System','NWD']
    elif pr=='RF':
        w = ['Accessories','Cabinet','Cooling Coil','Compressor','Control Card','Door','Electrical Point','Earthing','Fan Motor','Fuse','Others','Sealed System','Shelf','NWD']
    elif pr=='WM':
        w = ['Accessories','Brake','Cabinet','Control Card','Electrical Point','Earthing','Fuse','Others','Pipe','Spin Motor','Wash Motor','NWD']
    elif pr=='MW':
        w = ['Accessories','Cabinet','Control Card','Door','Electrical Point','Earthing','Fuse','Magnetron','Lock','Others','Motor','NWD']
    
    
    if vdt==today and (st>tm or et>tm):    
        mg='Start Time And End Time Should Be Less than Current Time'
        params = {'order':sod,'location':lc,'tech':t,'pcode':prd,'serial':ser_no,'war':ws,'contract':cnt,'visit':v_date,'stm':st,'etm':et,'wrk':wd,'ac':act,'rk':rem,'msg':mg,'alldata':w,'alldata1':a}
        return render(request,'visit.html',params)
    elif vdt>today:
        mg='Visit Date Cannot Be Greater Than Current Date'
        params = {'order':sod,'location':lc,'tech':t,'pcode':prd,'serial':ser_no,'war':ws,'contract':cnt,'visit':v_date,'stm':st,'etm':et,'wrk':wd,'ac':act,'rk':rem,'msg':mg,'alldata':w,'alldata1':a}
        return render(request,'visit.html',params)
    elif et<st:
        mg='Start Time Should Less Than End Time'
        params = {'order':sod,'location':lc,'tech':t,'pcode':prd,'serial':ser_no,'war':ws,'contract':cnt,'visit':v_date,'stm':st,'etm':et,'wrk':wd,'ac':act,'rk':rem,'msg':mg,'alldata':w,'alldata1':a}
        return render(request,'visit.html',params)
    else:
        obj1=Technician.objects.filter(Code=t)
        tname=''
        for e1 in obj1:
            tname+=e1.Name
        mg='Saved Successfully'
        vsave = VisitDetail(Service_Order=sod,Location=lc,Technician=t,Technician_Name=tname,Product_Code=prd,Serial_No=ser_no,Warranty=ws,Contract_No=cnt,Visit_Date=v_date,Start_Time=st,End_Time=et,Work_Done=wd,Action=act,Remark=rem,UDate=dt,UTime=tm)
        vsave.save()
        obj2=CallCentre.objects.filter(Service_Order=sod).update(Status='Pending')
        params = {'order':sod,'location':lc,'tech':t,'pcode':prd,'serial':ser_no,'war':ws,'contract':cnt,'visit':v_date,'stm':st,'etm':et,'wrk':wd,'ac':act,'rk':rem,'msg':mg,'alldata':w,'alldata1':a}
        return render(request,'visit.html',params)

def displayvisit(request,sod):
    obj=VisitDetail.objects.filter(Service_Order=sod)
    if obj:
        es=el=et=etn=epc=esn=ew=ecn=evd=est=eet=ew=eac=''
        for e in obj:
            es+=e.Service_Order
            el+=e.Location
            et+=e.Technician
            etn+=e.Technician_Name
            epc+=e.Product_Code
            esn+=e.Serial_No
            ew+=e.Warranty
            ecn+=e.Contract_No
            evd+=e.Visit_Date
            est+=e.Start_Time
            eet+=e.End_Time
            ew+=e.Work_Done
            eac+=e.Action
        context={'alldata':obj}
        return render(request,'displayvisit.html',context)
    else:
        context={'msg':'No Visits Found'}
        return render(request,'errorpage.html',context)

def rating(request):
    return render(request,'rating.html')

def feedback(request):
    if request.method=="POST":
        so=request.POST.get('sod')

    obj0=CallCentre.objects.filter(Service_Order=so,Status='Closed')
    if obj0:
        obj=CallCentre.objects.filter(Service_Order=so)
        fn=ln=pr=t=tn=wd=''
        for e in obj:
            fn+=e.First_Name
            ln+=e.Last_Name
            pr+=e.Product
        obj1=VisitDetail.objects.filter(Service_Order=so)
        for e1 in obj1:
            t+=e1.Technician
            tn+=e1.Technician_Name
            wd+=e1.Work_Done
    
        params = {'order':so,'name':fn+' '+ln,'tech':t+' - '+tn,'prod':pr,'wk':wd}
        return render(request,'feedback.html',params)
    else:
        error = 'Call Is Not Closed, Please Close The Call To Continue'
        params = {'order':so,'msg':error}
        return render(request,'rating.html',params)
        

def feedbacksave(request):
    if request.method=="POST":
        so=request.POST.get('sod')
        bh=request.POST.get('beh')
        sv=request.POST.get('serv')
        nm=request.POST.get('cname')
        tnm=request.POST.get('tname')
        p=request.POST.get('pname')
        w=request.POST.get('wname')
    tech=(tnm[0:6])
    tname=(tnm[9:])

    params = {'order':so,'name':nm,'tech':tnm,'prod':p,'wk':w,'r':bh,'r1':sv,'msg':'Thank You For Your Feedback'}
    rs = Rating(Service_Order=so,Name=nm,Technician=tech,Technician_Name=tname,Product=p,Work_Done=w,Behaviour=bh,Service=sv)
    rs.save()
    return render(request,'feedback.html',params)

def royalty(request,so):
    obj0=CallCentre.objects.filter(Service_Order=so)
    sts=''
    for e0 in obj0:
        sts=e0.Status
    if sts=='Free':
        error = 'Status is Free'
        params = {'order':so,'msg':error}
        return render(request,'callupdate.html',params)
    elif sts=='Closed':
        error = 'Call Is Already Closed'
        params = {'order':so,'msg':error}
        return render(request,'callupdate.html',params)
    else:
        sc=''
        obj=VisitDetail.objects.filter(Service_Order=so)
        if obj:
            ln=tn=wr=''
            for e in obj:
                ln=e.Location
                tn=e.Technician
                wr=e.Warranty
            pr=(ln[0:2])
            if wr=='In Warranty' or wr=='In Protection' or wr=='Dealer':
                sc==''
            else:
                if pr=='AC':
                    sc='550'
                elif pr=='RF':
                    sc='450'
                elif pr=='WM':
                    sc='350'
                else:
                    sc='350'
            if pr=='AC':
                pt=['---','Back Cover','Blower','Capacitor','Condensor','Compressor','Display PCB','Drain Pipe','Evaporator','Filter','Front Cover','IDO Motor','Main PCB','ODU Fan Motor','Power Cord','Remote','Sensor','Swing Motor','Transformer',]
            elif pr=='RF':
                pt=['---','Capacitor','Chiller Tray'',Compressor','Condensor','Dislplay PCB','Drier','Freezer Door','Frame','Gasket','Hinge','Main Door','Main PCB','Power Cord','Light Switch','Sensor','Shelf','Table Top Plastic','']
            elif pr=='WM':
                pt=['---','Base','Brake','Buzzer','Cabinet','Capacitor','Control Panel','Drain Pipe','Frame','Fuse','GearBox','Knob','Power Cord','Pulley','Pulsator','Spin Motor','Spin Timer','Spring','Tub Assembly','V-Belt','Wash Cover','Wash Motor','Wash Timer']
            else:
                pt=['---','Base','Bulb','Cabinet','Capacitor','Diode','Door','Fan Motor','Fuse','Magnetron','Motor','PCB','Power Cord','Sensor','Transformer','Tray']

            params = {'sod':so,'location':ln,'tech':tn,'charge':sc,'part':pt}
            return render(request,'royalty.html',params)
        else:
            params = {'msg':'Please Maintain Atleast One Visit','order':so}
            return render(request,'callupdate.html',params)

def royaltysave(request):
    error=''
    if request.method=="POST":
        so=request.POST.get('sod')
        lc=request.POST.get('loc')
        tc=request.POST.get('tech')
        ct1=request.POST.get('cat1')
        ct2=request.POST.get('cat2')
        ct3=request.POST.get('cat3')
        sc=request.POST.get('scharge')
        prt1=request.POST.get('part1')
        prt2=request.POST.get('part2')
        prt3=request.POST.get('part3')
        pa1=request.POST.get('pamount1')
        pa2=request.POST.get('pamount2')
        pa3=request.POST.get('pamount3')
       # tot=request.POST.get('total')
    obj=VisitDetail.objects.filter(Service_Order=so)
    ln=tn=wr=''
    for e in obj:
        ln+=e.Location
        tn+=e.Technician
        tname=e.Technician_Name
        wr+=e.Warranty
    pr=(ln[0:2])
    
    if pr=='AC':
        pt=['---','Back Cover','Blower','Capacitor','Condensor','Compressor','Display PCB','Drain Pipe','Evaporator','Filter','Front Cover','IDO Motor','Main PCB','ODU Fan Motor','Power Cord','Remote','Sensor','Swing Motor','Transformer',]
    elif pr=='RF':
        pt=['---','Capacitor','Chiller Tray'',Compressor','Condensor','Dislplay PCB','Drier','Freezer Door','Frame','Gasket','Hinge','Main Door','Main PCB','Power Cord','Light Switch','Sensor','Shelf','Table Top Plastic','']
    elif pr=='WM':
        pt=['---','Base','Brake','Buzzer','Cabinet','Capacitor','Control Panel','Drain Pipe','Frame','Fuse','GearBox','Knob','Power Cord','Pulley','Pulsator','Spin Motor','Spin Timer','Spring','Tub Assembly','V-Belt','Wash Cover','Wash Motor','Wash Timer']
    else:
        pt=['---','Base','Bulb','Cabinet','Capacitor','Diode','Door','Fan Motor','Fuse','Magnetron','Motor','PCB','Power Cord','Sensor','Transformer','Tray']
    
    if wr=='In Chargeable' and (sc=='' or sc=='0' or sc==0):
        error='Please Enter Service Charge'
        params = {'sod':so,'location':lc,'tech':tc,'charge':sc,'part':pt,'msg':error}
        return render(request,'royalty.html',params)
    
    if (ct1=='CHA' and (pa1=='' or pa1=='0')) or (ct2=='CHA' and (pa2=='' or pa2=='0')) or (ct3=='CHA' and (pa3=='' or pa3=='0')):
        error = 'Please Enter Correct Part Amount'
        params = {'sod':so,'location':lc,'tech':tc,'charge':sc,'ctg1':ct1,'ctg2':ct2,'ctg3':ct3,'part':pt,'pamt1':pa1,'pamt2':pa2,'pamt3':pa3,'msg':error}
        return render(request,'royalty.html',params)

    if (ct1=='DEA' and (sc>'0' or pa1>'0')) or (ct2=='DEA' and (sc>'0' or pa2>'0')) or (ct3=='DEA' and (sc>'0' or pa3>'0')):
        error = 'Service Charge/Part Amount is Not Applicable On Dealer'
        params = {'sod':so,'location':lc,'tech':tc,'charge':sc,'ctg1':ct1,'ctg2':ct2,'ctg3':ct3,'part':pt,'pamt1':pa1,'pamt2':pa2,'pamt3':pa3,'msg':error}
        return render(request,'royalty.html',params)

    if ((ct1=='WAR' or ct1=='CON') and pa1>'0') or ((ct2=='WAR' or ct2=='CON') and pa2>'0') or ((ct3=='WAR' or ct3=='CON') and pa3>'0'):
        error = 'Invalid Part Amount for WAR/CON Category'
        params = {'sod':so,'location':lc,'tech':tc,'charge':sc,'ctg1':ct1,'ctg2':ct2,'ctg3':ct3,'part':pt,'pamt1':pa1,'pamt2':pa2,'pamt3':pa3,'msg':error}
        return render(request,'royalty.html',params)
    
    if (ct1!='---' and prt1=='---') or (ct2!='---' and prt2=='---') or (ct3!='---' and prt3=='---'):
        error = 'Please Select The Part'
        params = {'sod':so,'location':lc,'tech':tc,'charge':sc,'ctg1':ct1,'ctg2':ct2,'ctg3':ct3,'part':pt,'pamt1':pa1,'pamt2':pa2,'pamt3':pa3,'msg':error}
        return render(request,'royalty.html',params)  

    if (sc=='' or sc=='0'):
        sc=0
    if  (pa1=='' or pa1=='0'):
        pa1=0
    if  (pa2=='' or pa2=='0'):
        pa2=0
    if  (pa3=='' or pa3=='0'):
        pa3=0
    tot = int(sc)+int(pa1)+int(pa2)+int(pa3)
    rs = Royalty(Service_Order=so,Location=lc,Technician=tc,Technician_Name=tname,Service_Charge=sc,Category1=ct1,Category2=ct2,Category3=ct3,Part_Name1=prt1,Part_Name2=prt2,Part_Name3=prt3,Part_Amount1=pa1,Part_Amount2=pa2,Part_Amount3=pa3,Total=tot)
    rs.save()
    error = 'Saved Successfully'
    params = {'sod':so,'location':lc,'tech':tc,'charge':sc,'ctg1':ct1,'ctg2':ct2,'ctg3':ct3,'part':pt,'pamt1':pa1,'pamt2':pa2,'pamt3':pa3,'total':tot,'msg':error}
    return render(request,'royalty.html',params)
    
def royaltyshow(request,so):
    obj=Royalty.objects.filter(Service_Order=so)
    if obj:
        od=lc=t=tn=sc=ct1=ct2=ct3=pn1=pn2=pn3=pa1=pa2=pa3=tot=''
        for e in obj:
            od+=e.Service_Order
            lc+=e.Location
            t+=e.Technician
            tn+=e.Technician_Name
            sc+=e.Service_Charge
            ct1+=e.Category1
            ct2+=e.Category2
            ct3+=e.Category3
            pn1+=e.Part_Name1
            pn2+=e.Part_Name2
            pn3+=e.Part_Name3
            pa1+=e.Part_Amount1
            pa2+=e.Part_Amount2
            pa3+=e.Part_Amount3
            tot+=e.Total
        params = {'alldata':obj}
        return render(request,'royaltyshow.html',params)
    else:
        mg = 'No Records Found'
        params = {'msg':mg}
        return render(request,'errorpage.html',params)

def callclose(request,so):
    obj0=CallCentre.objects.filter(Service_Order=so)
    sts=''
    for e0 in obj0:
        sts=e0.Status
    if sts=='Free':
        error = 'Status is Free'
        params = {'order':so,'msg':error}
        return render(request,'callupdate.html',params)
    elif sts=='Closed':
        error = 'Call Is Already Closed'
        params = {'order':so,'msg':error}
        return render(request,'callupdate.html',params)
    else:
        params = {'order':so}
        return render(request,'callclose.html',params)

def closesave(request):
    if request.method=="POST":
        so=request.POST.get('sod')
        ac=request.POST.get('act')
    obj=VisitDetail.objects.filter(Service_Order=so)
    acc=wr=''
    for e in obj:
        acc=e.Action
        wr=e.Warranty
    obj1=Royalty.objects.filter(Service_Order=so)
    sc=''
    for e1 in obj1:
        sc=e1.Service_Charge
    
    if wr=='In Chargeable' and (sc=='0' or sc==0 or sc==''):
        error = 'Incorrect Service Charge'
        params = {'order':so,'msg':error}
        return render(request,'callclose.html',params)

    if ac=='Yes' and acc=='Pending':
        error = 'Last Visit Action Is Pending, Cannot Be Closed'
        params = {'order':so,'msg':error}
        return render(request,'callclose.html',params)
    if ac=='No':
        error = 'Please Choose The Correct Option'
        params = {'order':so,'msg':error}
        return render(request,'callclose.html',params)
    error = 'Call Closed Successfully'
    params = {'order':so,'msg':error}
    obj1=CallCentre.objects.filter(Service_Order=so).update(Status='Closed')
    return render(request,'callclose.html',params)

def test(request):

    raw = parser.from_file('sample.pdf')
    dt = raw['content']
    print(dt)
    from googletrans import Translator
    import pyttsx3


    translator = Translator()
    translator.translate('안녕하세요.')
    # <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>
    s = translator.translate('안녕하세요.', dest='hi')
    print(s)
    # <Translated src=ko dest=ja text=こんにちは。 pronunciation=Kon'nichiwa.>
    t = translator.translate('This is a nice day', dest='hi')
    # <Translated src=la dest=en text=The truth is my light pronunciation=The truth is my light>
    print(t.src)
    print(t.dest)
    print(t.text)
    return HttpResponse(t.text)

#CALLCENTRE
    obj=CallCentre.objects.all()
    so=lc=fn=ln=pr=fl=add=cty=mob=pin=sts=rd=rt=rd=''
    ltorder=[]
    ltlocation=[]
    ltfname=[]
    ltlname=[]
    ltproduct=[]
    ltfault=[]
    ltaddress=[]
    ltcity=[]
    ltmobile=[]
    ltpin=[]
    ltstatus=[]
    ltrepdate=[]
    ltreptime=[]
    for e in obj:
        so=e.Service_Order
        lc=e.Location    
        fn=e.First_Name
        ln=e.Last_Name
        pr=e.Product
        fl=e.Fault
        add=e.Address
        cty=e.City
        mob=e.Mobile_No
        pin=e.Pin_Code
        sts=e.Status
        rd=e.Reported_Date
        rt=e.Reported_Time
        ltorder.append(so)
        ltlocation.append(lc)
        ltfname.append(fn)
        ltlname.append(ln)
        ltproduct.append(pr)
        ltfault.append(fl)
        ltaddress.append(add)
        ltcity.append(cty)
        ltmobile.append(mob)
        ltpin.append(pin)
        ltstatus.append(sts)
        ltrepdate.append(rd)
        ltreptime.append(rt)
#PLANNING
    obj1=Planning.objects.all()
    so1=apdt=aptm=tech=tnm=exdt=extm=etm=''
    ltorder1=[]
    ltappdate=[]
    ltapptime=[]
    lttechnician=[]
    lttechname=[]
    ltexdate=[]
    ltextime=[]
    ltendtime=[]
    for e1 in obj1:
        so1=e1.Service_Order
        apdt=e1.Appointment_Date    
        aptm=e1.Appointment_Time
        tech=e1.Technician
        tnm=e1.Technician_Name
        exdt=e1.Execution_Date
        extm=e1.Execution_Time
        etm=e1.End_Time
        ltorder1.append(so1)
        ltappdate.append(apdt)
        ltapptime.append(aptm)
        lttechnician.append(tech)
        lttechname.append(tnm)
        ltexdate.append(exdt)
        ltextime.append(extm)
        ltendtime.append(etm)
#DETAILS    
    obj2=Details.objects.all()
    so2=cst=pcode=serno=dop=exp=cont=effst=effet=''
    ltorder2=[]
    ltcusttype=[]
    ltpcode=[]
    ltserialno=[]
    ltdop=[]
    ltexpiry=[]
    ltcontract=[]
    lteffstart=[]
    lteffend=[]
    for e2 in obj2:
        so2=e2.Service_Order
        cst=e2.Cust_Type    
        pcode=e2.Product_Code
        serno=e2.Serial_No
        dop=e2.DOP
        exp=e2.Expiry
        cont=e2.Contract_No
        effst=e2.Effective_Date
        effet=e2.Effective_Expiry
        ltorder2.append(so2)
        ltcusttype.append(cst)
        ltpcode.append(pcode)
        ltserialno.append(serno)
        ltdop.append(dop)
        ltexpiry.append(exp)
        ltcontract.append(cont)
        lteffstart.append(effst)
        lteffend.append(effet)
#VISITDETAIL   
    obj3=VisitDetail.objects.all()
    so3=vt=vtn=vpc=vsn=vwr=vcn=vvdt=vst=vet=wd=act=rem=vud=vut=''
    ltorder3=[]
    ltvtech=[]
    ltvtechname=[]
    ltvpcode=[]
    ltvserno=[]
    ltvwar=[]
    ltvcontract=[]
    ltvdate=[]
    ltvtime=[]
    ltvetime=[]
    ltwork=[]
    ltaction=[]
    ltremark=[]
    ltudate=[]
    ltutime=[]
    for e3 in obj3:
        so3=e3.Service_Order
        vt=e3.Technician    
        vtn=e3.Technician_Name
        vpc=e3.Product_Code
        vsn=e3.Serial_No
        vwr=e3.Warranty
        vcn=e3.Contract_No
        vvdt=e3.Visit_Date
        vst=e3.Start_Time
        vet=e3.End_Time
        wd=e3.Work_Done
        act=e3.Action
        rem=e3.Remark
        vud=e3.UDate
        vut=e3.UTime
        ltorder3.append(so3)
        ltvtech.append(vt)
        ltvtechname.append(vtn)
        ltvpcode.append(vpc)
        ltvserno.append(vsn)
        ltvwar.append(vwr)
        ltvcontract.append(vcn)
        ltvdate.append(vvdt)
        ltvtime.append(vst)
        ltvetime.append(vet)
        ltwork.append(wd)
        ltaction.append(act)
        ltremark.append(rem)
        ltudate.append(vud)
        ltutime.append(vut)
#ROYALTY   
    obj4=Royalty.objects.all()
    so4=sc=ct1=ct2=ct3=pn1=pn2=pn3=pat1=pat2=pat3=ttl=rdt=rtm=''
    ltorder4=[]
    ltscharge=[]
    ltcat1=[]
    ltcat2=[]
    ltcat3=[]
    ltpname1=[]
    ltpname2=[]
    ltpname3=[]
    ltpamt1=[]
    ltpamt2=[]
    ltpamt3=[]
    lttotal=[]
    ltrdate=[]
    ltrtime=[]
    for e4 in obj4:
        so4=e4.Service_Order
        sc=e4.Service_Charge    
        ct1=e4.Category1
        ct2=e4.Category2
        ct3=e4.Category3
        pn1=e4.Part_Name1
        pn2=e4.Part_Name2
        pn3=e4.Part_Name3
        pat1=e4.Part_Amount1
        pat2=e4.Part_Amount2
        pat3=e4.Part_Amount3
        ttl=e4.Total
        rdt=e4.RDate
        rtm=e4.RTime
        ltorder4.append(so4)
        ltscharge.append(sc)
        ltcat1.append(ct1)
        ltcat2.append(ct2)
        ltcat3.append(ct3)
        ltpname1.append(pn1)
        ltpname2.append(pn2)
        ltpname3.append(pn3)
        ltpamt1.append(pat1)
        ltpamt2.append(pat2)
        ltpamt3.append(pat3)
        lttotal.append(ttl)
        ltrdate.append(rdt)
        ltrtime.append(rtm)
#RATING
    obj5=Rating.objects.all()
    so5=apdt=aptm=tech=tnm=exdt=extm=etm=''
    ltorder5=[]
    ltname=[]
    ltratingtech=[]
    ltratingtechname=[]
    ltprod=[]
    ltworkdone=[]
    ltbehaviour=[]
    ltservice=[]
    for e5 in obj5:
        so5=e5.Service_Order
        nm=e5.Name    
        rttech=e5.Technician
        rttechnm=e5.Technician_Name
        prd=e5.Product
        wkdn=e5.Work_Done
        behv=e5.Behaviour
        serv=e5.Service
        ltorder5.append(so5)
        ltname.append(nm)
        ltratingtech.append(rttech)
        ltratingtechname.append(rttechnm)
        ltprod.append(prd)
        ltworkdone.append(wkdn)
        ltbehaviour.append(behv)
        ltservice.append(serv)
    ccentre = {'Service Order':ltorder,'Location':ltlocation,'Reported Date':ltrepdate,'Reported Time':ltreptime,
    'Status':ltstatus,'First Name':ltfname,'Last Name':ltlname,'Product':ltproduct,'Fault':ltfault,'Address':ltaddress,
    'City':ltcity,'Mobile':ltmobile,'PIN':ltpin}
    
    plan = {'Service Order':ltorder1,'Appointment Date':ltappdate,'Appointment Time':ltapptime,'Technician':lttechnician,
    'Technician Name':lttechname,'Execution Date':ltexdate,'Execution Time':ltextime,'End Time':ltendtime}
    
    detail = {'Service Order':ltorder2,'Customer Type':ltcusttype,'Product Code':ltpcode,'Serial Number':ltserialno,
    'Date Of Purchase':ltdop,'Expiry Date':ltexpiry,'Contract':ltcontract,'Effective Date':lteffstart,'Effective Expiry':lteffend}
    
    visit = {'Service Order':ltorder3,'Warranty Status':ltvwar,
    'Visit Date':ltvdate,'Start Time':ltvtime,'Finish Time':ltvetime,'Work Done':ltwork,
    'Action':ltaction,'Remarks':ltremark,'Updation Date':ltudate,'Updation Time':ltutime}

    royalty = {'Service Order':ltorder4,'Service Charge':ltscharge,'Category 1':ltcat1,'Category 2':ltcat2,
    'Category 3':ltcat3,'Part Name 1':ltpname1,'Part Name 2':ltpname2,'Part Name 3':ltpname3,'Part Amount 1':ltpamt1,
    'Part Amount 2':ltpamt2,'Part Amount 3':ltpamt3,'Total':lttotal,'Collection Date':ltrdate,'Collection Time':ltrtime}
    
    rating = {'Service Order':ltorder5,'Customer Name':ltname,'Behaviour':ltbehaviour,'Service':ltservice}

    dfccentre=pd.DataFrame(ccentre)
    dfplan=pd.DataFrame(plan)
    dfdetail=pd.DataFrame(detail)
    dfvisit=pd.DataFrame(visit)
    dfroyalty=pd.DataFrame(royalty)
    dfrating=pd.DataFrame(rating)
    dframe = [dfccentre,dfplan,dfdetail,dfvisit,dfroyalty,dfrating]
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Service Order'],how='outer'), dframe).fillna('-')
    print(df_merged)
    df_merged.to_csv('file.csv',index=False)
    #df.to_csv(r'C:\Users\DANISH\Downloads\file1.csv') 
    print(df_merged[['Service Order','Location','Technician','Technician Name','Product Code']])
    return HttpResponse(dt)

def reports(request):
    return render(request,'reports.html')
    
def plainsummery(request):
    return render(request,'plainsummery.html')

def plainsummarydownload(request):
    if request.method=="POST":
        rdst=request.POST.get('repdatestart')
        rdend=request.POST.get('repdateend')
        cst=request.POST.get('ctype')
        stsfrm=int(request.POST.get('statusfrom'))
        ststo=int(request.POST.get('statusto'))
        pnfrm=request.POST.get('pinfrom')
        pnto=request.POST.get('pinto')
        actn=request.POST.get('act')
        vdet=request.POST.get('vst')
        print(vdet)
#CALLCENTRE
    obj=CallCentre.objects.all()
    so=lc=fn=ln=pr=fl=add=cty=mob=pin=sts=rd=rt=rd=''
    ltorder=[]
    ltlocation=[]
    ltfname=[]
    ltlname=[]
    ltproduct=[]
    ltfault=[]
    ltaddress=[]
    ltcity=[]
    ltmobile=[]
    ltpin=[]
    ltstatus=[]
    ltrepdate=[]
    ltreptime=[]
    for e in obj:
        so=e.Service_Order
        lc=e.Location
        fn=e.First_Name
        ln=e.Last_Name
        pr=e.Product
        fl=e.Fault
        add=e.Address
        cty=e.City
        mob=e.Mobile_No
        pin=e.Pin_Code
        sts=e.Status
        rd=e.Reported_Date
        rt=e.Reported_Time
        ltorder.append(so)
        ltlocation.append(lc)
        ltfname.append(fn)
        ltlname.append(ln)
        ltproduct.append(pr)
        ltfault.append(fl)
        ltaddress.append(add)
        ltcity.append(cty)
        ltmobile.append(mob)
        ltpin.append(pin)
        ltstatus.append(sts)
        ltrepdate.append(rd)
        ltreptime.append(rt)
#DETAILS    
    obj2=Details.objects.all()
    so2=cst1=''
    ltorder2=[]
    ltcusttype=[]
    for e2 in obj2:
        so2=e2.Service_Order
        cst1=e2.Cust_Type    
        ltorder2.append(so2)
        ltcusttype.append(cst1)
#VISITDETAIL   
    obj3=VisitDetail.objects.all()
    so3=vt=vtn=vpc=vsn=vwr=vcn=vvdt=vst=vet=wd=act=rem=vud=vut=''
    ltorder3=[]
    ltvtech=[]
    ltvtechname=[]
    ltvpcode=[]
    ltvserno=[]
    ltvwar=[]
    ltvcontract=[]
    ltvdate=[]
    ltvtime=[]
    ltvetime=[]
    ltwork=[]
    ltaction=[]
    ltremark=[]
    ltudate=[]
    ltutime=[]
    for e3 in obj3:
        so3=e3.Service_Order
        vt=e3.Technician    
        vtn=e3.Technician_Name
        vpc=e3.Product_Code
        vsn=e3.Serial_No
        vwr=e3.Warranty
        vcn=e3.Contract_No
        vvdt=e3.Visit_Date
        vst=e3.Start_Time
        vet=e3.End_Time
        wd=e3.Work_Done
        act=e3.Action
        rem=e3.Remark
        vud=e3.UDate
        vut=e3.UTime
        ltorder3.append(so3)
        ltvtech.append(vt)
        ltvtechname.append(vtn)
        ltvpcode.append(vpc)
        ltvserno.append(vsn)
        ltvwar.append(vwr)
        ltvcontract.append(vcn)
        ltvdate.append(vvdt)
        ltvtime.append(vst)
        ltvetime.append(vet)
        ltwork.append(wd)
        ltaction.append(act)
        ltremark.append(rem)
        ltudate.append(vud)
        ltutime.append(vut)

    ccentre = {'Service Order':ltorder,'Location':ltlocation,'Reported Date':ltrepdate,'Reported Time':ltreptime,
    'Status':ltstatus,'First Name':ltfname,'Last Name':ltlname,'Product':ltproduct,'Fault':ltfault,'Address':ltaddress,
    'City':ltcity,'Mobile':ltmobile,'PIN':ltpin}
    
    detail = {'Service Order':ltorder2,'Customer Type':ltcusttype}
    
    visit = {'Service Order':ltorder3,'Warranty Status':ltvwar,
    'Visit Date':ltvdate,'Start Time':ltvtime,'Finish Time':ltvetime,'Work Done':ltwork,
    'Action':ltaction,'Remarks':ltremark,'Updation Date':ltudate,'Updation Time':ltutime}
    
    df1 = pd.DataFrame(ccentre)
    df2 = pd.DataFrame(detail)
    df3 = pd.DataFrame(visit)
    dframe = [df1,df2,df3]
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Service Order'],how='outer'), dframe).fillna('-')
    
    st = datetime.strptime(rdst, "%d/%m/%Y")
    strt = datetime.strftime(st, "%Y-%m-%d")
    end = datetime.strptime(rdend, "%d/%m/%Y")
    endt = datetime.strftime(end, "%Y-%m-%d")

    df_merged['Reported Date'] = pd.to_datetime(df_merged['Reported Date'],dayfirst=True)
#    print(df_merged)
    df_merged['Status'].replace(['Free','Blank','Pending','Closed'],[1,2,3,4],inplace=True)
#    print(df_merged)
    
    date_range = ((df_merged['Reported Date'] >= strt) & (df_merged['Reported Date'] <= endt))
    df_date_range = df_merged.loc[date_range]
    #print(df_date_range)

    dfsts = df_date_range.groupby(['Customer Type'])
    df_status = dfsts.get_group(cst)
#    print(df_status)
    
#    print(ststo-stsfrm)
    if ststo>stsfrm:
        mask = ((df_status['Status'] >= stsfrm) & (df_status['Status'] <= ststo))
        dff = df_status.loc[mask]
#        print(dff1)
    else:
        mask = ((df_status['Status'] >= ststo) & (df_status['Status'] <= stsfrm))
        dff = df_status.loc[mask]
#        print(dff)

    dff['Status'].replace([1,2,3,4],['Free','Blank','Pending','Closed'],inplace=True)
#    print(dff)
    
    if actn == None:
        df_action = (dff)
    else:
        dfactn = (dff['Action'] == actn)
        df_action = dff.loc[dfactn]
#    print(df_action)

    print(vdet)

    if vdet == 'on':
        df_final = df_action
    else:
        df_final = df_action[['Service Order','Location','Reported Date','Reported Time','Status','First Name','Last Name','Product','Fault','Address','City','Mobile','PIN']]
    
    print(df_final)

    df_final.to_csv('file.csv',index=False)
    
    return render(request,'plainsummery.html')

def visitreport(request):
    obj = Technician.objects.all()
    params = {'Names':obj}

    
    return render(request,'visitreport.html',params)

def visitreportdwnld(request):
    obj = Technician.objects.all()
    params = {'Names':obj}
    if request.method=="POST":
        rdst = request.POST.get('repdatestart')
        rdend = request.POST.get('repdateend')
        cust = request.POST.get('ctype')
        techst = request.POST.get('techfrom')
        techen = request.POST.get('techto')
        actn = request.POST.get('act')
        vdtst = request.POST.get('vdatefrom')
        vdten = request.POST.get('vdateto')
        warsts = request.POST.get('war')
        print(warsts)
        

#CALLCENTRE
    obj=CallCentre.objects.all()
    so=lc=fn=ln=pr=fl=add=cty=mob=pin=sts=rd=rt=rd=''
    ltorder=[]
    ltlocation=[]
    ltfname=[]
    ltlname=[]
    ltproduct=[]
    ltfault=[]
    ltaddress=[]
    ltcity=[]
    ltmobile=[]
    ltpin=[]
    ltstatus=[]
    ltrepdate=[]
    ltreptime=[]
    for e in obj:
        so=e.Service_Order
        lc=e.Location    
        fn=e.First_Name
        ln=e.Last_Name
        pr=e.Product
        fl=e.Fault
        add=e.Address
        cty=e.City
        mob=e.Mobile_No
        pin=e.Pin_Code
        sts=e.Status
        rd=e.Reported_Date
        rt=e.Reported_Time
        ltorder.append(so)
        ltlocation.append(lc)
        ltfname.append(fn)
        ltlname.append(ln)
        ltproduct.append(pr)
        ltfault.append(fl)
        ltaddress.append(add)
        ltcity.append(cty)
        ltmobile.append(mob)
        ltpin.append(pin)
        ltstatus.append(sts)
        ltrepdate.append(rd)
        ltreptime.append(rt)
#VISITDETAIL   
    obj3=VisitDetail.objects.all()
    so3=vt=vtn=vpc=vsn=vwr=vcn=vvdt=vst=vet=wd=act=rem=vud=vut=''
    ltorder3=[]
    ltvtech=[]
    ltvtechname=[]
    ltvpcode=[]
    ltvserno=[]
    ltvwar=[]
    ltvcontract=[]
    ltvdate=[]
    ltvtime=[]
    ltvetime=[]
    ltwork=[]
    ltaction=[]
    ltremark=[]
    ltudate=[]
    ltutime=[]
    for e3 in obj3:
        so3=e3.Service_Order
        vt=e3.Technician    
        vtn=e3.Technician_Name
        vpc=e3.Product_Code
        vsn=e3.Serial_No
        vwr=e3.Warranty
        vcn=e3.Contract_No
        vvdt=e3.Visit_Date
        vst=e3.Start_Time
        vet=e3.End_Time
        wd=e3.Work_Done
        act=e3.Action
        rem=e3.Remark
        vud=e3.UDate
        vut=e3.UTime
        ltorder3.append(so3)
        ltvtech.append(vt)
        ltvtechname.append(vtn)
        ltvpcode.append(vpc)
        ltvserno.append(vsn)
        ltvwar.append(vwr)
        ltvcontract.append(vcn)
        ltvdate.append(vvdt)
        ltvtime.append(vst)
        ltvetime.append(vet)
        ltwork.append(wd)
        ltaction.append(act)
        ltremark.append(rem)
        ltudate.append(vud)
        ltutime.append(vut)
    ccentre = {'Service Order':ltorder,'Location':ltlocation,'Reported Date':ltrepdate,'Reported Time':ltreptime,
    'Status':ltstatus,'First Name':ltfname,'Last Name':ltlname,'Product':ltproduct,'Fault':ltfault,'Address':ltaddress,
    'City':ltcity,'Mobile':ltmobile,'PIN':ltpin}

    visit = {'Service Order':ltorder3,'Technician':ltvtech,'Technician Name':ltvtechname,'Warranty Status':ltvwar,
    'Visit Date':ltvdate,'Start Time':ltvtime,'Finish Time':ltvetime,'Work Done':ltwork,
    'Action':ltaction,'Remarks':ltremark,'Updation Date':ltudate,'Updation Time':ltutime}

    df1 = pd.DataFrame(ccentre)
    df2 = pd.DataFrame(visit)
    dframe = [df1,df2]
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Service Order'],how='outer'), dframe).fillna('-')
    
    st = datetime.strptime(rdst, "%d/%m/%Y")
    strt = datetime.strftime(st, "%Y-%m-%d")
    end = datetime.strptime(rdend, "%d/%m/%Y")
    endt = datetime.strftime(end, "%Y-%m-%d")

    df_merged['Reported Date'] = pd.to_datetime(df_merged['Reported Date'],dayfirst=True)
#    print(df_merged)

    date_range = ((df_merged['Reported Date'] >= strt) & (df_merged['Reported Date'] <= endt))
    df_rp_date_range = df_merged.loc[date_range]
    #print(df_rp_date_range)
    
    df_tech = ((df_rp_date_range['Technician Name'] == techst) | (df_merged['Technician Name'] == techen))
    df_tech_range = df_rp_date_range.loc[df_tech]
    #print(df_tech_range)
    
    if actn == None:
        df_action = df_tech_range
    else:
        dfactn = (df_tech_range['Action'] == actn)
        df_action = df_tech_range.loc[dfactn]
#    print(df_action)
 
    v_date_range = ((df_action['Visit Date'] >= vdtst) & (df_merged['Visit Date'] <= vdten))
    df_visitdate_range = df_action.loc[v_date_range]

    if warsts == None:
        df_final = df_visitdate_range
    else:
        df_fnl = (df_visitdate_range['Warranty Status'] == warsts)
        df_final = df_visitdate_range.loc[df_fnl]
    print(df_final)
    df_final.to_csv('file.csv',index=False)

    return render(request,'visitreport.html',params)