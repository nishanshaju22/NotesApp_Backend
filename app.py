from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)


# Define the Note Model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created": self.created_at.strftime("%d-%m-%y-%H:%M:%S"),
            "updated": self.updated_at.strftime("%d-%m-%y-%H:%M:%S")
        }


# Create a database

@app.before_request
def create_db_tables():
    db.create_all()
    

# API Endpoints

# Add notes
@app.route('/notes', methods=["POST"])
def create_notes():
    data = request.get_json()
    
    title = data.get('title', None)
    content = data.get('content', None)
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    new_notes = Note(title = title, content = content)
    db.session.add(new_notes)
    db.session.commit()
    
    return jsonify(new_notes.to_dict()), 201
   
# Get all notes
@app.route('/notes', methods=["GET"])
def get_notes():
    notes = Note.query.all()
    return jsonify([note.to_dict() for note in notes]), 200

# Get single notes by ID
@app.route('/notes/<int:note_id>', methods=["GET"])
def get_note(note_id):
    note = Note.query.get(note_id)
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    return jsonify(note.to_dict()), 200

# Delete a note by ID
@app.route('/notes/<int:note_id>', methods=["DELETE"])
def delete_note(note_id):
    note = Note.query.get(note_id)
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({"message": "Note deleted successfully"}), 204

# Update a note by ID
@app.route('/notes/<int:note_id>', methods=["PUT"])
def update_note(note_id):
    note = Note.query.get(note_id)
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    
    db.session.commit()
    
    return jsonify(note.to_dict()), 200


# Run the app 
if __name__ == '__main__':
    app.run(debug=True)