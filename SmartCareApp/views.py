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
from django_pandas.io import read_frame

# This function redirects user to login page, servicecentre page or callcentre page 
# according to session
def smartcare(request):
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

    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return HttpResponseRedirect('/callcentre')
            elif request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return render(request,'login.html')
        else:
            return render(request,'login.html')

# for logout

def logout(request):
    if request.session.has_key('is_logged'):
        del request.session['is_logged']
        return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')

# Redirects to callcentre page
# Session value 0 for callcentre
# 1 for servicecentre
def callcentre(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 0:
            return render(request,'callcentre.html')
        elif request.session['is_logged'] == 1:
            return HttpResponseRedirect('/servicecentre')
    else:
        return HttpResponseRedirect('/smartcare')

# to register call
def callregister(request):
    if request.method=="POST":
        sno = ''
        lno = ''
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
        # print(prdt)   
        if prdt=="--SELECT--" or fnm=='' or lnm=='' or flt=='' or add=='' or cty=='' or phno=='' or pincode=='':
            er='Please Fill All The Fields'
            params={'a':sno,'b':lno,'c':fnm,'d':lnm,'e':prdt,'f':flt,'g':add,'h':cty,'i':phno,'j':pincode,'error':er}
        
        # check for valid inputs
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
    else:
        if request.session.has_key('is_logged'):    # if session key is 0, return callregister, else redirect to smartcare
            if request.session['is_logged'] == 0:
                return render(request,'callregister.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# this opens the contract page
def contract(request):
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return render(request,'contract.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# to save the contract details
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
        # for Expiry Date
        obj=Details.objects.filter(Location=lno,Product_Code=pc,Serial_No=sn)
        if obj:
            end_date=''
            for e in obj:
                end_date+=e.Expiry
            date1 = datetime.strptime(end_date, "%d/%m/%Y")  
            new_date1 = date1 +timedelta(days=1)
            new_sdate = datetime.strftime(new_date1, "%d/%m/%Y")

        # Extended Expiry Date Generation
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

            params = {'alldata':obj0,'val':lno,'contract':cno,'pcode':pc,'serial':sn,'stdt':new_sdate,'edt':new_edate,'price':amt}
            cn = Contract(Location=lno,Contract_No=cno,Product_Code=pc,Serial_No=sn,Start_Date=new_sdate,End_Date=new_edate,Amount=price)
            cn.save()
        else:
            params = {'val':lno,'error':'Enter Valid Serial Number','alldata':obj0}
        return render (request,'contractform.html',params)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return HttpResponseRedirect('/contract')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# For booking Contract
def contractbook(request):
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return render(request,'contractbook.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# Update customer Details page
def custdetail(request):
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return render(request,'custdetail.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# Update customer Details 
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return render(request,'detailsupdate.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# To open service centre page
def servicecentre(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 0:
            return HttpResponseRedirect('/callcentre')
        elif request.session['is_logged'] == 1:
            return render(request,'servicecentre.html')
    else:
        return HttpResponseRedirect('/smartcare')

# Search page functionality
def search(request):
    if request.method == "POST":
        sod = request.POST.get('sorder')
        loc = request.POST.get('sloc')
        mob = request.POST.get('smob')
        con = request.POST.get('scontract')
        if sod:
            obj=CallCentre.objects.filter(Service_Order=sod)
            if obj: 
                context={'alldata':obj,'order':sod}
                return render(request,'orderresult.html',context)
            else:
                context={'msg':'Enter Valid Service Order'}
                return render(request,'search.html',context)
        elif loc:
            obj=CallCentre.objects.filter(Location=loc)
            if obj:
                context={'alldata':obj,'location':loc}
                return render(request,'locationresult.html',context)
            else:
                context={'msg':'Enter Valid Location'}
                return render(request,'search.html',context)
    
        elif mob:
            obj=CallCentre.objects.filter(Mobile_No=mob)
            if obj:
                context={'alldata':obj,'mobile':mob}
                return render(request,'mobileresult.html',context)
            else:
                context={'msg':'Enter Valid Mobile Number'}
                return render(request,'search.html',context)
        else:
            obj=Contract.objects.filter(Contract_No=con)
            if obj:
                context={'alldata':obj,'contract':con}
                return render(request,'contractresult.html',context)
            else:
                context={'msg':'Enter Valid Contract Number'}
                return render(request,'search.html',context)
    else:
        if request.session.has_key('is_logged'):
            return render(request,'search.html')
        else:
            return HttpResponseRedirect('/smartcare')

# To view Service order detials from location in search page
def ordershow(request,so):
    if request.session.has_key('is_logged'):
        obj = CallCentre.objects.filter(Location=so)
        params = {'alldata':obj}
        return render(request,'orderresult.html',params)
    else:
        return HttpResponseRedirect('/smartcare')

# To view Service order detials from location in search page
def order(request,lno):
    if request.session.has_key('is_logged'):
        obj=CallCentre.objects.filter(Location=lno)
        context={'alldata':obj}
        return render(request,'orderresult.html',context)
    else:
        return HttpResponseRedirect('/smartcare')

# For new calls data
def newcalls(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            t = datetime.now()
            w = t - timedelta(minutes=30)
            time_sub=str(w.strftime("%H%M"))
            date=str(t.strftime("%d/%m/%Y"))
            time=str(t.strftime("%H%M"))
            # Displaying all the records between current time and 30 minutes earlier time
            obj=CallCentre.objects.filter(Status='Free',Reported_Date=date,Reported_Time__range=(time_sub,time))
            context={'alldata':obj}
            return render(request,'newcalls.html',context)
        else:
            return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')
    
# all call records with status = Free
def freecalls(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=CallCentre.objects.filter(Status='Free')
            context={'alldata':obj}
            return render(request,'freecalls.html',context)
        else:
            return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')
        
# for call planning page
def callplan(request):
    if request.method=="POST":
        ono=request.POST.get('ordradio')
        
        if not ono:
            obj=CallCentre.objects.filter(Status='Free')

            context = {'msg':'Choose A Service Order','alldata':obj}
            return render(request,'freecalls.html',context)
        else:
            obj=Technician.objects.all()
            ad=arrow.now().format('DD/MM/YYYY')
            context={'alldata':obj,'sod':ono,'apdt':ad}
            return render(request,'callplan.html',context)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# for planning of calls for technician visit
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
        
        # converting dates into proper format
        apdate = datetime.strptime(dt, "%d/%m/%Y")     #appointment date
        exdate = datetime.strptime(ed, "%d/%m/%Y")     #execution date

    # validating for proper inputs
    # checking for Start Time, End time, Date etc.
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# All records with status = Blank
def blankcalls(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=CallCentre.objects.filter(Status='Blank')
            context={'alldata':obj}
            return render(request,'blankcalls.html',context)
        else:
            return HttpResponseRedirect('/smartcare')
    else:
            return HttpResponseRedirect('/smartcare')

# To view plannings
def viewplan(request):
    if request.method=="POST":
        bod=request.POST.get('blankord')
        if not bod:
            obj=CallCentre.objects.filter(Status='Blank')        
            context = {'msg':'Choose A Service Order','alldata':obj}
            return render(request,'blankcalls.html',context)
        else:
            obj=Planning.objects.filter(Service_Order=bod)
            context={'alldata':obj}
            return render(request,'viewplan.html',context)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# All records with status = Pending
def pendingcalls(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=CallCentre.objects.filter(Status='Pending')
            context={'alldata':obj}
            return render(request,'pendingcalls.html',context)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# To view visits of pending calls
def viewvisit(request):
    if request.method=="POST":
        pdod=request.POST.get('pendingord')
        if not pdod:
            obj=CallCentre.objects.filter(Status='Pending')
            context = {'msg':'Choose A Service Order','alldata':obj}
            return render(request,'pendingcalls.html',context)
        else:
            obj=VisitDetail.objects.filter(Service_Order=pdod)
            context={'alldata':obj}
            return render(request,'displayvisit.html',context)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# To display update calls page
# This page(callupdate.html) is called from various functions
def callupdate(request):
    if request.method=='POST':
        odno=request.POST.get('sod')
        obj=CallCentre.objects.filter(Service_Order=odno)
        obj1=Details.objects.filter(Service_Order=odno)
        if not obj:
            params={'error':'Please Enter Valid Service Order'}
            return render (request,'callupdate.html',params)
        else:
            params = {'alldata':obj,'alldata1':obj1}
            return render(request,'callupdation.html',params)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return render(request,'callupdate.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# To save details on Service Order on CallUpdate page
def calldetailsave(request,sno):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj0=Location_Details.objects.filter(Serial_No=sno)
            lno=pr=''
            for e0 in obj0:
                lno=e0.Location
                # pr=e0.Product_Code

            obj1=CallCentre.objects.filter(Location=lno)
            so=''
            for e1 in obj1:
                so=e1.Service_Order

            obj=CallCentre.objects.filter(Service_Order=so)
            
            params = {'alldata':obj,'alldata1':obj0}    
            return render(request,'callupdation.html',params)
        else:
            return redirect('/servicecentre')
    else:
        return HttpResponseRedirect('/smartcare')


# TO BE CHECKED WEATHER THIS FUNCTION IS USED OR NOT

# def callupdateshow(request):
#     obj=''
#     if request.method=='POST':
#         a=request.POST.get('sod')
#     obj=CallCentre.objects.filter(Service_Order=a)
#     context={'alldata':obj}
#     es=el=efn=eln=epr=ef=eadd=ecty=emb=epn=ests=edt=etm=''
#     for e in obj:
#         es+=e.Service_Order
#         el+=e.Location
#         efn+=e.First_Name
#         eln+=e.Last_Name
#         epr+=e.Product
#         ef+=e.Fault
#         eadd+=e.Address
#         ecty+=e.City
#         emb+=e.Mobile_No
#     params={'visit':'Display Call Visits','detail':'Display Appliance Detail','maintain':'Maintain Call Detail','so':es}
#     return render(request,'callupdate.html',params)

# To view Service Order on call update page
def vieworder(request,so):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=CallCentre.objects.filter(Service_Order=so)
            context={'alldata':obj}
            return render(request,'orderresult.html',context)
        else:
            return HttpResponseRedirect('/servicecentre')
    else:
        return HttpResponseRedirect('/smartcare')

# Saving Appliance details
def appdetails(request,lno):
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
        # generating Warranty Expiry date according to Product
        # 3 years for WM, 2 years for RF, 1 year for others
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
        params={'alldata':obj,'loc':lno,'code':prd,'sn':sno,'bill':bno,'dpp':dp,'msg':'Saved Successfully'}

        return render(request,'appdetailsadd.html',params)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                obj=CallCentre.objects.filter(Location=lno)
                params={'alldata':obj}
                return render(request,'appdetailsadd.html',params)
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# To save details on Service Order on CallUpdate page
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
        obj = CallCentre.objects.filter(Service_Order=od)
        obj1=Location_Details.objects.filter(Serial_No=ser)
        for e1 in obj1:
            pr=e1.Product
            pc=e1.Product_Code
            cst=e1.Cust_Type
            bl=e1.Bill_No
            dp=e1.DOP
            ex=e1.Expiry
            cn=e1.Contract_No
            efdt=e1.Effective_Date
            efex=e1.Effective_Expiry
        detsv = Details.objects.filter(Service_Order=od).update(Service_Order=od,Location=lno,Product=pr,
            Cust_Type=cst,Product_Code=pc,Serial_No=ser,Bill_No=bl,DOP=dp,Expiry=ex,Contract_No=cn,Effective_Date=efdt,Effective_Expiry=efex)
        params = {'alldata':obj,'alldata1':obj1,'msg':'Saved Successfully'}    
        return render(request,'callupdation.html',params)
    else:
        if req.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')
    
# To view Appliance Details
def viewdetail(request,loc):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=Location_Details.objects.filter(Location=loc)
            if obj:
                obj1=CallCentre.objects.filter(Location=loc)
                for e1 in obj1:
                    sod=e1.Service_Order
                    context={'alldata':obj,'sod':sod,'location':loc}
                return render(request,'appdetailshow.html',context)
            else:
                context={'msg':'No Details Found'}
                return render(request,'errorpage.html',context)
        else:
            return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')

# To view plannings of Service Order
def viewplanning(request,sod):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=Planning.objects.filter(Service_Order=sod)
            if obj:
                context={'alldata':obj}
                return render(request,'viewplanning.html',context)
            else:
                context={'msg':'No Plannings Found'}
                return render(request,'errorpage.html',context)
        else:
            return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')

# For mainting visit
def visit(request,so):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj0 = CallCentre.objects.filter(Service_Order=so)
            for i in obj0:
                sts=i.Status
            # checking for status, only Blank and Pending calls will be updated
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
                            # checking for Warranty status
                            if edate>rdate:
                                wr='In Warranty'
                                #print('Warranty')
                            elif rdate>edate and rdate<effdate:
                                wr='In Protection'
                                #protection
                            elif rdate>effdate:
                                wr='In Chargeable'
                                #chargeable
                # Defining Work Done codes for different products
                    if pr=='AC':
                        w = ['Accessories','Cabinet','Cooling Coil','Compressor','Control Card','Electrical Point','Earthing','IDU Fan Motor','ODU Fan Motor','Others','Sealed System','NWD']
                    elif pr=='RF':
                        w = ['Accessories','Cabinet','Cooling Coil','Compressor','Control Card','Door','Electrical Point','Earthing','Fan Motor','Fuse','Others','Sealed System','Shelf','NWD']
                    elif pr=='WM':
                        w = ['Accessories','Brake','Cabinet','Control Card','Electrical Point','Earthing','Fuse','Others','Pipe','Spin Motor','Wash Motor','NWD']
                    elif pr=='MW':
                        w = ['Accessories','Cabinet','Control Card','Door','Electrical Point','Earthing','Fuse','Magnetron','Lock','Others','Motor','NWD']
                
                # Defining actions
                    a = ['Repaired','Pending','Replaced']
                    params = {'order':so,'location':ln,'tech':tn,'pcode':pc,'serial':sn,'war':wr,'contract':cn,'visit':exdt,'alldata':w,'alldata1':a}
                    return render(request,'visit.html',params)
                else:
                    params = {'msg':'Please Maintain Appliance Details'}
                    return render(request,'errorpage.html',params)
        else:
            return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')

# Saving visit
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
    
    # checking for proper inputs
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/smartcare')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# Displaying updated visits
def displayvisit(request,sod):
    if request.session.has_key('is_logged'):
        obj=VisitDetail.objects.filter(Service_Order=sod)
        if obj:
            context={'alldata':obj}
            return render(request,'displayvisit.html',context)
        else:
            context={'msg':'No Visits Found'}
            return render(request,'errorpage.html',context)
    else:
        return HttpResponseRedirect('/smartcare')

# for rating service
def rating(request):
    if request.method=="POST":
        so=request.POST.get('sod')

        obj0=CallCentre.objects.filter(Service_Order=so,Status='Closed')
        if obj0:
            obj=CallCentre.objects.filter(Service_Order=so)
            obj1=VisitDetail.objects.filter(Service_Order=so)
            
            params = {'alldata':obj,'alldata1':obj1}
            return render(request,'feedback.html',params)
        else:
            error = 'Call Is Not Closed, Please Close The Call To Continue'
            params = {'order':so,'msg':error}
            return render(request,'rating.html',params)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return render(request,'rating.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')
        
# For saving ratings
def feedback(request):
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
        obj=CallCentre.objects.filter(Service_Order=so)
        obj1=VisitDetail.objects.filter(Service_Order=so)
    
        params = {'alldata':obj,'alldata1':obj1,'r':bh,'r1':sv}
    
        rs = Rating(Service_Order=so,Name=nm,Technician=tech,Technician_Name=tname,Product=p,Work_Done=w,Behaviour=bh,Service=sv)
        rs.save()
        return render(request,'feedback.html',params)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 0:
                return render(request,'rating.html')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')

# for royalt add page
def royalty(request,so):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
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
                # defining service charge for different products
                    else:
                        if pr=='AC':
                            sc='550'
                        elif pr=='RF':
                            sc='450'
                        elif pr=='WM':
                            sc='350'
                        else:
                            sc='350'
                # definnig Parts for different products
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
        else:
            return HttpResponseRedirect('/smartcare')
    else:
        return HttpResponseRedirect('/smartcare')

# Saving royalty
def royaltysave(request):
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
        error=''
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
    
    # checking for proper inputs
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

    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return HttpResponseRedirect('/servicecentre')
            else:
                return HttpResponseRedirect('/smartcare')
        else:
            return HttpResponseRedirect('/smartcare')
    
# To view royalty
def viewroyalty(request,so):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            obj=Royalty.objects.filter(Service_Order=so)
            if obj:
                params = {'alldata':obj}
                return render(request,'royaltyshow.html',params)
            else:
                mg = 'No Records Found'
                params = {'msg':mg}
                return render(request,'errorpage.html',params)
        else:
            return HttpResponseRedirect('/servicecentre')
    else:
        return HttpResponseRedirect('/smartcare')

# for call closing
def callclose(request,so):
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
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
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
            else:
                return HttpResponseRedirect('/servicecentre')
        else:
            return HttpResponseRedirect('/smartcare')

# for reports page
def reports(request):
    if request.session.has_key('is_logged'):
        if request.session['is_logged'] == 1:
            return render(request,'reports.html')
        else:
            return HttpResponseRedirect('/servicecentre')
    else:
        return HttpResponseRedirect('/smartcare')

# to download plain summary
def plainsummery(request):
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
    
        obj1=CallCentre.objects.all()
        obj2=Details.objects.all()
        obj3=VisitDetail.objects.all()

        df1 = read_frame(obj1)
        df2 = read_frame(obj2)
        df3 = read_frame(obj3)

        dframe = [df1,df2,df3]
        df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Service_Order'],how='outer'), dframe).fillna('-')
    
        st = datetime.strptime(rdst, "%d/%m/%Y")
        strt = datetime.strftime(st, "%Y-%m-%d")
        end = datetime.strptime(rdend, "%d/%m/%Y")
        endt = datetime.strftime(end, "%Y-%m-%d")

        df_merged['Reported_Date'] = pd.to_datetime(df_merged['Reported_Date'],dayfirst=True)
       
        df_merged['Status'].replace(['Free','Blank','Pending','Closed'],[1,2,3,4],inplace=True)
        
        date_range = ((df_merged['Reported_Date'] >= strt) & (df_merged['Reported_Date'] <= endt))
        df_date_range = df_merged.loc[date_range]
       
        dfsts = df_date_range.groupby(['Cust_Type'])
        df_status = dfsts.get_group(cst)
        
        if ststo>stsfrm:
            mask = ((df_status['Status'] >= stsfrm) & (df_status['Status'] <= ststo))
            dff = df_status.loc[mask]
        else:
            mask = ((df_status['Status'] >= ststo) & (df_status['Status'] <= stsfrm))
            dff = df_status.loc[mask]
    
        dff['Status'].replace([1,2,3,4],['Free','Blank','Pending','Closed'],inplace=True)
        
        if actn == None:
            df_action = (dff)
        else:
            dfactn = (dff['Action'] == actn)
            df_action = dff.loc[dfactn]
    
        if vdet == 'on':
            df_final = df_action
        else:
            df_final = df_action[['Service_Order','Location','Reported_Date','Reported_Time','Status','First_Name','Last_Name','Fault','Address','City','Mobile_No','Pin_Code']]
        
        df_final.to_csv('file.csv',index=False)
        
        return render(request,'plainsummery.html')
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                return render(request,'plainsummery.html')
            else:
                return HttpResponseRedirect('/servicecentre')
        else:
            return HttpResponseRedirect('/smartcare')

# to download visit reports
def visitreport(request):
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
        
        obj = Technician.objects.all()
        params = {'Names':obj}

        obj1=CallCentre.objects.all()
        obj2=VisitDetail.objects.all()

        df1 = read_frame(obj1)
        df2 = read_frame(obj2)

        dframe = [df1,df2]
        df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Service_Order'],how='outer'), dframe).fillna('-')
        
        st = datetime.strptime(rdst, "%d/%m/%Y")
        strt = datetime.strftime(st, "%Y-%m-%d")
        end = datetime.strptime(rdend, "%d/%m/%Y")
        endt = datetime.strftime(end, "%Y-%m-%d")

        df_merged['Reported_Date'] = pd.to_datetime(df_merged['Reported_Date'],dayfirst=True)

        date_range = ((df_merged['Reported_Date'] >= strt) & (df_merged['Reported_Date'] <= endt))
        df_rp_date_range = df_merged.loc[date_range]
    
        df_tech = ((df_rp_date_range['Technician_Name'] == techst) | (df_merged['Technician_Name'] == techen))
        df_tech_range = df_rp_date_range.loc[df_tech]
        
        if actn == None:
            df_action = df_tech_range
        else:
            dfactn = (df_tech_range['Action'] == actn)
            df_action = df_tech_range.loc[dfactn]
     
        v_date_range = ((df_action['Visit_Date'] >= vdtst) & (df_merged['Visit_Date'] <= vdten))
        df_visitdate_range = df_action.loc[v_date_range]

        if warsts == None:
            df_final = df_visitdate_range
        else:
            df_fnl = (df_visitdate_range['Warranty'] == warsts)
            df_final = df_visitdate_range.loc[df_fnl]
        print(df_final)
        df_final.to_csv('file.csv',index=False)

        return render(request,'visitreport.html',params)
    else:
        if request.session.has_key('is_logged'):
            if request.session['is_logged'] == 1:
                obj = Technician.objects.all()
                params = {'Names':obj}
                return render(request,'visitreport.html',params)
            else:
                return HttpResponseRedirect('/servicecentre')
        else:
            return HttpResponseRedirect('/smartcare')