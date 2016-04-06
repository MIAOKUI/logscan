import smtplib

sender = 'miaokui1231@gmail.com'
receivers = ['miaokui1231@gmail.com']

message = 'testing python smtplib package'

try:
    smtpobj = smtplib.SMTP('smtp.gmail.com',587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.login('miaokui1231@gmail.com', 'MK@bj026831')
    smtpobj.sendmail(sender, receivers, message)
    print("Successfully sent email")
except:
    print("Error")