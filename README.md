# PBL6

Command for Linux only (update and install necessary package)

`sudo apt-get update`

`sudo apt-get install libmysqlclient-dev pkg-config`

Command for MacOS only (update and install necessary package)

`brew update`

`brew install mariadb`

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

- Run create seeder database
 'python3 manage.py shell'
=> create account
>>> from auth_site.models import Account
>>> from auth_site.factories import AccountFactory
>>> num_objects = 20
>>> accounts = [AccountFactory.create() for _ in range(num_objects)]
>>> Account.objects.bulk_create(accounts)

=> create account
>>> from news.models import Categories
>>> from news.factories import CategoriesFactory
>>> num_objects = 10
>>> categories = [CategoriesFactory.create() for _ in range(num_objects)]
>>> Categories.objects.bulk_create(categories)

=> create account
 from news.models import News
 from news.factories import NewsFactory
 from auth_site.models import Account
 num_news = 100
 news = [NewsFactory.create() for _ in range(num_news)]
 News.objects.bulk_create(news)

 => create account
 from news.models import Comments
 from news.factories import CommentsFactory
 num_comments = 100
 comments = [CommentsFactory.create() for _ in range(num_comments)]
 Comments.objects.bulk_create(comments)