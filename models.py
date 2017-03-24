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
    book_name = db.Column(db.String(60))
    author_name = db.Column(db.String(45))
    price = db.Column(db.Float)
    no_of_copies = db.Column(db.Integer)

class book_issue(db.Model):
    __tablename__ = 'book_issue'
    id = db.Column(db.Integer,primary_key=True)
    book_id=db.Column(db.String(30))
    stu_roll_no = db.Column(db.String(40))
    issue_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    reminded = db.Column(db.Boolean)
