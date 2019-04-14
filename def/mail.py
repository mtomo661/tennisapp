# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

from_address  = 'mtomo661@ntv.co.jp'
to_address    = 'mtomo661@ntv.co.jp'

# 本文
msg = MIMEText( "Hello!!" )

# 件名、宛先
msg['Subject'] = 'Mail sending test.'
msg['From']    = from_address
msg['To']      = to_address

# Send the message via our own SMTP server, but don't include the envelope header.
s = smtplib.SMTP("smtp.gmail.com", 587)
s.connect()
s.sendmail( me, [you], msg.as_string() )
s.close()
