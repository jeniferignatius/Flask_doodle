from flask import render_template, redirect, url_for, abort, flash, jsonify
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, ContactForm, MeetupForm, SendingForm, MeetupeditForm
from .. import db
from ..models import Role, User, Contact,Meetup, Invite
from ..decorators import admin_required
from ..email import send_email


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        message = form.message.data
        my_data = Contact(name=name, email=email, phone=phone,message=message)
        db.session.add(my_data)
        db.session.commit()
        flash('Thank you for contacting us.')
        return redirect(url_for('main.index'))
    return render_template('contact.html', form=form)

@main.route('/meetup', methods=['GET', 'POST'])
@login_required
def meetup():
    form = MeetupForm()
    if form.validate_on_submit():
        name = form.name.data
        location = form.location.data
        startdate = form.startdate.data
        enddate = form.enddate.data
        note = form.note.data
        my_meetup = Meetup(name=name, location=location, startdate=startdate, enddate=enddate, note=note)
        db.session.add(my_meetup)
        db.session.commit()
        flash('Event has created...')
        return redirect(url_for('main.date'))
    name = form.name.data
    my_meetup = Meetup.query.order_by(Meetup.startdate)
    return render_template('meetup.html', form=form, my_meetup=my_meetup)

@main.route('/date', methods=['GET','POST'])
@login_required
def date():
    form = SendingForm()
    my_meetup = Meetup.query.all()
    my_invite = Invite.query.all()
    my_meetup = Meetup.query.order_by(Meetup.startdate)
    if form.validate_on_submit():
        my_invite = Invite(email=form.email.data)
        my_invite = Invite.query.filter_by(email=form.email.data.lower()).first()
        #db.session.add(my_invite)
        db.session.commit()
        #user = User.query.filter_by(email=form.email.data.lower()).first()
        if my_invite:
            #token = user.generate_token()
            send_email(my_invite.email, 'confirm your event',
                       'auth/email/invite_participant',
                       my_invite=my_invite)
        flash('An email with invite participants '
              'sent to you.')
    return render_template('date.html',form=form,my_meetup=my_meetup,my_invite=my_invite)

@main.route('/invite_participant', methods=['GET','POST'])
@login_required
def invite_participant():
    form = SendingForm()
    my_meetup = Meetup.query.all()
    my_invite = Invite.query.all()
    #my_meetup = Meetup.query.order_by(Meetup.startdate)
    if form.validate_on_submit():
        my_invite = Invite(email=form.email.data)
        my_invite = Invite.query.filter_by(email=form.email.data.lower()).first()
        #db.session.add(my_invite)
        db.session.commit()
        #user = User.query.filter_by(email=form.email.data.lower()).first()
        if my_invite:
            #token = user.generate_token()
            send_email(my_invite.email, 'confirm your event',
                       'auth/email/invite_participant',
                       my_invite=my_invite)
        flash('An email with invite participants '
              'sent to you.')
    return render_template('date.html',form=form, my_invite=my_invite)



#this is our update route where we are going to update the event
@main.route('/edit_event', methods = ['GET', 'POST'])
@login_required
def edit_event():
    #form = MeetupeditForm()
    my_data = Meetup.query.get_or_404(id)
    if request.method == 'POST':
        my_data= Meetup.query.get(request.form.get(id))
        #my_data = Meetup.query.filter_by(name=form.name.data.lower()).first()
 
        my_data.name = request.form['name']
        my_data.location = request.form['location']
        my_data.startdate = request.form['startdate']
        my_data.enddate = request.form['enddate']
        my_data.note = request.form['note']
        db.session.add(my_data._get_current_object())
        db.session.commit()
        flash("Event Updated Successfully")
        return redirect(url_for('main.date', name=my_data.name))
    form.name.data = my_data.name
    form.location.data = my_data.location
    form.startdate.data = my_data.startdate
    form.enddate.data = my_data.enddate
    form.note.data = my_data.note
    #return render_template('date.html', form=form,my_data=my_data)
 
 
 
 
#This route is for deleting the event
@main.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Meetup.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Event Deleted Successfully")
 
    return redirect(url_for('main.date'))

@main.route('/calendar-events')
def calendar_events():
	conn = None
	cursor = None
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT id, title, url, class, UNIX_TIMESTAMP(start_date)*1000 as start, UNIX_TIMESTAMP(end_date)*1000 as end FROM event")
		rows = cursor.fetchall()
		resp = jsonify({'success' : 1, 'result' : rows})
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
    


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
