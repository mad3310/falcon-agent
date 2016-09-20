#coding=utf-8
import os
import re
import logging
import time
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email.utils import formatdate
import hashlib
from tornado.gen import Task
from datetime import datetime
from mail_session import SMTPSession
from tornado.escape import utf8
from tornado.ioloop import PeriodicCallback

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# borrow email re pattern from django
_email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain

class EmailAddress(object):
    def __init__(self, addr, name=""):
        assert _email_re.match(addr), "Email address(%s) is invalid." % addr

        self.addr = addr
        if name:
            self.name = name
        else:
            self.name = addr.split("@")[0]

    def __str__(self):
        return '%s <%s>' % (utf8(self.name), utf8(self.addr))

class MailEgine(object):
    
    def __init__(self):
        #including the md5 sum of mail content
        self.mails = {}
        self.session = SMTPSession

    def egine_fire_start(self, host, port, user='',
                        password='', duration=30,
                        tls=False, interval = 600):
        self.interval = interval
        self.session.connect(host, port, user,
                        password, duration, tls)

    def _mail_address_filter(self, mailfrom, to):
        if isinstance(mailfrom, EmailAddress):
            mailfrom = str(mailfrom)
        else:
            mailfrom = utf8(mailfrom)
        to = [utf8(t) for t in to]
        mtlist = []
        for mail in to:
            for t in re.split(';|,', mail):
                mtlist.append(t)
        mailto = []
        for mt in mtlist:
            if re.match('\S*\s*<\s*\S+@\S+\.\S+>', mt):
                mailto.append(mt)
        return mailfrom, mailto

    def _mail_attachment(self, outer, filenames):
        filename_list = filenames.split(',')
        for filename in filename_list:
            file_part = MIMEText(open(filename,'rb').read())
            file_part.add_header('Content-Disposition',
                    'attachment',filename=filename)
            outer.attach(file_part)

    def mail_report(self, mailfrom, to, subject, body,
          md5_value = None, attachments = [], html = None):
        if html:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(body, "plain"))
            message.attach(MIMEText(html, "html"))
        else:
            message = MIMEText(body)
        if attachments:
            part = message
            message = MIMEMultipart("mixed")
            message.attach(part)
            for filename, data in attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(data)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment",
                    filename=filename)
                message.attach(part)
    
        message["Date"] = formatdate(time.time())
        message["From"] = mailfrom
        message["To"] = COMMASPACE.join(to)
        if md5_value:
            message["Subject"] = '%s_%s' %(md5_value[0:5],
                                    utf8(subject))
        else:
            message["Subject"] = utf8(subject)
        return message 

    def _mail_md5(self, mailfrom, to, subject, content):
        src = '%s%s%s%s' %(mailfrom, to, subject, content)
        myMd5 = hashlib.md5()
        myMd5.update(src)
        return myMd5.hexdigest()

    def _mail_record(self, md5_value, mailfrom,
                    to, subject):
        if not self.mails.has_key(md5_value):
            self.mails[md5_value] = dict(
                mailfrom = mailfrom,
                to = to,
                subject = subject)
        now = datetime.now()
        self.mails[md5_value].update(
              dict(sendtime = now.strftime(TIME_FORMAT)))

    def _mail_record_renew(self, md5_value):
        if self.mails.has_key(md5_value):
            now = datetime.now()
            self.mails[md5_value].update(
              dict(sendtime = now.strftime(TIME_FORMAT)))

    def _should_send(self, md5_value):
        now = datetime.now()
        if self.mails.has_key(md5_value):
            last_time = self.mails[md5_value]['sendtime']
            time_pass = now - datetime.strptime(
                            last_time, TIME_FORMAT)
            return time_pass.seconds > self.interval
        return True

    def _send(self, fr, to, message):
        self.session.send_mail(fr, to, utf8(message.as_string()))

    def send_exception_email(self, mailfrom, to, subject, body,
                    html=None, attachments=[]):
        fr, mailto = self._mail_address_filter(mailfrom, to)
        md5_value = self._mail_md5(mailfrom, to, subject, body)
        if not self._should_send(md5_value):
            logging.info(('too much email from %s to %s,'
                         'subject:%s, body md5:%s')
                    %(mailfrom, mailto, subject, md5_value))
            self._mail_record_renew(md5_value)
            return False 

        message = self.mail_report(mailfrom, to, subject, body,
                                md5_value, attachments, html)
        try:
            logging.info(('send email from %s to %s succeed,'
                           'subject:%s, mail body is:\n%s')
                           %(mailfrom, to, subject, body))
            self._send(fr, mailto, message)
            self._mail_record(md5_value, mailfrom, to, subject)
        except Exception as e:
            logging.error(('send email from %s to %s failed,'
                           'subject:%s, mail body is:\n%s')
                           %(mailfrom, to, subject, body))
            logging.debug(e, exc_info = True)
        return True 

    def send_normal_email(self, mailfrom, to, subject, body,
                    html=None, attachments=[]):
        fr, mailto = self._mail_address_filter(mailfrom, to)
        message = self.mail_report(mailfrom, to, subject, body,
                                md5_value = None,
                                attachments = attachments,
                                html = html)
        self._send(fr, mailto, message)

    def _ok_mail_build(self):
        now = datetime.now()
        for md5_value in self.mails.keys():
            last_time = self.mails[md5_value]['sendtime']
            timepass = now - datetime.strptime(last_time,
                                        TIME_FORMAT)
            #print timepass.seconds
            if timepass.seconds < self.interval:
                continue
            mail_dict = self.mails[md5_value]
            mailfrom = mail_dict['mailfrom']
            to = mail_dict['to']
            subject = 'OK--%s' %mail_dict['subject']
            body = 'DONOT WORRY'
            fr, mailto = self._mail_address_filter(mailfrom, to)
            yield dict(md5_value = md5_value,
                       mailfrom = fr,
                       mailto = mailto,
                       email = self.mail_report(mailfrom, mailto,
                                      subject, body, md5_value))
    
    def mail_scan_work(self):
        self._ok_mail_send()

    def _ok_mail_send(self):
        for mails in self._ok_mail_build():
            try:
                self._send(mails['mailfrom'],
                        mails['mailto'],
                        mails['email'])
                del self.mails[mails['md5_value']]
            except Exception as e:
                logging.info('send OK email failed, md5:%s',
                             mails['md5_value'])
                logging.debug(e, exc_info=True)

MailEgine = MailEgine()

if __name__ == '__main__':
    import time
    smtp_host = '10.205.91.22'
    smtp_port = 587
    smtp_user = 'mcluster'
    smtp_passwd = 'Mcl_20140903!'
    mailfrom = 'mcluster@letv.com'
    to = ['liujinliu <liujinliu@le.com>']
    subject = 'test mail'
    body = 'This is just a Test'
    body2 = 'This is another test'
    MailEgine.egine_fire_start(smtp_host, smtp_port,
                    smtp_user, smtp_passwd, interval=60)
    MailEgine.send_exception_email(mailfrom, to, subject, body)
    time.sleep(30)
    print '=========='
    MailEgine.send_exception_email(mailfrom, to, subject, body)
    print MailEgine.mails
    print '====normal mail===='
    MailEgine.send_normal_email(mailfrom, to, subject, body)
    print MailEgine.mails
    time.sleep(120)
    MailEgine.send_exception_email(mailfrom, to, subject, body)
    while True:
        #print "wait to sending ok email"
        MailEgine.mail_scan_work()
        time.sleep(10)

