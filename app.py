import os
import sqlite3
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename

# Import models
from Model.user import User
from Model.admin import Admin
from Model.crops import Crops
from Model.disease import Disease
from Model.comments import Comments
from Model.cropimage import Cropimage
from Model.message import Message

app = Flask(__name__, static_folder='static')
app.secret_key = 'agri_secret_key_128_bits_super_secure'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper to verify current session user
def get_session_user():
    if 'user_id' not in session:
        return None
    
    # Query database directly to check ban status and role
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, status FROM users WHERE id = ?", (session['user_id'],))
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[3] == 'banned':
        session.clear()
        return None
    
    # If admin, return Admin object, otherwise User object
    if row[2] == 'admin':
        return Admin(row[0], row[1], row[3])
    return User(row[0], row[1], row[2], row[3])

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# ================= AUTHENTICATION APIs =================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    success, res = User.register(email, password)
    if success:
        return jsonify({"message": "Registration successful. Please log in."}), 201
    return jsonify({"error": res}), 400

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    success, res = User.login(email, password)
    if success:
        session['user_id'] = res.user_id
        session['email'] = res.email
        session['role'] = res.role
        return jsonify({
            "message": "Login successful.",
            "user": {
                "id": res.user_id,
                "email": res.email,
                "role": res.role
            }
        })
    return jsonify({"error": res}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

@app.route('/api/auth/status', methods=['GET'])
def api_status():
    user = get_session_user()
    if user:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": user.user_id,
                "email": user.email,
                "role": user.role
            }
        })
    return jsonify({"authenticated": False})

# ================= CROPS APIs =================

@app.route('/api/crops', methods=['GET'])
def api_get_crops():
    try:
        crops_list = Crops.get_all()
        return jsonify(crops_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crops', methods=['POST'])
def api_add_crop():
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    data = request.get_json() or {}
    scientific_name = data.get('scientific_name')
    common_name = data.get('common_name')
    medicinal_benefit = data.get('medicinal_benefit')
    
    success, crop_id = user.addcropsinfo(scientific_name, common_name, medicinal_benefit)
    if success:
        return jsonify({"message": "Crop added successfully.", "crop_id": crop_id}), 201
    return jsonify({"error": crop_id}), 400

@app.route('/api/crops/<int:crop_id>', methods=['GET'])
def api_crop_detail(crop_id):
    crop_obj = Crops(crop_id=crop_id)
    info = crop_obj.getinfo()
    if info:
        return jsonify(info)
    return jsonify({"error": "Crop not found."}), 404

# ================= IMAGES APIs =================

@app.route('/api/crops/<int:crop_id>/images', methods=['POST'])
def api_upload_image(crop_id):
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400
        
    file = request.files['image']
    img_type = request.form.get('type') # 'healthy' or 'infected'
    
    if file.filename == '':
        return jsonify({"error": "Empty filename."}), 400
        
    if img_type not in ['healthy', 'infected']:
        return jsonify({"error": "Invalid image type. Must be 'healthy' or 'infected'."}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Unique prefix using crop_id and type to avoid overwrites
        filename = f"crop_{crop_id}_{img_type}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Save relative URL to database
        db_url = f"/static/uploads/{filename}"
        
        success, img_id = user.uploadimage(crop_id, db_url, img_type)
        if success:
            return jsonify({"message": "Image uploaded successfully.", "id": img_id, "url": db_url}), 201
        return jsonify({"error": img_id}), 400
        
    return jsonify({"error": "File type not allowed. Only JPG, JPEG, and PNG are accepted."}), 400

@app.route('/api/crops/<int:crop_id>/images/<int:image_id>', methods=['DELETE'])
def api_remove_image(crop_id, image_id):
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    # Get image url to delete file
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM crop_images WHERE id = ? AND crop_id = ?", (image_id, crop_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Image not found."}), 404
        
    url = row[0]
    
    # Remove from database
    success = Cropimage.removeimage(image_id)
    if success:
        # Delete local file if it is in uploads (don't delete seeded assets in images/)
        if 'uploads' in url:
            local_path = url.lstrip('/')
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception:
                    pass
        return jsonify({"message": "Image removed successfully."})
        
    return jsonify({"error": "Could not remove image."}), 500

