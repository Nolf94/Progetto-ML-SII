* Django environment setup:
		https://developer.mozilla.org/it/docs/Learn/Server-side/Django/development_environment

* Enter in your Django environment

* Install the dependencies from requirements.txt

		pip install -r /path/to/requirements.txt

* Provide env.config in the root folder of the project(check env.config.example)

* Migrate db (enter in .../Facebook_Django/project directory where manage.py is located):

		python manage.py makemigrations
		python manage.py migrate

* Run the project (sslserver for launch localhost with https connection):
		
		python manage.py runsslserver
