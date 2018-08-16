from django.core.mail import EmailMessage
from django.conf import settings

def send_email(subject, body, to_list, bccflag = None, sender = None):

    # Set bccflag = False (if not specified and only one person in to_list)
    if(not bccflag and len(to_list) == 1):
        bccflag = False
    else:
        bccflag = True
    
    try:
        if(to_list):
            msg = EmailMessage(
                subject=subject, 
                body=body, 
                from_email=sender,
                to=to_list if not bccflag else [settings.DEFAULT_FROM_EMAIL,],
                bcc=to_list if bccflag else None
            )
        
            msg.send()

    except Exception as e:
        print("ERROR - Could not send e-mail(s) - ", e)

    return