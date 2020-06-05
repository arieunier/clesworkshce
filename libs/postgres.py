from libs import variables, logs
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
MANUAL_ENGINE_POSTGRES = create_engine(variables.DATABASE_URL, pool_size=30, max_overflow=0)
Base.metadata.bind = MANUAL_ENGINE_POSTGRES
dbSession_postgres = sessionmaker(bind=MANUAL_ENGINE_POSTGRES)
session_postgres = dbSession_postgres()


# init platform event table

def insertTimeTravel(uid_, CurrentTime, DestinationTime,Customer_Number__c):
    sqlRequest = """
        insert into public.time_travel(id, "Current_Time", "Destination_Time", "Customer_Number") values (%(id)s, %(CurrentTime)s,  %(DestinationTime)s, %(Customer_Number__c)s)
    """
    MANUAL_ENGINE_POSTGRES.execute(sqlRequest, {'id':uid_,
            'CurrentTime':CurrentTime,'DestinationTime':DestinationTime , 'Customer_Number__c':Customer_Number__c})

def initPETable():
    try:
        sqlRequest = """        
        create table public.time_travel(
        Id varchar(36) not null primary key,
        "Current_Time" varchar(20) not null,
        "Destination_Time" varchar(20) not null,
        "Customer_Number" varchar(32) not null);       
        """
        result = MANUAL_ENGINE_POSTGRES.execute(sqlRequest, {})
        
    except Exception as e:
        import traceback
        traceback.print_exc()

def checkPETable():
    try:
        sqlRequest = "select count(*) from public.time_travel"
        result = __execRequest(sqlRequest, None)
        #if we go there, it means the table exist !
    except Exception as e:
        #if we go there, it means the table does not exist and we have to create it
        import traceback
        traceback.print_exc()
        initPETable()


def __resultToDict(result):
    arrayData =  []
    column_names = [desc[0] for desc in result.cursor.description]

    for entry in result:
        resDic = {}
        for column in column_names:
            resDic[column] = entry[column]
        arrayData.append(resDic)
    
    return arrayData
    #return {'data' : arrayData, 'columns': column_names}

def __execRequest(strReq, Attributes):
    if (MANUAL_ENGINE_POSTGRES != None):
        result = MANUAL_ENGINE_POSTGRES.execute(strReq, Attributes)
        return __resultToDict(result)
    return {'data' : [], "columns": []}

#Retreive customer details
def retrieveCustomerDetails(accountnumber):
    sqlRequest = """
    select 
        a.id as "Customer-Id", 
        a.Name as "Customer-Name", 
        a.BillingStreet as  "Customer-Address-Street", 
        a.BillingCity as "Customer_Address-City",
        a.BillingPostalCode as "Customer-Address-PostCode", 
        a.BillingCountry as "Customer-Address-Country", 
        to_char(a.personbirthdate, 'YYYY-MM-DD')  as "Customer-Date-Of-Birth"
        from salesforce.account a 
        where a.AccountNumber =  %(accountnumber)s
    """

    data = __execRequest(sqlRequest, {'accountnumber':accountnumber})
    #for some reasons Postgres does not accept alias with -
    return data

#subscription status
def subscriptionStatus(deviceSerialNumber):
    sqlRequest = """
    select 
        sub.name as "Subscription-Type",
        sub.License_status__c as "Subscription-Status",
        to_char(sub.valid_from__c, 'YYYY-MM-DD') as "Subscription-Valid__From",
        to_char(sub.valid_till__c, 'YYYY-MM-DD') as "Subscription-Valid__Till"
        from salesforce.subscription__c sub, salesforce.asset ass 
        where (sub.asset__c = ass.sfid and ass.serialnumber=%(deviceSerialNumber)s)
    """
    data = __execRequest(sqlRequest, {'deviceSerialNumber':deviceSerialNumber})
    #for some reasons Postgres does not accept alias with -
    return data    

