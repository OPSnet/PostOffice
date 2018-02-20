PostBox
=======

Smtpd server (via [aiosmtpd](https://github.com/aio-libs/aiosmtpd)) with a [falcon](https://falconframework.org/) 
frontend. Incoming messages are saved as serialized JSON objects in the `messages/` folder.

Requirements
------------
* Python 3.5+
* aiosmtpd
* falcon

Installation
------------
```
pip3 install -r requirements.txt
```

Usage
-----
To start the smtpd server:
```
./smtpd.py
```

To start the web API:
```
gunicorn -b '127.0.0.1:8000' server:application
```