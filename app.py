import os
import sys
import json
import re

import apiai
import requests
from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CLIENT_ACCESS_TOKEN = '6dc4dd64472140deaad4cbe8f39ff10f'   #apiai client access_token
db = SQLAlchemy(app)
app.config.from_pyfile('app.cfg')   #config file

from models import posts, subscribers,warden,hod

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world method get", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    regex = "SUBSCRIBE.[UuPpIi].[0-9].[a-zA-z].[0-9][0-9]"
                    pattern = re.compile(regex)
                    string = message_text.upper()
                    if pattern.match(string):
                        add_subscriber(string,sender_id)
                        send_message(sender_id, "You have been sucessfully subscribed !!")
                    else:
                        send_message(sender_id, process_text_message(message_text))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

@app.route('/getdata', methods=['POST'])    #This function process the information request of API.AI Query
def getdata():
    req = request.get_json(silent=True, force=True)
    data = request.get_json()
    print("Request:")
    print(json.dumps(req, indent=4))

    intentName = data["result"]["metadata"]["intentName"]
    print("************"+intentName)

    parameters_dict = data["result"]["parameters"] #retrive the parameters_dict
    result = "I don't know"

    if intentName == "posts":                       # If Query is for post search in posts table
        search_value = parameters_dict["post"]   #retrive the search term
        list_of_posts = posts.query.all()
        for each_post in list_of_posts:
            if each_post.post == search_value:
                result = each_post.name

    elif intentName == "details_of_post":
        detail_term = parameters_dict["details"]
        search_entity = parameters_dict["post"]
        list_of_posts = posts.query.all()
        for each_post in list_of_posts:
            if each_post.post == search_entity:
                if detail_term == "name":
                    result = each_post.name
                elif detail_term == "contact":
                    result = each_post.contact
                elif detail_term == "email":
                    result = each_post.email

    elif intentName == "details_of_hod":
        detail_term = parameters_dict["details"]
        dept_name = parameters_dict["department"]
        list_of_hods = hod.query.all()
        for each_hod in list_of_hods:
            if each_hod.deptname == dept_name:
                if detail_term == "name":
                    result = each_hod.name
                elif detail_term == "contact":
                    result = each_hod.contact
                elif detail_term == "email":
                    result = each_hod.email

    elif intentName == "details_of_warden":
        detail_term = parameters_dict["details"]
        hostel_name = parameters_dict["hostel"]
        list_of_wardens = warden.query.all()
        for each_warden in list_of_wardens:
            if each_warden.hostelname == hostel_name:
                if detail_term == "name":
                    result = each_warden.name
                elif detail_term == "contact":
                    result = each_warden.contact
                elif detail_term == "email":
                    result = each_warden.email
    res = {                                                #Generate the result to send back to API.AI
        "speech": result,
        "displayText": result,
        "source": "agent"
        }
    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'

    return r
@app.route('/send_notification_stu_chap')       #Function to send notification of stu chap
def send_notification_stu_chap():
    return render_template("indexstu.html")

@app.route('/book_entry')       #Function to Make a book entry in library table
def book_entry():
    return render_template("indexlib.html")

@app.route('/book_issue')       #Function to issue a book
def book_issue():
    return render_template("indexissue.html")


@app.route('/send_notification_stu_chap_post',methods=['POST'])       #Function to send notification of stu chap
def send_notification_stu_chap_post():
    chp_name = request.form['chp_name']
    eve_name = request.form['eve_name']
    eve_dscp = request.form['eve_dscp']
    eve_poster_url = request.form['eve_poster_url']
    date = request.form['date']
    time = request.form['time']
    venue = request.form['venue']
    tar_yr = request.form['tar_yr']
    years=tar_yr.split('_')
    for each_year in years:
        each_year=int(each_year)
        users=subscribers.query.all()
        for each_user in users:
            roll = each_user.roll_no
            roll = int(roll[1:3])
            curr = datetime.utcnow()
            curr_year = curr.year
            if(each_year == (int(curr_year)%2000)-roll):
                send_message(each_user.user_fb_id,chp_name)
                send_message(each_user.user_fb_id,'Poster URL: '+eve_poster_url)
                send_message(each_user.user_fb_id,"Hola peeps!!!")
                send_message(each_user.user_fb_id,'We at '+chp_name+' are excited to conduct- '+eve_name+'\n'+eve_dscp+'\n Date: '+date+'\n Time: '+time+'\n Venue: '+ venue )


    log(chp_name+" "+eve_name+" "+eve_dscp+" "+eve_poster_url+" "+date+" "+time+" "+venue+" "+tar_yr)
    return "Notification Sent Sucessfully !!"

@app.route('/book_entry_post',methods=['POST'])       #Function to Make a book entry in library table
def book_entry_post():
    b_id = request.form['id']
    b_name = request.form['b_name']
    a_name = request.form['a_name']
    price = request.form['price']
    no_of_copies = request.form['noc']
    return b_id+" "+b_name+" "+a_name+" "+price+" "+no_of_copies

@app.route('/book_issue_post',methods=['POST'])       #Function to issue a book
def book_issue_post():
    stu_roll_no = request.form['stu_no']
    b_name = request.form['b_name']
    issue_date = request.form['i_date']
    due_date = request.form['d_date']
    return stu_roll_no+" "+b_name+" "+issue_date+" "+due_date


def process_text_message(msg):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()    #make call to api.ai api
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = "Ajf54Trh" #generate random session_id later
    request.query = msg

    response = json.loads(request.getresponse().read().decode('utf-8'))
    log(response)
    responseStatus = response['status']['code']
    if (responseStatus == 200):
        # Sending the textual response of the bot.
        return (response['result']['fulfillment']['speech'])

    else:
        return ("Sorry, I couldn't understand that question")


@app.route('/seeallpost',methods=['GET'])       #Function to see all entry in posts
def seeallpost():
    a=posts.query.all()
    log(a)
    log("hello")
    x=""
    for p in a:
        x=x+p.name+" "+p.post+" "+p.contact+" "+p.email+"<br>"
    return x

@app.route('/add/posts/<details>',methods=['GET'])      #Function for add entry in posts
def addposts(details):
    get_name, get_post, get_contact, get_email = details.split('_')
    pos = posts(name = get_name, post = get_post, contact = get_contact, email = get_email)
    db.session.add(pos)
    db.session.commit()
    return "sucessfully added"

@app.route('/del/posts/all',methods=['GET'])    #Function for delete all values in posts
def delposts():
    posts.query.delete()
    db.session.commit()
    return "sucessfully deleted"

@app.route('/seeallsubscribers',methods=['GET'])       #Function to see all entry in subscribers
def seeallsubscribers():
    a=subscribers.query.all()
    log(a)
    log("hello")
    x=""
    for p in a:
        x=x+p.roll_no+" "+p.user_fb_id+"<br>"
    return x

@app.route('/add/subscribers/',methods=['GET'])      #Function for add entry in subscribers
def addsubscribers():
    user = subscribers(roll_no = 'U15CO061', user_fb_id = 'hfsakjhskajhsk')
    db.session.add(user)
    db.session.commit()
    return "sucessfully added"

@app.route('/del/subscribers/all',methods=['GET'])    #Function for delete all values in subscribers
def delsubscribers():
    subscribers.query.delete()
    db.session.commit()
    return "sucessfully deleted"

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
def add_subscriber(request_string, user_id):
    a,user_roll_no = request_string.split(' ')
    user = subscribers(roll_no = user_roll_no, user_fb_id = user_id)
    db.session.add(user)
    db.session.commit()

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
