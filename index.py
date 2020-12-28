import boto3
import logging
import os
import json
from botocore.exceptions import ClientError

sesv2 = boto3.client("sesv2")

def lambda_handler(event, context):

    global log_level
    log_level = str(os.environ.get("LOG_LEVEL")).upper()
    if log_level not in [
                            "DEBUG", "INFO",
                            "WARNING", "ERROR",
                            "CRITICAL"
                        ]:
        log_level = "ERROR"
    logging.getLogger().setLevel(log_level)

    logging.info(event)


    for record in event['Records']:
      try:
        ses_event = json.loads(json.loads(record['body'])['Message'])

        logging.info(ses_event)

        # If event is a Bounce, handle it
        if (ses_event["notificationType"] == "Bounce" and ses_event["bounce"]["bounceType"] == "Permanent" ):
            for recipient in ses_event["bounce"]["bouncedRecipients"]:
                sesv2.put_suppressed_destination(
                  EmailAddress = recipient["emailAddress"],
                  Reason = "BOUNCE"
                )
                # CUSTOMER TODO - Update customer system with Bounce status

        # If event is a spam complaint
        elif (ses_event["notificationType"] == "Complaint"):
            for recipient in ses_event["complaint"]["complainedRecipients"]:
                sesv2.put_suppressed_destination(
                  EmailAddress = recipient["emailAddress"],
                  Reason = "COMPLAINT"
                )
                # CUSTOMER TODO - Update customer system with Complaint status
      except Exception as e:
          logging.error("Received Error while processing SQS record: %s", e)
