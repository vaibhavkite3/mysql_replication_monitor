#!/usr/bin/python3
#######################################
# Script to Monitor MySQL Replication #
# Alerts notification via email       #
#######################################

import os  
import shlex
import string
import subprocess
import sys
import socket
import json
import logging
import pprint
import time
from datetime import datetime,date,timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



#********************Configure Logging********************
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logDir = os.path.dirname(os.path.realpath(__file__)) + '/logs'
# create log directory if not already exists
if not os.path.exists(logDir):
    os.makedirs(logDir)

logFile = logDir + '/mysql_replication_monitor_' + datetime.now().strftime ("%Y%m%d") + '.log'
# create a file handler
handler = logging.FileHandler(logFile)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)
#**********************Logging configured**********************

#**********************Check if the setting file exists and read**********************
settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
if not os.path.exists(settings_file):
    logger.error('Cannot find the settings file')
    sys.exit(1)

with open(settings_file) as data_file:
    try:
        settings_data = json.load(data_file)
    except:
        logger.error('Cannot parse and load settings from the settings file')
        sys.exit(2)
#**********************Check if the setting file exists and read done**********************

#**********************function to execute command and return output or error**********************
def runCmd(cmd):
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    out, err = proc.communicate()
    ret = proc.returncode
    return (ret, out, err)
#**********************function to execute command and return output or error done**********************

#**********************Email Sending Function**********************
def send_email(recipients,message,subject):
    msg = MIMEMultipart()
    msg['From'] = settings_data["EMAIL_FROM"]
    msg['To'] = recipients
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))

    try:
        mailserver = smtplib.SMTP(settings_data["SMTP_SERVER"], settings_data["SMTP_PORT"])
        if(settings_data["SMTP_STARTTLS"]) == "true":
            mailserver.starttls()

        mailserver.ehlo()
        if(settings_data["SMTP_AUTH"]) == "true":
            mailserver.login(settings_data["SMTP_USERNAME"], settings_data["SMTP_PASSWORD"])

        try:
            mailserver.sendmail(msg['From'],recipients.split(','),msg.as_string())
            return True
        finally:
            mailserver.quit()        
    except Exception as e:
        logger.error("Unable to send email. Please check settings, ERROR : %s" % e)
        return False

#************************End of Email Sending*************************

email_recipients = ''
# Create a string of email IDs for sending alerts
for email in settings_data["EMAILS_ALERTS_TO"]:
    if email_recipients == '':
        email_recipients = email
    else:
        email_recipients = email_recipients + ',' + email

################### Main() ######################

# execute command to get slave status from mysql
mysql_repl_check_cmd = '/usr/bin/mysql' + ' -h' + settings_data['MYSQL_HOST'] + ' -P' + settings_data['MYSQL_PORT'] + ' -u' + settings_data['MYSQL_USER'] + ' -p' + settings_data['MYSQL_PASS'] + ' -e "SHOW SLAVE STATUS\\G"'
returnCode, stdOut, stdErr = runCmd(mysql_repl_check_cmd)

if returnCode:
        logger.error("There was an error in connecting MySQL / executing MySQL command %s" % stdErr)

# save the result in variable 
slaveStatusList = stdOut.decode("utf-8").split('\n')

# remove the first and last item of the list
del slaveStatusList[0]
del slaveStatusList[-1]

# put data into dictionary
slaveStatusDict={}
for i in slaveStatusList:
        slaveStatusDict[i.split(':')[0].strip()] = i.split(':')[1].strip()

# check and validate below parameters
# Slave_IO_Running , Slave_SQL_Running , Last_Errno
if (slaveStatusDict["Slave_IO_Running"] == "Yes" and slaveStatusDict["Slave_SQL_Running"] == "Yes" and slaveStatusDict["Last_Errno"] == "0"):
        logger.info("Replication is working")
        #logger.info(pprint.pformat(slaveStatusDict))

        # Check if Replication is working BUT its behind master
        if (int(slaveStatusDict["Seconds_Behind_Master"]) > int(settings_data["SECOND_BEHIND_MASTER_THREASHOLD"]) ):
                logger.info("Replication is behind master")
                # Send Email alert
                email_alert_body = ''
                email_alert_body = "<html><body><h3>MySQL replication is behind master by <b>" + slaveStatusDict["Seconds_Behind_Master"] + "</b> seconds which is more than threashold value, Please check. </h3>" + "<br><br>" + "<h5>Detail replication slave status :</h5>" + "<br><br><p>" + pprint.pformat(slaveStatusDict) + "</p></body></html>"
                email_subject =  'Alert from ' + socket.gethostname() + ' MySQL Replication problem !!!'
                if email_recipients != '':        
                    if send_email(email_recipients, email_alert_body, email_subject):
                        logger.info("Email Sent to :" + email_recipients)
                else:
                    logger.error("Failed to send Email")     
else:
        logger.info("Replication is NOT working")
        # Send Email alert
        email_alert_body = ''
        email_alert_body = "<html><body><h3>MySQL replication is <b>NOT</b> working , please check </h3>" + "<br><br>" + "<h5>Detail replication slave status :</h5>" + "<br><br><p>" + pprint.pformat(slaveStatusDict) + "</p></body></html>"
        email_subject =  'Alert from ' + socket.gethostname() + ' MySQL Replication problem !!!'
        if email_recipients != '':        
            if send_email(email_recipients, email_alert_body, email_subject):
                logger.info("Email Sent to :" + email_recipients)
            else:
                logger.error("Failed to send Email")
