import imaplib
import poplib
import os
import constants
import smtplib

#from userUtils import getUserConfig, get
#import resumeUtils

from imap_tools import MailBox, AND
import userUtils 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

def sendMail(ToEmailAddr, subject, body, contentType):
    
    ToEmailAddr = 'rkanade@gmail.com' #ToEmailAddr -> done purposefully to avoid sending emails to
    
    print("Setting up SMTP server again")

    msg = MIMEMultipart()
    msg['From'] = os.environ.get("SMTP_MAIL_USERNAME")
    msg['To'] = ToEmailAddr
    msg['Subject'] = str(subject)

    msg.attach(MIMEText(body,contentType)) #'plain'

    print( msg.as_string() )

    with smtplib.SMTP(os.environ.get("SMTP_MAIL_SERVER"), os.environ.get("SMTP_MAIL_PORT")) as server:
        server.login(os.environ.get("SMTP_MAIL_USERNAME"), os.environ.get("SMTP_MAIL_PASSWORD"))
        server.sendmail(os.environ.get("SMTP_MAIL_USERNAME"), ToEmailAddr, msg.as_string())
        server.close()

    print("Mail sent successfully.")


if __name__ == "__main__":
    #processEmailsForApp(constants.APP_CODE_CAMI);
    #processEmails("rrkanade22@yahoo.com","CAMI")
    sendMail('rrkanade22@yahoo.com', "test subject", "test body",'plain')
