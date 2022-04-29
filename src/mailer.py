import os

from dotenv import load_dotenv
from pepipost.pepipost_client import PepipostClient
from pepipost.models.send import Send
from pepipost.models.mfrom import From
from pepipost.models.content import Content
from pepipost.models.type_enum import TypeEnum 
from pepipost.exceptions.api_exception import APIException
from pepipost.models.personalizations import Personalizations
from pepipost.models.email_struct import EmailStruct

load_dotenv(verbose=False)

def send_email(subject=None, content=None):
    """ Sends an email using the Pepipost API
    """

    client = PepipostClient(os.getenv("API_KEY"))

    mail_send_controller = client.mail_send 

    body = Send()
    body.mfrom = From()
    body.mfrom.email = os.getenv("FROM_EMAIL")
    body.mfrom.name = os.getenv("FROM_NAME")
    body.subject = subject

    body.content = []
    body.content.append(Content())
    body.content[0].mtype = TypeEnum.HTML
    body.content[0].value = content

    body.personalizations = []
    body.personalizations.append(Personalizations())
    body.personalizations[0].to = []
    body.personalizations[0].to.append(EmailStruct())
    body.personalizations[0].to[0].name = os.getenv("TO_NAME")
    body.personalizations[0].to[0].email = os.getenv("TO_EMAIL")

    print("=' * 50")
    print(body)
    try:
        result = mail_send_controller.create_generatethemailsendrequest(body)
        print(f"Email sent successfully:\n{result}")
    except APIException as e:
        print(f"Failed to send email:\n{e}")

