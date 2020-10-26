from flask import Flask, render_template,redirect,url_for,flash,request
from forms import PredictorForm
import pickle
import numpy as np
import real_time_data as rtd
import datetime

app = Flask(__name__)
model=pickle.load(open('model.pkl','rb'))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'TOP_SECRET_PROJECT'

form_data = {
    'Country': '',
    'Forest': '',
}

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html',title='',status='')

@app.route('/about')
def about():
    return render_template('about.html',title='about',status='')

@app.route('/donate')
def donate():
    return render_template('donate.html',title='donate',status='')

@app.route('/predictor', methods=['GET','POST'])
def predictor():
    form = PredictorForm()

    if form.validate_on_submit():
        form_data['Country'] = form.country.data.capitalize()
        form_data['Forest'] = form.forest.data.title()

        try:
            for key, value in rtd.fetch_data(form_data['Forest']):
                form_data[key.capitalize()] = value
        except:
            print('ERROR: Could not find it!')

        #Converting UNIX Timestamp to Datetime
        timestamp = datetime.datetime.fromtimestamp(form_data['Time'])
        form_data['Time'] = timestamp.strftime('%d-%m-%Y %H:%M:%S')

        flash(f'Form Submitted Successfully', 'success')
        # then redirect to "end" the form
        return redirect(url_for('prediction')) #Change to Result page

    return render_template('predictor.html', title='predictor', form = form)

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    int_features = [int(x) for x in request.form.values()]
    final = [np.array(int_features)]
    print(int_features)
    print(final)
    prediction = model.predict_proba(final)
    output = '{0:.{1}f}'.format(prediction[0][1], 2)

    if output > str(0.5):
        return render_template('forest_fire.html',
                               pred='Your Forest is in Danger.\nProbability of fire occuring is {}'.format(output))
    else:
        return render_template('forest_fire.html',
                               pred='Your Forest is safe.\n Probability of fire occuring is {}'.format(output))


@app.route('/prediction')
def prediction():
    return render_template('prediction.html',title='prediction',status='',form_data=form_data)

@app.route('/forest_fire')
def forest_fire():
    return render_template('forest_fire.html',title='forest_fire',status='')


@app.route('/services')
def services():
    return render_template('services.html',title='services',status='')

if __name__ =='__main__':
    app.run(debug=True)
