import os
import sys
import json
import re
import string
import random

import apiai
import requests
from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta,date
import wikipedia
from operator import itemgetter,attrgetter
from time import strftime
import pytz

app = Flask(__name__)
CLIENT_ACCESS_TOKEN = '6dc4dd64472140deaad4cbe8f39ff10f'   #apiai client access_token

db = SQLAlchemy(app)
app.config.from_pyfile('app.cfg')   #config file

from models import posts, subscribers,warden,hod,lib_books,book_issue,prev_papers,sessions,reminders

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
    print("##############FROM webhook()################")
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    if(sender_id != '1639100099730911'):
                        upper_case_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        digits = "0123456789"
                        sessionID = ''.join(random.SystemRandom().choice(upper_case_letters + digits) for _ in range(7))
                        s = sessions(senderID = sender_id, sessionsID = sessionID)
                        db.session.add(s)
                        db.session.commit()

                        regex = "SUBSCRIBE.[UuPpIi].[0-9].[a-zA-z].[0-9][0-9]"
                        pattern = re.compile(regex)
                        string = message_text.upper()
                        if pattern.match(string):
                            add_subscriber(string,sender_id)
                            send_message(sender_id, "You have been sucessfully subscribed !!")
                        else:
                            send_message(sender_id, process_text_message(message_text,sessionID))
                            db.session.delete(s)
                            db.session.commit()

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
    print("##############Request(FROM getdata())################")
    print(json.dumps(req, indent=4))

    intentName = data["result"]["metadata"]["intentName"]

    parameters_dict = data["result"]["parameters"] #retrive the parameters_dict
    sess_ID = data["sessionId"]

    print("************"+intentName+"***********"+sess_ID)
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

    elif intentName == "search_books":
        book_name_to_search = (parameters_dict["book_name"]).upper()
        google_books_api = requests.get('https://www.googleapis.com/books/v1/volumes?q='+book_name_to_search)
        google_books_json = json.loads(google_books_api.content)
        book_name_to_search = (google_books_json['items'][0]['volumeInfo']['title']).upper()

        log(book_name_to_search)
        list_of_books = lib_books.query.all()
        for each_book in list_of_books:
            log(each_book.book_name)
            if each_book.book_name == book_name_to_search:
                result = "Yes, "+each_book.book_name+ " is available in Library. There are "+str(each_book.no_of_copies)+" copies currently available."

    elif intentName == "wiki":
        wiki_search_term = parameters_dict["wiki_term"]
        try:
            result = "Here is what I found out.\n\n" + str(wikipedia.summary(wiki_search_term, sentences=3))
        except wikipedia.exceptions.DisambiguationError as e:
            result = "Here is what I found out.\n\n" + str(wikipedia.summary(e.options[0], sentences=3))

    elif intentName == "previous_year_paper":
        dept = (parameters_dict["department"]).upper()
        subject = (parameters_dict["subject"]).upper()
        result = ""
        list_of_papers = prev_papers.query.all()
        for each_paper in list_of_papers:
            if (each_paper.subject == subject and each_paper.dept_name == dept):
                result = result + each_paper.year + " URL: " + each_paper.url + "\n\n"

    elif intentName == "map_search":
        maps_query = parameters_dict["map_query_term"]
        query_result = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+maps_query+'&location=21.167171%2C72.785145&radius=7000&key=AIzaSyBwyRj5vcOaRV9hRp_9MBph81hdyIsG2Wc')
        query_result_json = json.loads(query_result.content)
        list_of_places=[]
        #print(query_result_json)
        for place in query_result_json['results']:
            address = place['formatted_address']
            name_of_place = place['name']
            place_rating = place['rating']
            det_of_place={'rating':place_rating,'name_of_place':name_of_place,'address':address}
            list_of_places.append(det_of_place)

        list_of_places.sort(key=itemgetter('rating'),reverse=True)
        result=""
        r=""
        send_id=str(db.session.query(sessions).filter(sessions.sessionsID==sess_ID).all()[0].senderID)

        send_message(send_id,"Here is what I found:")
        for place in list_of_places[0:6]:
            r="Name: "+place['name_of_place']+"\n"+"Address: "+place['address']+"\n"+"Rating: "+str(place['rating'])+"\n"+"---------------\n"
            send_message(send_id,r)
        place=list_of_places[6]
        result="Name: "+place['name_of_place']+"\n"+"Address: "+place['address']+"\n"+"Rating: "+str(place['rating'])+"\n"+"---------------\n"

    elif intentName == "reminder_task":
        remind_text = parameters_dict["remind_text"]
        remind_time = parameters_dict["time"]
        remind_date = parameters_dict["date"]
        send_id=str(db.session.query(sessions).filter(sessions.sessionsID==sess_ID).all()[0].senderID)

        reminder = reminders(senderID = send_id, reminder_text = remind_text, reminder_time = remind_date+" "+remind_time, reminded = False)
        db.session.add(reminder)
        db.session.commit()
        result = "Your reminder set successfully"

    print("#######FROM getdata() RESULT which is sent to API.AI webhook call######")
    print(result)
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
def book_issue_from_lib():
    return render_template("indexissue.html")

