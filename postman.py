#!/usr/bin/env python3

import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os
import smtplib

import requests


def send_mail(to, fro, subject, text, files=None, server='localhost'):
    if files is None:
        files = []
    assert type(to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = ', '.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                        % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    args = parser.parse_args()
    messages = requests.get('http://{}/'.format(args.host)).json()
    for message in messages:
        send_mail(message['rcpt_tos'], message['mail_from'], message['subject'], message['body'])


if __name__ == '__main__':
    main()
