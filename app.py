from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
#from send_mail import send_mail
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup as bs


app = Flask(__name__)

ENV = 'prod'
#ENV ='dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hkwqwmjzaocbtd:190d5dc808eab38d25ab0c358a74fc08f22dbba9a10f558dd7db40bbc1463dd1@ec2-52-201-55-4.compute-1.amazonaws.com:5432/db8r04lt818ifp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments





class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)



@app.route('/')
def index():
    return render_template('overview.html')





@app.route('/login')
def login():
    return render_template('login.html')




@app.route('/overview')
def overview():
    return render_template('overview.html')



@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        # print(customer, dealer, rating, comments)
        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields')
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data)
            db.session.commit()
           # send_mail(customer, dealer, rating, comments)
            return render_template('success.html')
        return render_template('index.html', message='You have already submitted feedback')






@app.route('/portfolio')
def portfolio():
    return render_template('index2.html')






@app.route('/weather', methods = ['GET','POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')
        
        if new_city:
            new_city_obj = City(name=new_city)

            db.session.add(new_city_obj)
            db.session.commit()

    cities = City.query.all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=352318b0096c90c8b3a94a031f4ee602'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(city.name)).json()

        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)










def getData(url):
    r = urllib.request.urlopen(url)
    return r










def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for j, v in enumerate(voices):
        if voices[j].id == 'hindi':
            break

    print(voices[j].id)
    engine.setProperty('voice', voices[j].id)
    engine.setProperty('rate', 100)
    engine.setProperty('volume', 0.9)
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = r.listen(source, timeout=3)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()


def mains():

    a = "Jammu and Kashmir\nPunjab\nHimachal Pradesh\nHaryana\nDelhi\nRajasthan\nUttar Pradesh\nUttarakhand\nMadhya Pradesh\nChattisgarh\nGujarat\nMaharashtra\nKarnataka\nGoa\nKerala\nTamil nadu\nAndhra pradesh\nTelangana\nOrissa\nBihar\nJharkhand\nWest Bengal\nAssam\nArunach Pradesh\nSikkim\nMeghalaya\nMizoram\nNagaland\nTripura"

    states = a.split("\n")
    states_list = []
    for state in states:
        states_list.append(state.lower())


    print("started parsing")
    myHtmlData = getData("https://www.mohfw.gov.in/")
    print("parsed")

    soup = bs(myHtmlData, 'html.parser')
    myDataStr = ""
    for tr in soup.find_all('tr'):
        myDataStr += tr.get_text()
    myDataStr = myDataStr[1:]
    itemList = myDataStr.split("\n\n")

    print("Started Program")

    END_PHRASE = "stop"

    i = 0
    # UPDATE_COMMAND = "update"

    while True:
        getAudio = []
        print("Listening...")
        text = get_audio()
        getAudio.append(text)
        print(text)
        if (getAudio[0] == 'total cases'):
            total_confirmed_in_india = itemList[34].split("\n")
            total_confirmed_cases_in_india_text = total_confirmed_in_india[0]
            total_number_of_cases_in_india = total_confirmed_in_india[1]
            total_number_of_cured_in_india = itemList[35]
            total_number_of_deaths_in_india = itemList[36]

            nTex = f'I ,am ,announcing ,about  , {total_confirmed_cases_in_india_text}  , in, which, total,' \
                    f'confirmed, cases, are, {total_number_of_cases_in_india[:-1]} , cured,and, discharge' \
                    f'd, are ,{total_number_of_cured_in_india},  ' \
                    f'and, total ,deaths, till, now, are , {total_number_of_deaths_in_india} ,'
            speak(nTex)
            continue
        for item in itemList[1:35]:
            dataList = item.split("\n")
            if dataList[1].lower() in getAudio:

                nText = f'I ,am ,announcing ,about ,State , {dataList[1]}  in, which, total,confirmed,cases, are, {dataList[2]} , cured,and, discharged, are ,{dataList[3]},  ' \
                        f'and, total ,deaths, till, now, are , {dataList[4]} ,'

                speak(str(nText))
                break
            else:
                continue

        # if text == UPDATE_COMMAND:
        #   result = "Data is being updated. This may take a moment!"
        #  data.update_data()

        # if result:
        #   speak(result)

        if text.find(END_PHRASE) != -1:  # stop loop
            print("Exit")
            break












@app.route('/corona')
def corona():
    #mains()
    return render_template('corona_data.html')



















@app.route('/notification',methods=['POST'])
def notification():
    try:

        if request.method == 'POST':
            mains()
    except:
        return render_template('corona_data.html')
    return render_template('corona_data.html')













if __name__ == '__main__':
    app.run()
