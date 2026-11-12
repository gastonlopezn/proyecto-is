from myapp.extensions import db

class Category(db.Model):
    __tablename__ = "category"

    title = db.Column(db.String, primary_key=True)

    def __repr__(self):
        return f"<Category {self.title}>"