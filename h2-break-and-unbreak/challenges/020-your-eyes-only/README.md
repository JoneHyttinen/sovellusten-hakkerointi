# Django login example

Copyright 2024 Tero Karvinen https://TeroKarvinen.com

## How virtualenv/ was created

	$ virtualenv virtualenv/ -p python3 --system-site-packages

	$ source virtualenv/bin/activate
	$ which pip
	...virtualenv/bin/pip
	
	$ cat requirements.txt
	django==4.2.*
	$ pip install -r requirements.txt
	Successfully installed django-4.2.16

	$ django-admin --version
	4.2.16

## How to use virtualenv/

	$ source virtualenv/bin/activate

## How to run

Navigate to the folder containing manage.py. 

Update the database. 

	$ ./manage.py makemigrations; ./manage.py migrate

Run test server. 

	$ ./manage.py runserver

Happy hacking!
