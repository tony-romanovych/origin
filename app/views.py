from flask import current_app as app, request, session, flash, redirect, url_for
from flask_github import GitHub, GitHubError
from .decorators import templated


github = GitHub(app)


@github.access_token_getter
def token_getter():
    return session.get('oauth_token')


@app.route('/')
@templated('index.html')
def index():
    return {
        "github_link": 'https://github.com/%s' % app.config['ORIGINAL_REPO'],
        "user": {
            "authorized": 'oauth_token' in session,
            "profile_url": "#"
        }
    }


@app.route('/login')
def login():
    """
    NOTE: Though public_repo is too wide scope, there's no narrower alternatives at the time. The same concern applies
    to possibility of recreating existing Origin repo.
    TODO: pass CSRF token into state (fix a bug in the library?)
    """
    if 'oauth_token' in session:
        flash('Already logged in.')
        return redirect(url_for('index'))

    return github.authorize(scope='public_repo', redirect_uri=url_for('auth', _external=True))


@app.route('/auth')
@github.authorized_handler
def auth(oauth_token):
    """
    :param oauth_token: OAuth token received from GitHub or None if authorization failed.
    TODO: Get more information about user, and use smth like session.user
    TODO: Verbose error message
    """
    next_url = request.args.get('next') or url_for('index')

    if oauth_token is None:
        flash("Authorization failed.", category='error')
    else:
        session['oauth_token'] = oauth_token
        flash("Authorization successful.")

    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('oauth_token', None)
    return redirect(url_for('index'))


@app.route('/clone')
def clone_repository():
    """
    TODO: redirect to login
    TODO: check if repo already exists
    TODO: fork, mirror or clone?
    TODO: add link to the newly created fork (response.html_url)
    """
    if 'oauth_token' not in session:
        flash('You are not authorized. Please log in to your GitHub account first.', category='warning')
        return redirect(url_for('index'))

    try:
        response = github.post('/repos/%s/forks' % app.config['ORIGINAL_REPO'])
    except GitHubError:
        flash('Cloning repo failed: %s' % GitHubError, category='error')
        return redirect(url_for('index'))

    flash('Repository successfully cloned.', category='success')
    flash('Forking a Repository happens asynchronously. '
          'You may have to wait a short period of time before you can access the git objects.', category='info')
    return redirect(url_for('index'))
