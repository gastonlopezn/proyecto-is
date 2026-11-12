from myapp.extensions import db

class Tag(db.Model):
    __tablename__ = "tag"

    title = db.Column(db.String, primary_key=True)

    def __repr__(self):
        return f"<Tag {self.title}>"