# ================= DISEASES APIs =================

@app.route('/api/crops/<int:crop_id>/diseases', methods=['POST'])
def api_manage_disease(crop_id):
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    data = request.get_json() or {}
    disease_name = data.get('disease_name')
    description = data.get('description')
    treatment = data.get('treatment')
    is_treatable = data.get('is_treatable', True)
    
    success, res = user.manage_category(crop_id, disease_name, description, treatment, is_treatable)
    if success:
        return jsonify(res), 200
    return jsonify({"error": res}), 400

# ================= COMMENTS APIs =================

@app.route('/api/crops/<int:crop_id>/comments', methods=['POST'])
def api_post_comment(crop_id):
    user = get_session_user()
    if not user:
        return jsonify({"error": "Authentication required to comment."}), 401
        
    data = request.get_json() or {}
    text = data.get('text')
    
    success, res = Comments.post_comment(crop_id, user.user_id, text)
    if success:
        return jsonify({"message": "Comment posted successfully.", "comment_id": res}), 201
    return jsonify({"error": res}), 400

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def api_delete_comment(comment_id):
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    success = Comments.delete_comment(comment_id)
    if success:
        return jsonify({"message": "Comment deleted successfully."})
    return jsonify({"error": "Comment not found."}), 404

# ================= DIRECT MESSAGES APIs =================

@app.route('/api/messages', methods=['GET'])
def api_get_messages():
    user = get_session_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
        
    with_user_id = request.args.get('with_user_id', type=int)
    
    if with_user_id:
        # Check if chat target exists
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users WHERE id = ?", (with_user_id,))
        target_row = cursor.fetchone()
        conn.close()
        
        if not target_row:
            return jsonify({"error": "Target user not found."}), 404
            
        history = Message.get_chat_history(user.user_id, with_user_id)
        return jsonify(history)
    else:
        # Return recent chat partner list with their emails and last message
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query distinct users that have exchanged messages with current user
        cursor.execute('''
            SELECT DISTINCT id, email FROM users WHERE id != ? AND id IN (
                SELECT sender_id FROM messages WHERE receiver_id = ?
                UNION
                SELECT receiver_id FROM messages WHERE sender_id = ?
            )
        ''', (user.user_id, user.user_id, user.user_id))
        chat_users = [dict(r) for r in cursor.fetchall()]
        
        # Also return all users list if admin or user wants to start new chat
        # For simplicity, we also return all users (excluding banned ones)
        cursor.execute("SELECT id, email, role FROM users WHERE id != ? AND status = 'active'", (user.user_id,))
        all_users = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return jsonify({
            "recent_chats": chat_users,
            "all_users": all_users
        })

@app.route('/api/messages', methods=['POST'])
def api_send_message():
    user = get_session_user()
    if not user:
        return jsonify({"error": "Authentication required."}), 401
        
    data = request.get_json() or {}
    receiver_id = data.get('receiver_id')
    text = data.get('text')
    
    if not receiver_id:
        return jsonify({"error": "Receiver ID is required."}), 400
        
    success, res = Message.send_message(user.user_id, receiver_id, text)
    if success:
        return jsonify({"message": "Message sent.", "id": res}), 201
    return jsonify({"error": res}), 400

# ================= USER MANAGEMENT APIs =================

@app.route('/api/users', methods=['GET'])
def api_get_users():
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, status FROM users WHERE role != 'admin'")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/users/<int:user_id>/ban', methods=['POST'])
def api_ban_user(user_id):
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    success, msg = user.ban(user_id)
    if success:
        return jsonify({"message": msg})
    return jsonify({"error": msg}), 400

@app.route('/api/users/<int:user_id>/unban', methods=['POST'])
def api_unban_user(user_id):
    user = get_session_user()
    if not user or user.role != 'admin':
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403
        
    success, msg = user.unban(user_id)
    if success:
        return jsonify({"message": msg})
    return jsonify({"error": msg}), 400

if __name__ == '__main__':
    print("Starting Crops Info and Disease Detection Management System server on port 5000...")
    app.run(debug=True, port=5000)
