from flask import render_template,redirect, url_for, session, request, jsonify
from app import app, client, db,GOOGLE_CLIENT_SECRET
from models import *
import requests
import json

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

@app.route('/')
def index():
    if 'google_id' in session:
        user = User.query.filter_by(user_id=session['google_id']).first()
        if user:
            return render_template('index.html', user=user)
    return 'You are not logged in. <a href="/login">Login</a>'

@app.route('/login')
def login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('callback', _external=True),
        scope=['openid', 'email', 'profile'],
    )
    return redirect(request_uri)

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg['token_endpoint']

        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=url_for('callback', _external=True),
            code=code
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(client.client_id, GOOGLE_CLIENT_SECRET),
        )
        token_response.raise_for_status()

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo_response.raise_for_status()

        user_info = userinfo_response.json()
        if user_info.get('email_verified'):
            user_id = user_info['sub']
            user_name = user_info['name']
            user_email = user_info['email']
            user_profile_pic = user_info['picture']

            session['google_id'] = user_id
            session['google_name'] = user_name
            session['google_email'] = user_email

            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                new_user = User(
                    user_id=user_id,
                    name=user_name,
                    email=user_email,
                    profile_pic=user_profile_pic
                )
                db.session.add(new_user)
                new_user_leaderboard = Leaderboard(
                    level=0,
                    user_id=user_id
                )
                db.session.add(new_user_leaderboard)
                db.session.commit()
            
            return redirect(url_for('index'))
        else:
            return 'User email not available or not verified by Google.', 400
    except requests.exceptions.RequestException as e:
        print(f'Error during OAuth token exchange: {e}')
        return 'An error occurred during the OAuth process.', 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/leaderboard')
def view_users():
    scores = User.query.join(Leaderboard, User.user_id == Leaderboard.user_id).add_columns(
        User.user_id, User.name, Leaderboard.level, Leaderboard.updatedon
    ).all()
    user_list = [{'id': score.user_id, 'name': score.name, 'level': score.level, 'Time': score.updatedon} for score in scores]
    return jsonify(user_list)
