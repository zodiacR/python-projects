#!/usr/bin/python
#-*-encoding: utf-8 -*-
import imapclient
import email
import sys
from email.header import make_header, decode_header
import smtplib
from email.mime.text import MIMEText
import getpass

# Setting infomation about imap
server = "imap.example.com"
username = raw_input("User>>")
passwd = getpass.getpass("Passwd>>")

server_conn = imapclient.IMAPClient(server, ssl=True)
print "Attempting to connect example server...."

try:
	print "Login in...."
	server_conn.login(username, passwd)
except server_conn.Error, e:
	print e
	sys.exit(1)
else:
	# Pick up unseen emails
	print "Select 'INBOX'"
	server_conn.select_folder("INBOX")
	result = server_conn.search("UNSEEN")
	print "Dowdloading...."
	# Don't change the email status flag
	mail_list = server_conn.fetch(result, ["BODY.PEEK[]"])

	# Parse the email
	for message_id, message in mail_list.iteritems():
		e = email.message_from_string(message["BODY[]"])
		
		# Encode header acording to special encoding
		try:
			SUBJECT =  unicode(make_header(decode_header(e['Subject'])))
		except UnicodeDecodeError:
			origin = decode_header(e["Subject"])
			SUBJECT = unicode(make_header([(origin[0][0],'gbk')]))
		FROM = unicode(make_header(decode_header(e['From'])))

		content_type =  e.get_content_maintype()

		# Parse mail body
		if content_type == "multipart":
			for part in e.get_payload():
				if part.get_content_maintype() == "text":
					msg = part.get_payload(decode=True).strip()

		elif content_type == "text":
			msg = part.get_payload(decode=True).strip()
		
		print "Read(r) it or forward(f) to example mail?"
		choice = raw_input(">>")
		choice = choice.lower()
		
		if choice == "r":
			fp = open("./mail1.txt", "ab")
			fp.write(msg)
			print "Done."

		# Forwarding email to someone
		elif choice == "f":
			sendto = "example@example.com"
			server_send = "smtp.example.com"
			msg = MIMEText(msg, _subtype="html",_charset="utf-8")
			msg["Subject"] = SUBJECT
			msg["From"] = FROM
			msg["To"] = sendto
			try:
				s_server = smtplib.SMTP_SSL(server_send)
			except smtplib.SMTPConnectError:
				print "Connection error!"		
				sys.exit(2)

			try:
				s_server.login(username, passwd)
			except smtplib.SMTPAuthenticationError:
				print "Authentication failed!"
				sys.exit(2)
			else:
				s_server.sendmail(username, sendto, msg.as_string())
				print "Sent to %s" % sendto
			finally:
				s_server.quit()

finally:
	server_conn.logout()
