from flask import current_app as app, request, session, flash, redirect, url_for, jsonify
from flask_github import GitHub
from .decorators import templated


github = GitHub(app)


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
    if 'oauth_token' in session:
        flash('Already logged in.')
        return redirect(url_for('index'))

    # Though public_repo is too wide scope, there's no narrower alternatives at the time
    # The same concern applies to possibility of recreating existing Origin repo
    return github.authorize(scope='public_repo', redirect_uri=url_for('auth', _external=True))


@app.route('/auth')
@github.authorized_handler
def auth(oauth_token):
    next_url = request.args.get('next') or url_for('index')

    if oauth_token is None:
        flash("Authorization failed.", category='error')
    else:
        session['oauth_token'] = oauth_token
        flash("Authorization successful.")

    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('oauth_token')

    return redirect(url_for('index'))


@app.route('/clone')
def clone_repository():
    if 'oauth_token' not in session:
        # TODO: redirect to login
        flash('You are not authorized. Please log in to your GitHub account first.', category='error')
        return redirect(url_for('index'))

    # TODO: fork, mirror or clone?
    response = github.post('/repos/' + app.config['ORIGINAL_REPO'] + '/forks')

    return jsonify(response)


@github.access_token_getter
def token_getter():
    return session.get('oauth_token')
