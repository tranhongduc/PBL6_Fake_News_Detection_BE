# PBL6

Command for Linux only (update necessary package)

`sudo apt-get update`

`sudo apt-get install`

`libmysqlclient-dev pkg-config`

Windows / Linux:

- Once installed python, type `pip install django` to install Django package
- Create Django project with command `django-admin startproject "name-project"`
- CD into directory where we have our Django project and create Django application with command `python manage.py startapp "name-app"`
- Install dependencies

    `pip install -r requirements.txt`

- Apply changes of migrate

    `python manage.py makemigrations`

- Run Migrate

    `python manage.py migrate`

- Run Server

    `python manage.py runserver`

- Create user for django admin panel 

    `python manage.py createsuperuser`

- Run AI model (update soon)