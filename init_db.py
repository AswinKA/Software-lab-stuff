import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        status TEXT NOT NULL DEFAULT 'active'
    );
    ''')
    
    # 2. Create crops table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scientific_name TEXT NOT NULL,
        common_name TEXT NOT NULL,
        medicinal_benefit TEXT
    );
    ''')
    
    # 3. Create crop_images table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crop_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        type TEXT NOT NULL, -- 'healthy' or 'infected'
        FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
    );
    ''')
    
    # 4. Create diseases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS diseases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        disease_name TEXT NOT NULL,
        description TEXT NOT NULL,
        treatment TEXT NOT NULL,
        is_treatable INTEGER NOT NULL DEFAULT 1, -- 0 = False, 1 = True
        FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
    );
    ''')
    
    # 5. Create comments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    
    # 6. Create messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    
    # Seed default users
    # Password hashing using werkzeug
    admin_pw = generate_password_hash('admin123')
    user1_pw = generate_password_hash('user123')
    user2_pw = generate_password_hash('user123')
    
    users_data = [
        ('admin@agri.com', admin_pw, 'admin', 'active'),
        ('john@agri.com', user1_pw, 'user', 'active'),
        ('alice@agri.com', user2_pw, 'user', 'active')
    ]
    
    for email, pw, role, status in users_data:
        try:
            cursor.execute("INSERT INTO users (email, password, role, status) VALUES (?, ?, ?, ?)", (email, pw, role, status))
        except sqlite3.IntegrityError:
            pass # already seeded
            
    # Seed default crops
    crops_data = [
        (1, 'Solanum lycopersicum', 'Tomato', 'Rich in lycopene, vitamin C, and potassium. Promotes heart health, reduces cancer risk, and benefits skin health.'),
        (2, 'Zea mays', 'Corn', 'High in dietary fiber, lutein, and zeaxanthin, supporting digestive health and eye function.'),
        (3, 'Solanum tuberosum', 'Potato', 'Good source of vitamin B6, potassium, and antioxidants. Helps lower blood pressure and supports digestion.')
    ]
    
    for cid, s_name, c_name, med in crops_data:
        cursor.execute("SELECT id FROM crops WHERE id = ?", (cid,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO crops (id, scientific_name, common_name, medicinal_benefit) VALUES (?, ?, ?, ?)", (cid, s_name, c_name, med))
            
    # Seed crop images
    images_data = [
        (1, '/static/images/tomato_healthy.jpg', 'healthy'),
        (1, '/static/images/tomato_infected.jpg', 'infected'),
        (2, '/static/images/corn_healthy.jpg', 'healthy'),
        (2, '/static/images/corn_infected.jpg', 'infected'),
        (3, '/static/images/potato_healthy.jpg', 'healthy'),
        (3, '/static/images/potato_infected.jpg', 'infected')
    ]
    
    for crop_id, url, img_type in images_data:
        cursor.execute("SELECT id FROM crop_images WHERE crop_id = ? AND url = ?", (crop_id, url))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO crop_images (crop_id, url, type) VALUES (?, ?, ?)", (crop_id, url, img_type))
            
    # Seed diseases
    diseases_data = [
        (1, 'Late Blight', 'Caused by the oomycete Phytophthora infestans. It appears as irregular dark, water-soaked lesions on leaves and stems, with white fuzzy growth on the undersides during humid weather.', 'No cure once infected. Immediately remove and destroy all infected plants. Apply preventative copper-based fungicides to surrounding healthy crops. Ensure good spacing for ventilation.', 0),
        (1, 'Tomato Mosaic Virus', 'Causes mottling (light and dark green mosaic patterns) on leaves, leaf curling, and severe stunting. Fruits may ripen unevenly and show internal browning.', 'No chemical cure. Remove and burn infected plants. Disinfect hands and gardening tools with soap or milk solution. Use resistant seed varieties.', 0),
        (1, 'Blossom End Rot', 'Causes a dark, flat, leathery black patch at the bottom (blossom end) of the tomatoes. It is a physiological disorder rather than a disease.', 'Maintain consistent watering (avoid letting soil dry out completely). Apply calcium carbonate or gypsum to soil. Avoid excessive nitrogen fertilizer.', 1),
        (2, 'Common Rust', 'Caused by the fungus Puccinia sorghi. Characterized by prominent powdery, reddish-brown pustules on both upper and lower leaf surfaces.', 'Use resistant hybrids. Apply fungicides like strobilurins or triazoles early if rust symptoms threaten the crop. Rotate crops and clean debris.', 1),
        (2, 'Maize Dwarf Mosaic', 'Stunting of plants, mosaic patterns of yellow/light green stripes on leaves, and reduced ear size. Transmitted by aphids.', 'Control aphid vectors. Manage weed hosts (like Johnsongrass) near the field. Plant resistant corn hybrids.', 0),
        (3, 'Early Blight', 'Caused by the fungus Alternaria solani. Produces dark brown to black spots with concentric rings ("target board" pattern) on older leaves first.', 'Apply copper or chlorothalonil fungicides. Space plants to ensure dry leaves. Clean up all crop residues after harvest. Rotate crops yearly.', 1)
    ]
    
    for crop_id, d_name, desc, treat, treatable in diseases_data:
        cursor.execute("SELECT id FROM diseases WHERE crop_id = ? AND disease_name = ?", (crop_id, d_name))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO diseases (crop_id, disease_name, description, treatment, is_treatable) VALUES (?, ?, ?, ?, ?)", (crop_id, d_name, desc, treat, treatable))
            
    # Seed sample comments
    comments_data = [
        (1, 2, 'My tomatoes are showing small yellow spots. Should I be worried about late blight?'),
        (1, 1, 'Hi John! Yes, watch them closely. If they turn into dark water-soaked spots, remove the leaves immediately. Early prevention is key!'),
        (2, 3, 'Can common rust be treated organically?'),
        (2, 1, 'Alice, yes, you can try organic copper fungicides or neem oil sprays if detected early.')
    ]
    
    for crop_id, user_id, text in comments_data:
        cursor.execute("SELECT id FROM comments WHERE crop_id = ? AND user_id = ? AND text = ?", (crop_id, user_id, text))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO comments (crop_id, user_id, text) VALUES (?, ?, ?)", (crop_id, user_id, text))
            
    # Seed sample messages
    messages_data = [
        (2, 1, "Hello Admin, I have a quick question about my tomatoes."),
        (1, 2, "Sure, John! What symptoms are you seeing?"),
        (2, 1, "They have dark spots on the bottom. I read about Blossom End Rot here. Is it really calcium deficiency?"),
        (1, 2, "Yes, it is highly likely calcium deficiency combined with uneven watering. Try to water them consistently and add some agricultural lime.")
    ]
    
    for sender, receiver, text in messages_data:
        cursor.execute("SELECT id FROM messages WHERE sender_id = ? AND receiver_id = ? AND text = ?", (sender, receiver, text))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, text) VALUES (?, ?, ?)", (sender, receiver, text))
            
    conn.commit()
    conn.close()
    print("Database initialized and seeded successfully.")

if __name__ == '__main__':
    init_db()
