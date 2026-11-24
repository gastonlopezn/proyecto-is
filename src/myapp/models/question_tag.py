from myapp.extensions import db

# Tabla de asociación muchos-a-muchos entre Question y Tag.
# ondelete="CASCADE" asegura que, al borrar una pregunta o un tag,
# también se borren sus filas de asociación a nivel de base de datos.
question_tag = db.Table(
    "question_tag",
    db.Column(
        "question_id",
        db.Uuid,
        db.ForeignKey("question.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_title",
        db.String,
        db.ForeignKey("tag.title", ondelete="CASCADE"),
        primary_key=True,
    ),
)
