import boto3
import json
import os
from db import Database
from queries import get_employee_email

sqs = boto3.client("sqs")
ses = boto3.client("ses")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
db = Database()

def process_notifications():
    response = sqs.receive_message(QueueUrl=SQS_QUEUE_URL, MaxNumberOfMessages=10)

    if 'Messages' in response:
        for msg in response['Messages']:
            data = json.loads(msg['Body'])
            manager_id = data['manager_id']
            dashboard_id = data['dashboard_id']

            # Get manager email
            conn = db.get_connection()
            with conn.cursor() as cur:
                cur.execute(get_employee_email, (manager_id,))
                name, email = cur.fetchone()

            # Send email via SES
            ses.send_email(
                Source="myemail@example.com",
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": "Dashboard Shared with You"},
                    "Body": {
                        "Text": {
                            "Data": f"Hi {name}, a new dashboard has been shared with you."
                        }
                    }
                }
            )
            print(f"Notified {email} about dashboard {dashboard_id}")

            # Delete message from SQS
            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )

process_notifications()