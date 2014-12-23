# Setup Instructions for OSX #

## Install ##
- Follow the instructions [here](http://docs.python-guide.org/en/latest/starting/install/osx/) to install [Homebrew](http://brew.sh/) and then (re)install python.
- If for some reason the step above does not install pip and virtualenv, follow the instructions [here](https://pip.pypa.io/en/latest/installing.html#python-os-support) to get pip and then install virtualenv using pip install virtualenv.
- Install ngrok with `brew install ngrok` (thanks Homebrew!)
- Install the latest stable version of postgres 9. I recommend using Postgresapp for mac, available [here](http://postgresapp.com/).

## Configure ##
- `$ cd` into your projects/workspaces directory and run `$ git clone https://github.com/blockcypher/explorer.git`. The result of `$ git remote -v` should look like this:
```
origin	git@github.com:blockcypher/explorer.git (fetch)
origin	git@github.com:blockcypher/explorer.git (push)
```
- `$ cd explorer/` to get to the project root direction, create a python3 virtual environment (`$ virtualenv -p python3 venv`) and then activate it (`$ source venv/bin/activate`)
- Install requirements: `$ pip3 install -r requirements.txt` (this will take a few mins)
- Create a `.env` file in the project root directory with the following:
```
DEBUG=True
TEMPLATE_DEBUG=True
DJ_DEFAULT_URL=postgres://postgres:YOURLOCALPASSWORDHERE@localhost:5432/explorer_local
SECRET_KEY=RANDOMLY_GENERATED_50CHAR_STRING
SITE_DOMAIN=pick_this_yourself.ngrok.com
BLOCKCYPHER_API_KEY=PUT_YOURS_HERE
GH_CLIENT_ID=FROM_GITHUB
GH_CLIENT_SECRET=FROM_GITHUB
```
(these are for your local machine, production is a little different as `settings.py` is smartly designed to default to production settings)

- Create a database on your local machine with whatever name you like. I recommend `explorer_local` so it's clear you're working on a local copy. You'll be using this above in `DJ_DEFAULT_URL`. I've assumed your user is `postgres`, but you could have a different user.
- Create DB tables from code (replace `foreman` with `heroku` for running on production, which should basically never happen again):

```bash
# Create tables (can't remember if this is neccessary with Django 1.7 now)
$ foreman run python3 manage.py syncdb

# Run migrations:
$ foreman run python3 manage.py migrate
```
## Run the Site Locally ##

Run the webserver locally:
```
$ foreman run ./manage.py runserver
```

Now visit: http://127.0.0.1:8000/

To receive webhooks locally, you need to also run `ngrok` in the terminal (use the same `SITE_DOMAIN` from your `.env` file above):
```
$ ngrok -subdomain=pick_this_yourself 8000
```

Now visit http://pick_this_yourself.ngrok.com to confirm it's working (you could even do this on your phone)

## Check Out the Admin Section ##

- Create a superuser admin for yourself, by entering the following into `$ foreman run python3 manage.py shell`:

```python
from users.models import AuthUser
AuthUser.objects.create_superuser(email='YOURCHOICE', password='PASSWORDGOESHERE')
```

Now visit http://127.0.0.1:8000/admin


## Submit Your First Pull Request ##

First, pull the latest version of the code from github:
```
$ git pull origin master
```

Make a new branch:
```
$ git checkout -b my_branch
```

Make some trivial change and commit it:
```
$ git commit -am 'my changes'
```

Push it up to github:
```
$ git push origin my_branch
```

You can submit your pull request here:
https://github.com/blockcypher/explorer

Congrats, you're all setup!

# Post Setup Instructions #

## Build Awesome Features ##

You're on your own for that.

## Git Foo ##

Compare your local version of site to what's on github:
```
$ git log origin/master..HEAD --oneline
```
