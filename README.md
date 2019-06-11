PostOffice
=======

PostOffice is intended to act as a way to handle sending emails from a server
completely separate from the backend in a way that is not hard to configure and
use (as postfix and sendmail are hardly that).

PostOffice itself is split into three parts:
* PostOffice (smtpd.py)
* PostMaster (server.py)
* PostMan (postman.py)

Loosely, how this works is that your backend software, such as Gazelle, uses
a native send email function (such as PHP's [mail](https://www.php.net/manual/en/function.mail.php))
and then the backend uses something like [nullmailer](https://untroubled.org/nullmailer/)
to send it to the IP/Port of the PostOffice, which then logs the email. The
PostMaster is setup on the same machine as PostOffice which launches an
internet accessible endpoint which when requested, returns a list of currently
waiting emails to be sent. The PostMan then is run on a separate server and
makes calls to the web route that directs to PostMaster and then does
the actual delivery of email. The headers of the email then only contain
the IP address of PostMan, and nothing about the upstream.

All components are written targetting Python 3.5+.

## PostOffice (smtpd.py)

### Requirements
* aiosmtpd
* mail-parser

### Usage
PostOffice is responsible for catching emails as they come in and logging them
to files for later processing. These messages are saved (one per file) as
serialized JSON objects to the `messages/` folder that sits next to this
file. While historically, SMTPD are often run on port 25, doing so requires
sudo access, and so we recommend using a differnet port allowing the service
to run as a non-privileged user. To configure nullmailer, you will add a line
under `/etc/nullmailer/remotes` that reads something like:
```
127.0.0.1 smtp port=12345
```

To run the service, we provide a [systemd](systemd/postoffice.service) file for
reference.

## PostMaster (server.py)

### Requirements
* gunicorn (or equivalent wsgi server)
* falcon

### Usage
PostMaster is responsible for serving up the emails captured by the PostOffice
to a PostMan who wants to deliver them. To do this, it iterates through
the `messages/` folder getting the contents of at-most 50 files and then
outputs it as a JSON object. After a file is read, it is destroyed, with the
PostMaster assuming that it has been delivered.

Running this service, we suggest that it be run using a socket, with an example
of the two necessary systmd files provided for the [service](systemd/postmaster.service)
and [socket](systemd/postmaster.socket). To hook this to nginx, you would
have it proxy_pass requests to: `http://unix:/run/postoffice/postmaster.socket`.

## PostMan (postman.py)

### Requirements
* requests

### Usage
PostMan is responsible for actually sending email. It makes a call to a web
host (which should then serve up the response from PostMaster). It's recommend
that it be calling a web-frontend (e.g. https://example.com/postoffice) which
handles both making sure requests only come from the server running PostMan
as well as then proxies to the server running PostMaster. After getting
the response from the server, it then iterates through the JSON object
and actually sends out the emails to their intended recipients (using postfix
or sendmail).

PostMan itself should be set up as a cron service that runs frequently
to constantly handle sending out email, such as every two minutes:
```
*/2 * * * * python3 /path/to/postman.py example.com/postoffice
```

PostMan does support using a basic HTTP authentication on its request for added
security on the server running the PostOffice accessible endpoint, but you
should still make sure that the endpoint only allows communication
from the IP address of the server running PostMan (through nginx, use a 
`deny all` rule with a `allow from <IP_ADDRESS>`).

## Development

Install Dependencies:
```
pip3 install -r requirements.txt
```

To start the smtpd server:
```
./smtpd.py
```

To start the web API:
```
gunicorn -b '127.0.0.1:8000' server:application
```