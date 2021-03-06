from app import db
class posts(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    post=db.Column(db.String(20))
    contact=db.Column(db.String(14))
    email=db.Column(db.String(60))

    def __repr__(self):
        return '<posts %r>' % (self.name)

class subscribers(db.Model):
    __tablename__='subscribers'
    id=db.Column(db.Integer,primary_key=True)
    roll_no=db.Column(db.String(20))
    user_fb_id=db.Column(db.String(100))

    def __repr__(self):
        return '<subscribers %r>' % (self.roll_no)

class warden(db.Model):
    __tablename__='warden'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    hostelname=db.Column(db.String(40))
    contact=db.Column(db.String(20))
    email=db.Column(db.String(60))

    def __repr__(self):
        return '<warden %r>' %(self.name)

class hod(db.Model):
    __tablename__='hod'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    deptname=db.Column(db.String(40))
    contact=db.Column(db.String(20))
    email=db.Column(db.String(60))

    def __repr__(self):
        return '<hod %r>' %(self.name)

class lib_books(db.Model):
    __tablename__ = 'lib_books'
    id = db.Column(db.Integer,primary_key=True)
    book_id=db.Column(db.String(30),unique=True)
    book_name = db.Column(db.Text)
    author_name = db.Column(db.Text)
    price = db.Column(db.Float)
    no_of_copies = db.Column(db.Integer)

    def __repr__(self):
        return '<lib_books %r>' %(self.book_name)

class book_issue(db.Model):
    __tablename__ = 'book_issue'
    id = db.Column(db.Integer,primary_key=True)
    book_name=db.Column(db.Text)
    stu_roll_no = db.Column(db.Text)
    issue_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    reminded = db.Column(db.Boolean)

    def __repr__(self):
        return '<book_issue %r>' %(self.book_name)

class prev_papers(db.Model):
    __tablename__='prev_papers'
    id=db.Column(db.Integer,primary_key=True)
    dept_name=db.Column(db.String(100))
    year=db.Column(db.String(5))
    semester=db.Column(db.String(2))
    subject=db.Column(db.String(40))
    exam_type=db.Column(db.String(20))
    url=db.Column(db.String(100))

    def __repr__(self):
        return '<prev_papers %r>' % (self.subject)

class sessions(db.Model):
    __tablename__='sessions'
    id=db.Column(db.Integer,primary_key=True)
    senderID=db.Column(db.String(50))
    sessionsID=db.Column(db.String(10))

    def __repr__(self):
        return '<sessions %r>' % (self.senderID)

class reminders(db.Model):
    __tablename__='reminders'
    id=db.Column(db.Integer,primary_key=True)
    senderID=db.Column(db.String(50))
    reminder_text=db.Column(db.String(100))
    reminder_time = db.Column(db.String(50))
    reminded = db.Column(db.Boolean)

    def __repr__(self):
        return '<reminders %r>' % (self.senderID)

class daily_time_table(db.Model):
    __tablename__='daily_time_table'
    id=db.Column(db.Integer,primary_key=True)
    department=db.Column(db.String(5))
    year=db.Column(db.String(4))
    semester=db.Column(db.String(4))
    day_of_week=db.Column(db.Integer)
    subjects=db.Column(db.String(100))

    def __repr__(self):
        return '<daily_time_table %r>' % (self.day_of_week)
