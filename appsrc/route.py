import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from libs import postgres , utils , logs
from flask import make_response
import traceback
import urllib
from uuid import uuid4
import pprint 
from appsrc import app



@app.route('/customerDetails', methods=['GET'])
def customerDetails():
    try:
        logs.logger.debug(utils.get_debug_all(request))
        #gets attributes
        received_request = request.json
        if (received_request == None):
            received_request = []
        received_args = request.args
        if ('Customer-Number' not in received_request and 'Customer-Number' not in received_args):
            return utils.returnResponse("Error, missing Customer-Number data", 404) 
        
        # gets the value of the attribute, priority is given to request.body
        CustomerNumber=""
        if ('Customer-Number' in received_request):
            CustomerNumber = received_request['Customer-Number']
        else: #must be in the request.args
            CustomerNumber = received_args['Customer-Number']
        
        # calls the functions with the proper param
        data = postgres.retrieveCustomerDetails(CustomerNumber)
        if (len(data) >= 1 ): #only sends the first entry within the array .. should have only one  ..
            return utils.returnResponse(data[0], 200)     
        # nothing was found sending back an empty result
        return utils.returnResponse({}, 200)   
        
        
    except Exception as e :
        import traceback
        traceback.print_exc()
        return utils.returnResponse("An Error Occured.", 200)        
       
@app.route('/subscribtionStatus', methods=['GET'])
def subscribtionStatus():
    try:
        logs.logger.debug(utils.get_debug_all(request))
        #gets attributes
        received_request = request.json
        if (received_request == None):
            received_request = []
        received_args = request.args
        if ('Device-Serial-Number' not in received_request and 'Device-Serial-Number' not in received_args):
            return utils.returnResponse("Error, missing Device-Serial-Number data", 404) 
        
        # gets the value of the attribute, priority is given to request.body
        DeviceSN=""
        if ('Device-Serial-Number' in received_request):
            DeviceSN = received_request['Device-Serial-Number']
        else: #must be in the request.args
            DeviceSN = received_args['Device-Serial-Number']

        # calls the functions with the proper param
        data = postgres.subscriptionStatus(DeviceSN)
        if (len(data) >= 1 ): #only sends the first entry within the array .. should have only one  ..
            return utils.returnResponse(data[0], 200)     
        # nothing was found sending back an empty result
        return utils.returnResponse({}, 200)     
        
        
    except Exception as e :
        import traceback
        traceback.print_exc()
        return utils.returnResponse("An Error Occured.", 200)                


@app.route('/customerPassions', methods=['GET'])
def customerPassions():
    try:
        logs.logger.debug(utils.get_debug_all(request))

        #gets attributes
        received_request = request.json
        if (received_request == None):
            received_request = []
        received_args = request.args
        if ('Customer-Number' not in received_request and 'Customer-Number' not in received_args):
            return utils.returnResponse("Error, missing Customer-Number data", 404) 
        if ('Current-Decade' not in received_request and 'Current-Decade' not in received_args):
            return utils.returnResponse("Error, missing Current-Decade data", 404) 

        # gets the value of the attribute, priority is given to request.body
        CustomerNumber=""
        if ('Customer-Number' in received_request):
            CustomerNumber = received_request['Customer-Number']
        else: #must be in the request.args
            CustomerNumber = received_args['Customer-Number']
        currentDecade=""
        if ('Current-Decade' in received_request):
            currentDecade = received_request['Customer-Decade']
        else: #must be in the request.args
            currentDecade = received_args['Current-Decade']


        # calls the functions with the proper param
        data = postgres.customerPassion(CustomerNumber, currentDecade)
        #ok now rework the structure as this one is different
        # waiting for some data

        if (len(data) >= 1 ): #only sends the first entry within the array .. should have only one  ..
            return utils.returnResponse(data, 200)     
        # nothing was found sending back an empty result
        return utils.returnResponse({}, 200)     
        
        
    except Exception as e :
        import traceback
        traceback.print_exc()
        return utils.returnResponse("An Error Occured.", 200)                        

@app.route('/customerOrder', methods=['GET'])
def customerOrder():
    try:
        logs.logger.debug(utils.get_debug_all(request))
        #gets attributes
        received_request = request.json
        if (received_request == None):
            received_request = []
        received_args = request.args
        if ('SF-Order-Number' not in received_request and 'SF-Order-Number' not in received_args):
            return utils.returnResponse("Error, missing SF-Order-Number data", 404) 
        
        # gets the value of the attribute, priority is given to request.body
        sfOrderNumber=""
        if ('SF-Order-Number' in received_request):
            sfOrderNumber = received_request['SF-Order-Number']
        else: #must be in the request.args
            sfOrderNumber = received_args['SF-Order-Number']
        # calls the functions with the proper param
        data = postgres.retrieveCustomerOrder(sfOrderNumber)


        if (len(data) >= 1 ): #only sends the first entry within the array .. should have only one  ..
            return utils.returnResponse(data[0], 200)     
        # nothing was found sending back an empty result
        return utils.returnResponse({}, 200)     
        
        
    except Exception as e :
        import traceback
        traceback.print_exc()
        return utils.returnResponse("An Error Occured.", 200)              