#customerPassion
def customerPassion(accountNumber, decade):
    sqlRequest = """
    WITH getContactId as (
        select con.sfid as conId
        from salesforce.contact con, salesforce.account acc
        where con.accountId=acc.sfid and acc.accountnumber=%(accountNumber)s
        )
    select pass.name, pass.decade__c, pass.passion__c
    from salesforce.passion__c pass 
    where 
        pass.contact__c = (select conId from getContactId) 
        and pass.decade__c=%(decade)s
 
    """
    data = __execRequest(sqlRequest, {'accountNumber':accountNumber,'decade':decade})
    # ok work on the data
    Passion = {}
    for entry in data:
        if (entry['name'] in Passion) : #already added
            Passion[entry['name']].append(entry['passion__c'])
        else: #new
            Passion[entry['name']] =  []
            Passion[entry['name']].append(entry['passion__c'])
    result = {'Customer-Passions': {"Passion" : Passion}}
    return result   

def retrieveCustomerOrder(orderNumber):
    sqlRequestMaster="""
           WITH getAccountId as (
                select 
                        ord.accountId as "SF-Customer-Id",
                        ord.OrderNumber as "SF-Order-Number",
                        to_char(ord.PoDate, 'YYYY-MM-DD')  as "SF-Order-Header-Date",
                        ord.CurrencyIsoCode as "SF-Order-Header-Currency",
                        ord.TotalAmount as "SF-Order-Header-Net-Value",
                        ord.Type as "SF-Order-Header-Type",
                        ord.sfid as "Order-Id"
                from salesforce.order ord
                where ord.ordernumber=%(orderNumber)s
                )
            select acc.Name as "SF-Order-Header-Customer-Name", 
                    acc.Id__c as "SF-Customer-Id",
                    ---acc.sfid,
                    acc.personemail as "SF-Order-Header-Customer-email",
                    acc.personmobilephone as "SF-Order-Header-Customer-Mobile",
                    acc.BillingStreet as "SF-Order-Header-Billing-Address",
                    acc.BillingCity as "SF-Order-Header-Billing-City",
                    acc.BillingPostalCode as "SF-Order-Header-Billing-Postcode",
                    acc.BillingCountry as "SF-Order-Header-Billing-Country",
                    acc.ShippingStreet as "SF-Order-Header-Shipping-Address",
                    acc.ShippingCity as "SF-Order-Header-Shipping-City",
                    acc.ShippingPostalCode as "SF-Order-Header-Shipping-Postcode",
                    acc.ShippingCountry as "SF-Order-Header-Shipping-Country",
                    getAcc.* 
            from salesforce.account acc, getAccountId getAcc
            where acc.sfid = (select "SF-Customer-Id" from getAccountId)
        """    
    sqlRequestSlave="""
        select
            orditem.order_line_number__c as "SAP-Order-Item-and-Schedule-Number",
            ---orditem.issued_serial_number__c as "SF-Order-Item-Serial-Number",
            prod.productcode as "SF-Order-Item-Product-Number",
            orditem.quantity as "SF-Order-Item-Quantity",
            prod.quantityunitofmeasure as "SF-Order-Item-Unit",
            orditem.unitprice as "SF-Order-Item-Value",
            orditem.description as "SF-Order-Item-Description"
        from 
                salesforce.order ord,
                salesforce.orderitem orditem,
                salesforce.product2 prod
        where
                ord.ordernumber=%(orderNumber)s and
                orditem.orderid=ord.sfid and
                prod.sfid=orditem.product2id
        """
    dataMaster = __execRequest(sqlRequestMaster, {'orderNumber':orderNumber})
    dataSlave = __execRequest(sqlRequestSlave, {'orderNumber':orderNumber})


    #need to add the slave part to the master paet
    SFOrderLines=[]
    for entry in dataSlave:
        SFOrderLines.append({'OrderItem':entry})
    dataMaster[0]['SF-Order-Lines'] = SFOrderLines

    return dataMaster