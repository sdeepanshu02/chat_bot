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
