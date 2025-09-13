from backend.src.Models import User, db
from Application import app  # make sure you import your Flask app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    if not User.query.filter_by(username="admin1").first():
        hashed = bcrypt.generate_password_hash("password").decode("utf-8")
        u = User(username="admin1", password=hashed)
        db.session.add(u)
        db.session.commit()
        print("Created admin user:", u.username)
    else:
        print("Admin user already exists")

    # Verify
    print("All users:", User.query.all())
