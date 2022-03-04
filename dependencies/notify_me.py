import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def notify_me(mailto, subject, body, mode='plain'):
    """
    This function sends an email FROM A HOTMAIL ADDRESS to any email address.
    To allow the email sending from you hotmail account, you have to validate
    it, if you get an error please chech your inbox
    
    Parameters
    ----------
    subject : str
        Email subject.
    body : str
        Email body.
    mailto : str
        Receiver's email address.
    mode : str
        Mail sending mode: plain or html

    Returns
    ----------
        None.

    """
    # ================================================== ERROR CHECK ================================================= #
    if type(subject) != str:
        raise ValueError("Parameter subject must be of type str")
    if type(body) != str:
        raise ValueError("Parameter body must be of type str")
    if type(mailto) != str:
        raise ValueError("Parameter mailto must be of type str")
    if mode not in ("plain", "html"):
        raise ValueError("Unknown mail sending mode. Only 'plain' and 'html' modes available")
    
    # ============================================ VARIABLE INITIALIZATION =========================================== #
    mailfrom = "medusa_py@hotmail.com"  # Mail created ad-hoc for this purpose only
    password = "1234abcd1234abcd"       # Ultra high secure password
    host = "smtp-mail.outlook.com"

    # =============================================== MAIL SENDING =================================================== #
    # SMTP connection
    server = smtplib.SMTP(host, 587, "YOUR_USERNAME", timeout=120)
    server.starttls()
    server.login(mailfrom, password)
    # Message creation
    msg = MIMEMultipart()
    msg['From'] = mailfrom
    msg['To'] = mailto
    msg['Subject'] = subject
    body = body.replace('\xa0', ' ') # Non -break spaces are provoking mail to truncate. Replace them by normal spaces
    msg.attach(MIMEText(body, mode))
    # Email sending
    server.sendmail(
      mailfrom, 
      mailto, 
      msg.as_string())
    # Connection closing    print(H)
    server.quit()