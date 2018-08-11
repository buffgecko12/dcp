from django.core.mail import send_mail

def send_email(subject, body, to_list, sender = None):
    try:
        if(to_list):
            send_mail(subject, body, sender, to_list)
    except Exception as e:
        print("ERROR - Could not send e-mail(s) - ", e)

    return