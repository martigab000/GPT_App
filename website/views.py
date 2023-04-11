from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Input, Response
from . import db
from .code import ask_ai, delete_temp, check_db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_text()
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
                
        #if not note:
            #flash('Please enter some text!', category='error')
    return render_template("hcfa1500.html", user=current_user)
def user_text():
    if request.method == 'POST': 
        #Gets the text from the HTML 
        text = request.form.get('text')
        if text:
            if len(text)<1:
                flash('Note is too short!', category='error')
            elif check_db(text) != None:
                response = check_db(text)
                flash(response)
            else:
                if current_user.is_authenticated:
                    new_text = Input(data=text, user_id=current_user.id)  #providing the schema for the note 
                    db.session.add(new_text) #adding the note to the database 
                    db.session.commit()
                    flash('Text added!', category='success')
                    text_data = new_text.data
                    text_id = new_text.id
                    ask_ai(text_data, text_id)
                else:
                    #new_text = Input(data=text)
                    #db.session.add(new_text)
                    #db.session.commit()
                    flash('Text added to temp cache!', category='success')
                
        #if not text:
            #flash('Please enter some text!', category='error')

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

@views.route('/delete-text', methods=['POST'])
def delete_text():
    delete_temp()  
    text = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    textId = text['textId']
    text = Response.query.get(textId)
    #print(text)
    input = text.input_id
    #print(input)
    user_id = Input.query.get(input)
    #print(user_id)
    if text:
        if user_id.user_id == current_user.id:
            db.session.delete(text)
            db.session.delete(user_id)
            db.session.commit()

    return jsonify({})