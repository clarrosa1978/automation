#!/bin/bash

receiver_email="fernando.letona@coto.com.ar"
subject="[slnxansible | Healthcheck] "
body="Please find the attachment."
attachment_path="/tecnol/healthcheck/results/salida_final.txt"
smtp_server="relayinterno.redcoto.com.ar"
smtp_port="25"

email_body=$(mktemp)
echo -e "Subject: $subject\n\n$body" > "$email_body"
mailx -s "$subject" -a "$attachment_path" -r "root@slnxansible.redcoto.com.ar" "$receiver_email" < "$email_body"
rm "$email_body"
