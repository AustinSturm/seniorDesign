## Installation
We are utilizing python3.5, Django, virtualenv

**Install virtualEnv**
```
apt-get install python3.5
apt-get install python-setuptools python-dev build-essential
apt-get install python3-pip
pip install virtualenv
```
**Install Django and rest_framework**
```
pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support

git clone https://github.com/django/django.git
pip install -e django/

# external modules
pip install coreapi
```
**Activate virtualEnv**
```
cd sd/
source api/bin/activate
```
**Set Allowed hosts in settings.py**
```
ALLOWED_HOSTS = ['your_ip', 'localhost', '127.0.0.1']

Example: ALLOWED_HOSTS = ['18.218.238.214', 'localhost', '127.0.0.1']
```
**Ensure Database is upto Date**
```
python3 manage.py makemigrations
python3 manage.py migrate
```
##Run Server
To run the server in your client session, closing the SSH session or terminal will disable the running server:
```
cd /sd/rest
python3 manage.py runserver 0.0.0.0:8000
```

To run the server in the background allowing the session to be closed while keeping the server running:
```
cd /sd/rest
nohup python3 manage.py runserver 0.0.0.0:8000 &
```

##Scorched Earth Policy
If it won't migrate, make it.
```
drop database dbname;
create database dbname;
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;

rm all migrations excluding __init__ and pycache__

**pray**

makemigrations && migrate
```