@app.route('/prev_papers_entry')       #Function to enter previous year paper details
def prev_papers_entry():
    return render_template("q_papers.html")

@app.route('/exam_time_table')       #Function to enter exam time table details
def exam_time_table():
    return render_template("e_tt.html")

@app.route('/check_reminder',methods=['GET'])
def check_reminder():
    list_of_reminders = reminders.query.all()
    ist = datetime.now(pytz.timezone('Asia/Kolkata'))
    curr_time = datetime.strptime(ist.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
    for each_reminder in list_of_reminders:
        reminder_time = datetime.strptime(each_reminder.reminder_time,'%Y-%m-%d %H:%M:%S')
        if ((reminder_time - curr_time).total_seconds()<=7200):
            msg="Your event "+each_reminder.reminder_text+" is about to begin shortly"
            send_message(each_reminder.senderID,msg)
            db.session.delete(each_reminder)
            db.session.commit()
    return "Success"


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
            if curr.month<7:
                if(each_year == (int(curr_year)%2000)-roll):
                    send_message(each_user.user_fb_id,chp_name)
                    send_message(each_user.user_fb_id,'Poster URL: '+eve_poster_url)
                    send_message(each_user.user_fb_id,"Hola peeps!!!")
                    send_message(each_user.user_fb_id,'We at '+chp_name+' are excited to conduct- '+eve_name+'\n'+eve_dscp+'\n Date: '+date+'\n Time: '+time+'\n Venue: '+ venue )
            else:
                if(each_year == (int(curr_year)%2000)-roll+1):
                    send_message(each_user.user_fb_id,chp_name)
                    send_message(each_user.user_fb_id,'Poster URL: '+eve_poster_url)
                    send_message(each_user.user_fb_id,"Hola peeps!!!")
                    send_message(each_user.user_fb_id,'We at '+chp_name+' are excited to conduct- '+eve_name+'\n'+eve_dscp+'\n Date: '+date+'\n Time: '+time+'\n Venue: '+ venue )


    log(chp_name+" "+eve_name+" "+eve_dscp+" "+eve_poster_url+" "+date+" "+time+" "+venue+" "+tar_yr)
    return "Notification Sent Sucessfully !!"

@app.route('/book_entry_post',methods=['POST'])       #Function to Make a book entry in library table
def book_entry_post():
    b_id = (request.form['id']).upper()
    b_name = (request.form['b_name']).upper()
    a_name = (request.form['a_name']).upper()
    price = float(request.form['price'])
    no_of_copy = int(request.form['noc'])
    google_books_api = requests.get('https://www.googleapis.com/books/v1/volumes?q='+b_name+'+inauthor:'+a_name)
    google_books_json = json.loads(google_books_api.content)
    b_name = (google_books_json['items'][0]['volumeInfo']['title']).upper()
    a_name = (google_books_json['items'][0]['volumeInfo']['authors'][0]).upper()
    book = lib_books(book_id = b_id, book_name = b_name, author_name = a_name, price = price, no_of_copies = no_of_copy)
    db.session.add(book)
    db.session.commit()
    return "Sucessfully Added Book"+b_id+" "+b_name+" "+a_name+" "+str(no_of_copy)

@app.route('/book_issue_post',methods=['POST'])       #Function to issue a book
def book_issue_from_lib_post():
    stu_roll_no = str(request.form['stu_no']).upper()
    b_name = str(request.form['b_name']).upper()
    issue_date=date.today()
    due_date=date.today()+timedelta(days=1)
    issued_book=book_issue(book_name=b_name,stu_roll_no=stu_roll_no,issue_date=issue_date,due_date=due_date,reminded=False)
    db.session.query(lib_books).filter(lib_books.book_name==b_name).update({lib_books.no_of_copies:lib_books.no_of_copies-1})
    db.session.add(issued_book)
    db.session.commit()
    return stu_roll_no+" "+b_name+" "+str(issue_date)+" "+str(due_date)

@app.route('/prev_papers_entry_post',methods=['POST'])       #Function to enter previous year paper details
def prev_papers_entry_post():
    dept = (request.form['dept']).upper()
    year = str(request.form['year'])
    sem = str(request.form['sem'])
    subject = (request.form['sub']).upper()
    exam_type = (request.form['type']).upper()
    url = request.form['url']
    paper = prev_papers(dept_name = dept, year = year, semester = sem, subject = subject, exam_type = exam_type, url = url)
    db.session.add(paper)
    db.session.commit()
    return "sucessfully added " + dept + " " + year + " " + sem + " " + subject + " " + exam_type

@app.route('/exam_time_table_post',methods=['POST'])       #Function to enter exam time table details
def exam_time_table_post():
    dept_name = (request.form['dept']).upper()
    year = request.form['year']
    sem = request.form['semester']

    date1 = (request.form['1']).upper()).upper()
    sub1 = (request.form['2']).upper()
    time1 = (request.form['3']).upper()

    date2 = (request.form['4']).upper()
    sub2 = (request.form['5']).upper()
    time2 = (request.form['6']).upper()

    date3 = (request.form['7']).upper()
    sub3 = (request.form['8']).upper()
    time3 = (request.form['9']).upper()

    date4 = (request.form['10']).upper()
    sub4 = (request.form['11']).upper()
    time4 = (request.form['12']).upper()

    date5 = (request.form['13']).upper()
    sub5 = (request.form['14']).upper()
    time5 = (request.form['15']).upper()

    exam_time_table_msg = "Exam Time Table\n---------------\nDepartment: " + dept_name + "\nYear: " + year + "\nSemester: " + sem + "\n---------------------\n"+date1+"\n"+sub1+"\n"+time1
    exam_time_table_msg = exam_time_table_msg + "\n---------------------\n"+date2+"\n"+sub2+"\n"+time2
    exam_time_table_msg = exam_time_table_msg + "\n---------------------\n"+date3+"\n"+sub3+"\n"+time3
    exam_time_table_msg = exam_time_table_msg + "\n---------------------\n"+date4+"\n"+sub4+"\n"+time4
    exam_time_table_msg = exam_time_table_msg + "\n---------------------\n"+date5+"\n"+sub5+"\n"+time5

    dept_short_dict = {'COMPUTER ENGINEERING DEPARTMENT':'CO','ELECTRICAL ENGINEERING DEPARTMENT':'EE','ELECTRONICS ENGINEERING DEPARTMENT':'EC','MECHANICAL ENGINEERING DEPARTMENT':'ME','CIVIL ENGINEERING DEPARTMENT':'CE','CHEMICAL ENGINEERING DEPARTMENT':'CH'}
    dept_name = dept_short_dict[dept_name]
    return exam_time_table_msg+dept_name

