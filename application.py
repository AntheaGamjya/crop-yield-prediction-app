import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

# Initialize Flask app and OAuth
application = Flask(__name__)
application.secret_key = 'your_secret_key_app'  # Replace with your secret key

# Configure OAuth
oauth = OAuth(application)
google = oauth.register(
    name='google',
    client_id='577170508273-u1hl7j6c76rc3ks33j60khphm2e087oe.apps.googleusercontent.com',  # Replace with your client_id
    client_secret='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',  # Replace with your client_secret
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

# Load your dataset
df = pd.read_csv('features.csv', header=0)

# Load the pre-trained model and preprocessor
with open('model_xgb (1).pkl copy', 'rb') as model_file:
    model = pickle.load(model_file)

with open('preprocesser.pkl', 'rb') as preprocessor_file:
    preprocessor = pickle.load(preprocessor_file)

@application.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@application.route('/')
def home():
    return render_template('home.html')

@application.route('/authorize')
def authorize():
    # This is the callback route where Google redirects after successful login
    token = google.authorize_access_token()  # Retrieves the access token
    resp = google.get('userinfo')  # Fetch user info from Google
    user_info = resp.json()  # Parse the user info response
    session['user_email'] = user_info['email']  # Store user email in the session
    return redirect(url_for('predict_page'))  # Redirect to the prediction page

@application.route('/predict-page')
def predict_page():
    # Check if user is logged in
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('predict.html')

@application.route('/predict', methods=['POST'])
def predict():
    # Collect user inputs
    state = request.form['state']
    year = int(request.form['year'])
    crop = request.form['crop']
    area = float(request.form['area'])

    reqd_features = df.loc[
        (df['year'] == year) &
        (df['state'] == state) &
        (df['crop'] == crop)
    ]
    reqd_features.insert(3, 'area', area)

    # Make prediction
    prediction = model.predict(reqd_features)
    predicted_yield = prediction[0]
    return render_template('output.html', prediction=f" {predicted_yield:.2f} tons")

@application.route('/logout')
def logout():
    session.pop('user_email', None)  # Remove user email from the session
    return redirect(url_for('home'))

if __name__ == '__main__':
    application.run(debug=True)
# if __name__ == "__main__":
#     application.run(host='0.0.0.0', port=8080)
