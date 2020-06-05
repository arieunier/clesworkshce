import asyncio
import os 
from aiosfstream import SalesforceStreamingClient
from libs import logs
from libs import postgres
import uuid


LOGGER = logs.LOGGER


CONSUMER_KEY=os.environ.get('CONSUMER_KEY','')
CONSUMER_SECRET=os.environ.get('CONSUMER_SECRET','')
USERNAME=os.environ.get('USERNAME','')
PASSWORD=os.environ.get('PASSWORD','')
TOPICS=os.environ.get('TOPICS','')

async def stream_events():
    # connect to Streaming API
    async with SalesforceStreamingClient(
            sandbox=False,
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            username=USERNAME,
            password=PASSWORD) as client:

        for topic in TOPICS.split(";"):        
            LOGGER.debug("Subscribing to {}".format(topic))
            await client.subscribe(topic)
        

        # listen for incoming messages
        async for message in client:
            LOGGER.debug("Message Received => {} ".format(message))
            Current_Time__c = message["data"]["payload"]["Current_Time__c"]
            Destination_Time__c = message["data"]["payload"]["Destination_Time__c"]
            Customer_Number__c = message["data"]["payload"]["Customer_Number__c"]
            uid = uuid.uuid4().__str__()
            postgres.insertTimeTravel(uid, Current_Time__c, Destination_Time__c, Customer_Number__c)


if __name__ == "__main__":
    # checcks the db
    postgres.checkPETable()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream_events())