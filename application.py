from flask import Flask, render_template, url_for, request, redirect, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, City, Art

# For OAuth

from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Web client 1"


# Connect to database and create database session

engine = create_engine('sqlite:///cityart.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    print "Access token is:"
    print access_token
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print response
        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        print response
        return redirect('/')


# Show all cities


@app.route('/')
def DefaultCityArt():
    city = session.query(City)
    return render_template('citylist.html', city=city, login_session=login_session)


@app.route('/cities/<int:city_id>')
def CityPage(city_id):
    cities = session.query(City)
    city = session.query(City).filter_by(id=city_id).one()
    art = session.query(Art).filter_by(city_id=city.id)
    return render_template('artlist.html', city=city, art=art, cities=cities, login_session=login_session)


@app.route('/cities/artwork/<int:art_id>')
def ArtPage(art_id):
    art = session.query(Art).filter_by(id=art_id).one()
    return render_template('artpage.html', art=art, login_session=login_session)

# Allow user to create new art item


@app.route('/new/', methods=['GET', 'POST'])
def newArt():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Art(name=request.form['itemName'],
                      description=request.form['itemDescription'],
                      city_id=request.form['categoryName'])
        session.add(newItem)
        session.commit()
        print "Item has been added"
        art_id = newItem.id
        return redirect(url_for('ArtPage', art_id=art_id))
    else:
        cities = session.query(City)
        return render_template('newart.html', cities=cities, login_session=login_session)

# Allow users to edit art items


@app.route('/cities/artwork/<int:art_id>/edit', methods=['GET', 'POST'])
def editArt(art_id):
    editedItem = session.query(Art).filter_by(id=art_id).one()
    cities = session.query(City)
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['itemName'] or request.form['itemDescription'] or request.form['categoryName']:
            editedItem.name = request.form['itemName']
            editedItem.description = request.form['itemDescription']
            editedItem.city_id=request.form['categoryName']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('ArtPage', art_id=art_id))
    else:
        return render_template('edit_art.html', editedItem=editedItem, cities=cities, login_session=login_session)


# Allow user to delete art items


@app.route('/cities/artwork/<int:art_id>/delete', methods=['GET', 'POST'])
def deleteArt(art_id):
    deletedItem = session.query(Art).filter_by(id=art_id).one()
    city_id = deletedItem.city_id
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        return redirect(url_for('CityPage', city_id=city_id))
    else:
        return render_template('delete_art.html',
                               deletedItem=deletedItem,
                               city_id=city_id,
                               login_session=login_session)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