def process_text_message(msg,s_id):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()    #make call to api.ai api
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = s_id
    request.query = msg

    response = json.loads(request.getresponse().read().decode('utf-8'))
    #print("##############FROM process_text_message() Printing response from API.AI################")
    #print(response)
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

@app.route('/seelib',methods=['GET'])       #Function to see all entry in library
def seelib():
    a=lib_books.query.all()
    b=book_issue.query.all()
    log(a)
    log("hello")
    x=""
    for p in a:
        x=x+p.book_id+" "+p.book_name+" "+p.author_name+" "+str(p.price)+" "+str(p.no_of_copies)+"<br>"
    x = x + "<br><br><br>"
    for p in b:
        x=x+p.book_name+" "+p.stu_roll_no+" "+str(p.issue_date)+" "+str(p.due_date)+" "+str(p.reminded)+"<br>"
    return x

@app.route('/dellib',methods=['GET'])       #Function to del all entry in library
def dellib():
    lib_books.query.delete()
    book_issue.query.delete()
    db.session.commit()
    return "sucessfully deleted"

@app.route('/seeprevpapers',methods=['GET'])       #Function to see all entry in prev_papers
def seeprevpapers():
    a=prev_papers.query.all()
    log(a)
    log("hello")
    x=""
    for p in a:
        x=x+p.dept_name+" "+p.year+" "+p.semester+" "+p.subject+" "+p.exam_type+" "+p.url+"<br>"
    return x

@app.route('/delprevpapers',methods=['GET'])       #Function to del all entry in prev_papers
def delprevpapers():
    prev_papers.query.delete()
    db.session.commit()
    return "sucessfully deleted"

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

@app.route('/del/reminders/all',methods=['GET'])    #Function for delete all values in subscribers
def delreminders():
    reminders.query.delete()
    db.session.commit()
    return "sucessfully deleted"


@app.route('/cron_test',methods=['GET'])    #Function for testing cron scheduling
def cron_test():
    curr_time = datetime.utcnow()
    send_message("1690740887619815","Hola It's "+str(curr_time)+" now")
    return "sucessful"

@app.route('/seeallsessions',methods=['GET'])    #Function for testing cron scheduling
def seeallsessions():
    a=sessions.query.all()
    log(a)
    x=""
    for p in a:
        x=x+p.senderID+" "+p.sessionsID+"<br>"
    return x

@app.route('/seeallreminders',methods=['GET'])    #Function to see all reminders
def seeallreminders():
    a=reminders.query.all()
    log(a)
    x=""
    for p in a:
        x=x+p.senderID+" "+p.reminder_text+" "+p.reminder_time+" "+str(p.reminded)+"<br>"
    return x

def send_message(recipient_id, message_text):

    print("##############FROM send_message()################")
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
