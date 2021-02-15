
# MySQL Replication Monitor

### Features

- Support MySQL database server replication;
- Email alerts if anomaly in replication ;
- Alert if replication running behind ;
- No external python modules required;
- Remote mysql server replication monitoring available;



###Pre-requisite


####Python3

`$ apt install python3`

####Cron expression  (e.g. every 1 hour)

Configure a cron to execute this script at required interval.

                    
###Configuration file details (settings.json)
                    
Key  | Values | Example
------------- | ------------- | -------------
MYSQL_HOST  | Hostname or IP address of MySQL Server | 127.0.0.1
MYSQL_PORT  | MySQL Server PORT | 3306
MYSQL_USER | MySQL authentication username  | root
MYSQL_PASS | MySQL authentication password | root
SECOND_BEHIND_MASTER_THREASHOLD | Seconds upto mysql replication delay allowed | 900
EMAIL_ALERTS | To enable OR disable email alerts | true / false
EMAIL_FROM | emails  address appear to be received from | alerts@example.com
SMTP_SERVER | SMTP server address or IP | smtp.google.com
SMTP_PORT | SMTP server PORT | 587 / 25
SMTP_AUTH | IF authentication to SMTP server required | true / false
SMTP_USERNAME | SMTP authentication username | smtpadmin
SMTP_PASSWORD | SMTP authentication password | smtppassword
SMTP_STARTTLS | STARTTLS flag required | true / false
EMAILS_ALERTS_TO | Array of email address to alert to be sent | ["user1@example.com","user5@example.com"]

mysql_replication_monitor
