import uuid

from sqlalchemy.orm import validates

from myapp.extensions import db


class Position(db.Model):
    __tablename__ = "position"
    __table_args__ = (
        db.CheckConstraint(
            "quantity >= 0",
            name="ck_position_quantity_non_negative",
        ),
    )

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    response_id = db.Column(
        db.Uuid,
        db.ForeignKey("response.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = db.relationship("User", back_populates="positions")
    response = db.relationship("Response", back_populates="positions")

    @validates("quantity")
    def validate_quantity(self, _key: str, value: float) -> float:
        if value is None or value < 0:
            raise ValueError("Position quantity cannot be negative.")
        return value

    def __repr__(self) -> str:
        return (
            f"<Position user_id={self.user_id!r} "
            f"response_id={self.response_id!r} "
            f"quantity={self.quantity} purchase_price={self.purchase_price}>"
        )
