# Project Origin

This repository source code and running example of it together form a self-replicating GitHub repository.

Application is created primarily for education purpose. Functionality is dead simple: it allows you to sign in
to your GitHub account and clone its source code ("fork" in GitHub terms). You get a new repository with full
application source code copy, licensed under MIT. You can then run your own application instance following the
instructions below.

Check out live example at https://origin-234822.appspot.com/. Interface is pretty straightforward and self-describing.
Don't forget to logout after you've done playing with it.


## Tech specs


Application is written in Python 3 using [Flask](http://flask.pocoo.org/) - python microframework for web development.
Additionally I used [GitHub-Flask](https://github-flask.readthedocs.io/en/latest/) extension that gives
high level interface to GitHub API and OAuth authorization process. Docs for the latter are available
[here](https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/). It is deployed to
Google Cloud Platform and is running on Google App Engine.

Therefore, code structure is conventional to Flask projects, with couple differences/alternatives:
- `.env` file is used to store config values, especially those considered to be private. This file must not be
  commited to repository. There's `.env.example` with the list of available settings.
- Dependencies are handled via `virtualenv` together with `requirements.txt`. I would like to use `pipenv`,
  but this is the special requirement of App Engine.
- `main.py` in the project root used as an entrypoint.


## Installation


#### Prerequisites
First of all, you have to own a GitHub account, in which you have permissions to create OAuth apps.

Then you also have to create and activate an account on [Google Cloud Platform](https://cloud.google.com/).
This application is tested in Google App Engine Python 3 Standard Environment
([docs](https://cloud.google.com/appengine/docs/standard/python3/)),
and this instructions assume that you use it too. However, you can choose another deployment option for Python3
application, see more examples in official [Flask documentation](http://flask.pocoo.org/docs/1.0/deploying/).

#### Step 1 - Create a GitHub OAuth app
In order for application to be able to sign in to other user GitHub account, GitHub has to be able to identify it.
This is done by registering it as GitHub OAuth app. To do that, follow the steps one and (optionally) two from the
official [GitHub tutorial](https://developer.github.com/apps/building-oauth-apps/).

Because your application is not deployed yet, you don't know the _Homepage URL_ and _Authorization callback URL_.
As for now, you can just set it to something valid like `https://origin.appspot.com/` and `https://origin.appspot.com/auth`.

#### Step 2 - Get the source code
Create a folder on your computer that is gonna be your _project root_ folder.
Then run `git clone https://github.com/tony-romanovych/origin .` within your new project root or manually download
zip archive from repository home page (and extract files to the project root). If you have already forked the project,
you can also do the same with your repository.

#### Step 3 - Set the environment variables
In the project root copy file `.env.example` and rename it to `.env`. This is just a regular text file that follows
.ini files syntax, so you can use any text editor.

First, set a random string as a secret key. More info on why this is important and how to generate a secure key is
available [here](http://flask.pocoo.org/docs/1.0/quickstart/#sessions). Then, set GitHub app client ID and client secret
that you've got on previous step. Finally, if you want new repositories to be forked from **your** repo instead of
original (`tony-romanovych/origin`), change that value.

#### Step 4 - Create new google cloud project, deploy and run the application
Good instructions on how to create a new gcloud project can be found in official
[App Engine docs](https://cloud.google.com/appengine/docs/standard/python3/quickstart).
Follow the steps 1-4 in _Before you begin_ section.

As it's done, open command prompt, go to the project root and execute `gcloud app deploy`. It takes couple minutes to
upload files, build the project and update the service. Finally, you should see a success message with the URL of
the deployed service. Congratulations, your app is now up and running! Follow this link (or run `gcloud app browse`)
and check if homepage is displaying right.

#### Step 5 - Adjust GitHub OAuth app settings
Now go back to GitHub OAuth app settings and replace _Homepage URL_ and domain portion of _Authorization callback URL_
with the new service URL (`/auth` remains). That's it! Your app is fully functional, go ahead and test it yourself.


## Notes


I don't much like the code structure, especially talking about `app/views.py`. All logic is mixed and placed within
controllers (or *views* in terms of Flask). And this module has import side effects, which feels as something definitely
bad. However, Flask documentation is absolutely ok with that, so I'm not sure, maybe it's kinda proper style, due to
its simplicity or whatever.

Seems like this GitHub lib is not ready to production. It cannot handle CSRF token on auth properly, it cannot handle
OAuth error messages. Should have used my own approach or write a pull request.

#### TO DO
- On `/clone` redirect to login and back (in order to complete entire workflow in one step)
- Extend GitHub-Flask: pass CSRF token into `state`, handle auth error message
- Write tests, refactor `app/views.py`; mock GitHub interaction?
- Review code, add comments if necessary
- Check if repo already exists on auth
- Improve configuration, create dev/test/prod envs,
  use [dotenv](http://flask.pocoo.org/docs/1.0/cli/#environment-variables-from-dotenv)
- Deployment scripts?

#### Explore
- Logging and failure reports, [Flask error handling](http://flask.pocoo.org/docs/1.0/errorhandling/)
- Overall security, server-side session
- Show more info before and after cloning?
- Consider setting "entrypoint" in app.yaml instead of main.py
- Refresh tokens?
