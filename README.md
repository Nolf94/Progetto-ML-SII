Tested on Windows with Python 3.7.3. To install and run the application
* Django environment set up:

		https://developer.mozilla.org/it/docs/Learn/Server-side/Django/development_environment

* Enter in your Django environment

* Install the dependencies from requirements.txt

		pip install -r /path/to/requirements.txt

* Provide dotenv in the root folder of the project(check dotenv.example)

* Migrate db (enter in .../Facebook_Django/project directory where manage.py is located):

		python manage.py migrate

* Run the project (sslserver for launch localhost with https connection):
	
		python manage.py runsslserver

Doc for Facebook Api Graph:

	https://developers.facebook.com/docs/graph-api/reference/v4.0/object/likes
	https://developers.facebook.com/docs/graph-api/reference/post/
	https://developers.facebook.com/docs/graph-api/reference/user/posts/
	https://developers.facebook.com/docs/graph-api/reference/user/books/
	https://developers.facebook.com/docs/graph-api/reference/user/movies/
	https://developers.facebook.com/docs/graph-api/reference/user/music/
	https://developers.facebook.com/docs/graph-api/reference/user/photos/
	https://developers.facebook.com/docs/graph-api/reference/user/albums/
	https://developers.facebook.com/docs/graph-api/reference/v4.0/user/feed/