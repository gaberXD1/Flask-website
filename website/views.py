from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, User, Message, Schedule, Registration
from . import db
import json
import os
from datetime import datetime

views = Blueprint('views', __name__)

# Ensure allowed file extensions (PNG, JPG, JPEG)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
from werkzeug.utils import secure_filename
import os

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')
        
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user, notes=notes)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

#@views.route('/schedule')
#@login_required
#def schedule():
    #return render_template("schedule.html", user=current_user, page_background="background-schedule")

@views.route('/players', methods=['GET', 'POST'])
@login_required
def register_camp():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        age = request.form.get('age')
        position = request.form.get('position')
        team_name = request.form.get('team_name')
        phone_number = request.form.get('phone_number')
        paid = bool(request.form.get('paid'))

        new_registration = Registration(
            user_id=current_user.id,
            full_name=full_name,
            age=int(age) if age else None,
            position=position,
            team_name=team_name,
            phone_number=phone_number,
            paid=paid
        )

        db.session.add(new_registration)
        db.session.commit()
        flash('Uspešno si se prijavil v kamp!', category='success')
        return redirect(url_for('views.home'))

    return render_template('players.html', user=current_user)

@views.route('/index')
@login_required
def index():
    return render_template("index.html", user=current_user, page_background="background-introduction")

@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        new_message = Message(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        db.session.add(new_message)
        db.session.commit()
        flash('Sporočilo uspešno poslano!', category='success')
        return redirect(url_for('views.home'))

    return render_template('contact.html', user=current_user)


@views.route('/travel')
@login_required
def travel():
    return render_template("travel.html", user=current_user, page_background="background-travel")

@views.route('/about')
@login_required
def about():
    return render_template("about.html", user=current_user, page_background="background-about")

# 🛡️ ADMIN PANEL
@views.route('/admin')
@login_required
def admin_panel():  # <-- TO je ime endpointa
    if current_user.email != "admin@email.com":
        flash("Dostop zavrnjen – samo za admina.", category='error')
        return redirect(url_for('views.home'))

    users = User.query.all()
    messages = Message.query.all()
    schedules = Schedule.query.all()
    registrations = Registration.query.all()

    return render_template(
        "admin.html",
        user=current_user,
        users=users,
        messages=messages,
        schedules=schedules,
        registrations=registrations
    )

@views.route('/delete-message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    if current_user.email != "admin@email.com":
        flash("Dostop zavrnjen.", category='error')
        return redirect(url_for('views.home'))

    message = Message.query.get(message_id)
    if message:
        db.session.delete(message)
        db.session.commit()
        flash('Sporočilo izbrisano.', category='success')

    return redirect(url_for('views.admin_panel'))

@views.route('/ban-user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    if current_user.email != "admin@email.com":
        flash("Dostop zavrnjen.", category='error')
        return redirect(url_for('views.home'))

    user = User.query.get(user_id)
    if user:
        user.banned = True
        user.email = "[odstranjen]"
        db.session.commit()
        flash("Uporabnik je bil banan in e-mail odstranjen.", category='success')
    else:
        flash("Uporabnik ni najden.", category='error')

    return redirect(url_for('views.admin_panel'))

@views.route('/admin/schedule-editor', methods=['GET', 'POST'])
@login_required
def schedule_editor():
    if current_user.email != "admin@email.com":
        flash("Dostop zavrnjen", category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        time = request.form.get('time')         # pričakujemo YYYY-MM-DDTHH:MM
        activity = request.form.get('activity')
        person = request.form.get('person')
        day = request.form.get('day')

        try:
            time_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Napačen format datuma in ure!", category='error')
            return redirect(url_for('views.schedule_editor'))

        new_schedule = Schedule(
            match_date=time_obj,
            team_name=activity,
            user_id=current_user.id,
            day=int(day)
        )
        db.session.add(new_schedule)
        db.session.commit()
        flash("Schedule shranjen!", category='success')
        return redirect(url_for('views.schedule_editor'))

    schedules = Schedule.query.order_by(Schedule.day.asc(), Schedule.match_date.asc()).all()
    return render_template('schedule_editor.html', user=current_user, schedules=schedules)



@views.route('/schedule')
@login_required
def show_schedule():
    schedules = Schedule.query.order_by(Schedule.match_date.asc()).all()
    users = User.query.all()
    users_dict = {u.id: u.first_name for u in users}
    return render_template("schedule.html", user=current_user, schedules=schedules, users_dict=users_dict)


@views.route('/delete-schedule/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    if current_user.email != "admin@email.com":
        flash("Dostop zavrnjen.", category='error')
        return redirect(url_for('views.home'))

    schedule = Schedule.query.get(schedule_id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
        flash("Vrstica izbrisana!", category='success')
    return redirect(url_for('views.schedule_editor'))

@views.route('/edit-schedule/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    if current_user.email != "admin@email.com":
        flash("Dostop zavrnjen.", category='error')
        return redirect(url_for('views.home'))

    schedule = Schedule.query.get_or_404(schedule_id)

    if request.method == 'POST':
        time = request.form.get('time')
        activity = request.form.get('activity')
        person = request.form.get('person')  # To preberemo iz obrazca
        day = request.form.get('day')

        try:
            match_time = datetime.strptime(time, "%Y-%m-%dT%H:%M")
            schedule.match_date = match_time
            schedule.team_name = activity
            schedule.user_id = current_user.id
            schedule.person_name = person  # Posodobi z `person_name`
            schedule.day = int(day)
            db.session.commit()
            flash("Vrstica posodobljena!", category='success')
            return redirect(url_for('views.schedule_editor'))
        except ValueError:
            flash("Napaka pri formatiranju datuma!", category='error')

    return render_template("edit_schedule.html", user=current_user, schedule=schedule)





