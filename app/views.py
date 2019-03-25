from dataclasses import asdict
from flask import current_app as app, g, request, session, flash, redirect, url_for
from flask_github import GitHub, GitHubError
from werkzeug.exceptions import HTTPException
from .models import User
from .decorators import templated

github = GitHub(app)


@github.access_token_getter
def token_getter():
    return g.user.oauth_token


@app.before_request
def before_request():
    g.user = User(**session.get('user', {}))


@app.after_request
def after_request(response):
    session['user'] = asdict(g.user)
    return response


@app.route('/')
@templated('index.html')
def index():
    pass


@app.route('/login')
def login():
    """
    NOTE: Though public_repo is too wide scope, there's no narrower alternatives at the time. The same concern applies
    to possibility of recreating existing Origin repo.
    TODO: pass CSRF token into state (fix a bug in the library?)
    """
    if g.user.authorized:
        flash('Already logged in.', category='warning')
        return redirect(url_for('index'))

    return github.authorize(scope='public_repo', redirect_uri=url_for('auth', _external=True))


@app.route('/auth')
@github.authorized_handler
def auth(oauth_token):
    """
    :param oauth_token: OAuth token received from GitHub or None if authorization failed.
    TODO: Verbose error message
    """
    next_url = request.args.get('next') or url_for('index')

    if oauth_token is None:
        flash("Authorization failed.", category='error')
        return redirect(next_url)

    g.user.oauth_token = oauth_token
    flash("Authorization successful.", category='success')

    try:
        response = github.get('/user')
        g.user.username = response['login']
        g.user.profile_url = response['html_url']
    except GitHubError:
        flash('Failed to get user info: %s' % GitHubError, category='error')

    return redirect(next_url)


@app.route('/logout')
def logout():
    """
    Lazy logout: it is just resetting User object in request context, which will later clean the session.
    """
    g.user.reset()
    flash('You have logged out.', category='success')

    return redirect(url_for('index'))


@app.route('/clone')
def clone_repository():
    """
    TODO: redirect to login
    TODO: check if repo already exists
    """
    if not g.user.authorized:
        flash('You are not authorized. Please log in to your GitHub account first.', category='warning')
        return redirect(url_for('index'))

    try:
        response = github.post('/repos/%s/forks' % app.config['ORIGINAL_REPO'])
        g.user.repo_url = response['html_url']
    except GitHubError:
        flash('Cloning repo failed: %s' % GitHubError, category='error')
        return redirect(url_for('index'))

    flash('Repository successfully cloned.', category='success')
    flash('Forking a Repository happens asynchronously. '
          'You may have to wait a short period of time before you can access the git objects.', category='info')

    return redirect(url_for('index'))


@app.errorhandler(HTTPException)
@templated('error.html')
def handle_http_error(e):
    return {"exception": e}, e.code
