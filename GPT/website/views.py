from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Input
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ai_text()
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 
        if note:
            if len(note)<1:
                flash('Note is too short!', category='error')
            else:
                new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
                db.session.add(new_note) #adding the note to the database 
                db.session.commit()
                flash('Note added!', category='success')
                
        if not note:
            flash('Please enter some text!', category='error')

    return render_template("home.html", user=current_user)
def ai_text():
    if request.method == 'POST': 
        #Gets the text from the HTML 
        text = request.form.get('text')
        print(text)
        print(current_user)
        print(current_user.id)
        if text:
            if len(text)<1:
                flash('Note is too short!', category='error')
            else:
                if current_user.is_authenticated:
                    new_text = Input(data=text, user_id=current_user.id)  #providing the schema for the note 
                    db.session.add(new_text) #adding the note to the database 
                    db.session.commit()
                    flash('Text added!', category='success')
                else:
                    #new_text = Input(data=text)
                    #db.session.add(new_text)
                    #db.session.commit()
                    flash('Text added to temp cache!', category='success')
                
        if not text:
            flash('Please enter some text!', category='error')

    return jsonify({})


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})