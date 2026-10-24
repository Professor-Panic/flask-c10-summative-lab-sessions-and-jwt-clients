from faker import Faker

from app import app
from extensions import db
from models import Note, User

fake = Faker()


def seed():
    Note.query.delete()
    User.query.delete()

    users = []
    for name in ("tedd", "ian", "carol"):
        user = User(username=name)
        user.password_hash = "password123"
        db.session.add(user)
        users.append(user)
    db.session.flush()

    for user in users:
        for _ in range(15):
            db.session.add(
                Note(
                    title=fake.sentence(nb_words=4).rstrip("."),
                    content=fake.paragraph(nb_sentences=4),
                    user_id=user.id,
                )
            )
    db.session.commit()
    print("Seeded users tedd, ian, carol (password: password123), 15 notes each.")


if __name__ == "__main__":
    with app.app_context():
        seed()
