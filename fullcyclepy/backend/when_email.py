'''send email'''
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from helpers.queuehelper import QueueName
from fcmapp import Component

EMAIL = Component('email')

def when_email(channel, method, properties, body):
    '''when email event is raised'''
    try:
        doemail(body)
    except Exception as ex:
        EMAIL.app.logexception(ex)

def doemail(msg):
    '''sends the email'''
    melogin = EMAIL.app.readlogin('emaillogin.conf')
    sendtoemailfile = EMAIL.app.readlogin('emailsendto.conf')
    meuser = melogin.username
    you = sendtoemailfile.username
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Mining Summary"
    msg['From'] = meuser
    msg['To'] = you
    text = "Daily Summary\nLine2\n"
    html = """\
    <html>
      <head></head>
      <body>
        <p>Daily Summary<br>
           Line2<br>
           
        </p>
      </body>
    </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(melogin.username, melogin.password)
    mail.sendmail(meuser, you, msg.as_string())
    mail.quit()

    print('email sent')

def main():
    EMAIL.listeningqueue = EMAIL.app.subscribe_and_listen(QueueName.Q_EMAIL, when_email)

if __name__ == "__main__":
    main()
