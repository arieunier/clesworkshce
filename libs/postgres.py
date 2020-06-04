from libs import variables, logs
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
MANUAL_ENGINE_POSTGRES = create_engine(variables.DATABASE_URL, pool_size=30, max_overflow=0)
Base.metadata.bind = MANUAL_ENGINE_POSTGRES
dbSession_postgres = sessionmaker(bind=MANUAL_ENGINE_POSTGRES)
session_postgres = dbSession_postgres()

      
def __resultToDict(result):
    arrayData =  []
    column_names = [desc[0] for desc in result.cursor.description]

    for entry in result:
        resDic = {}
        for column in column_names:
            resDic[column.replace('___','-')] = entry[column]
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
        a.id as "Customer___Id", 
        a.Name as "Customer___Name", 
        a.BillingStreet as  "Customer___Address___Street", 
        a.BillingCity as "Customer_Address___City",
        a.BillingPostalCode as "Customer___Address___PostCode", 
        a.BillingCountry as "Customer___Address___Country", 
        a.personbirthdate as "Customer___Date___Of___Birth"
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
        sub.name as "Subscription___Type",
        sub.License_status__c as "Subscription___Status",
        sub.valid_from__c as "Subscription___Valid__From",
        sub.valid_till__c as "Subscription___Valid__Till"
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
                        ord.accountId as "SF___Customer___Id",
                        ord.OrderNumber as "SF___Order___Number",
                        ord.PoDate as "SF___Order___Header___Date",
                        ord.TotalAmount as "SF___Order___Header___Currency",
                        ord.TotalAmount as "SF___Order___Header___Net___Value",
                        ord.Type as "SF___Order___Header___Type",
                        ord.sfid as "Order___Id"
                from salesforce.order ord
                where ord.ordernumber=%(orderNumber)s
                )
            select acc.Name as "SF___Order___Header___Customer___Name", 
                    acc.Id__c as "SF___Customer___Id",
                    ---acc.sfid,
                    acc.personemail as "SF___Order___Header___Customer___email",
                    acc.personmobilephone as "SF___Order___Header___Customer___Mobile",
                    acc.BillingStreet as "SF___Order___Header___Billing___Address",
                    acc.BillingCity as "SF___Order___Header___Billing___City",
                    acc.BillingPostalCode as "SF___Order___Header___Billing___Postcode",
                    acc.BillingCountry as "SF___Order___Header___Billing___Country",
                    acc.ShippingStreet as "SF___Order___Header___Shipping___Address",
                    acc.ShippingCity as "SF___Order___Header___Shipping___City",
                    acc.ShippingPostalCode as "SF___Order___Header___Shipping___Postcode",
                    acc.ShippingCountry as "SF___Order___Header___Shipping___Country",
                    getAcc.* 
            from salesforce.account acc, getAccountId getAcc
            where acc.sfid = (select "SF___Customer___Id" from getAccountId)
        """    
    sqlRequestSlave="""
        select
            orditem.order_line_number__c as "SAP___Order___Item___and___Schedule___Number",
            ---orditem.issued_serial_number__c as "SF___Order___Item___Serial___Number",
            prod.productcode as "SF___Order___Item___Product___Number",
            orditem.quantity as "SF___Order___Item___Quantity",
            prod.quantityunitofmeasure as "SF___Order___Item___Unit",
            orditem.unitprice as "SF___Order___Item___Value",
            orditem.description as "SF___Order___Item___Description"
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
    print("NbResult={}".format(len(dataMaster)))
    #logs.logger.info("dataMaster={}".format(dataMaster))
    dataSlave = __execRequest(sqlRequestSlave, {'orderNumber':orderNumber})
    print("NbResult={}".format(len(dataSlave)))
    #logs.logger.info("dataSlave={}".format(dataSlave))


    #need to add the slave part to the master paet
    SFOrderLines=[]
    for entry in dataSlave:
        SFOrderLines.append({'OrderItem':entry})
    dataMaster[0]['SF-Order-Lines'] = SFOrderLines

    return dataMaster