# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`
# The Cloud Functions for Firebase SDK to create Cloud Functions and set up triggers.
from firebase_functions import firestore_fn, https_fn

# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import json, xmltodict
import datetime

app = initialize_app()

# initialize_app()
#
#
# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello world!")

@https_fn.on_request()
def addmessage(req: https_fn.Request) -> https_fn.Response:
    """Take the text parameter passed to this HTTP endpoint and insert it into
    a new document in the messages collection."""
    # Grab the text parameter.
    original = req.args.get("text")
    if original is None:
        return https_fn.Response("No text parameter provided", status=400)

    firestore_client: google.cloud.firestore.Client = firestore.client()

    # Push the new message into Cloud Firestore using the Firebase Admin SDK.
    _, doc_ref = firestore_client.collection("messages").add(
        {"original": original}
    )

    # Send back a message that we've successfully written the message
    return https_fn.Response(f"Message with ID {doc_ref.id} added.")

@https_fn.on_request()
def xml2json(req: https_fn.Request) -> https_fn.Response:
    with open("../export.xml") as xml_file:
        xml = xml_file.read()
        data_dict = xmltodict.parse(xml)
        json_data = json.dumps(data_dict, indent = 4)
    json_read = json.loads(json_data)
    with open("data.json", "w") as json_file:
       json_file.write(json_data) 
    #print(json_read['HealthData']["Record"][0])
    # records = json_read['HealthData']["Record"]
    # Previous_Date = datetime.datetime.today() - datetime.timedelta(days=4)
    # base = datetime.datetime.today()
    # query_date = str(Previous_Date)[:10]
    # date_list = [str(base - datetime.timedelta(days=x))[:10] for x in range(7)]
    # #print(date_list)
    # for record in records:
    #     if record["@type"] == "HKQuantityTypeIdentifierRespiratoryRate" and record["@startDate"][:10] in date_list:
    #         #print("Current JSON Date: ", record["@startDate"][:10])
    #         print(record["@startDate"][:10], ": ", record["@value"]) 
   
    return https_fn.Response("Message added")


@firestore_fn.on_document_created(document="messages/{pushId}")
def makeuppercase(
    event: firestore_fn.Event[firestore_fn.DocumentSnapshot | None],
) -> None:
    """Listens for new documents to be added to /messages. If the document has
    an "original" field, creates an "uppercase" field containg the contents of
    "original" in upper case."""

    # Get the value of "original" if it exists.
    if event.data is None:
        return
    try:
        original = event.data.get("original")
    except KeyError:
        # No "original" field, so do nothing.
        return

    # Set the "uppercase" field.
    print(f"Uppercasing {event.params['pushId']}: {original}")
    upper = original.upper()
    event.data.reference.update({"uppercase": upper})