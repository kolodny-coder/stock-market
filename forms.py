from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange

# Setting Up the form fields
class RegisterPlayers(FlaskForm):
    user_name = StringField(validators=[DataRequired()])
    submit = SubmitField('Register')

class SalesBids(FlaskForm):
    sell_asking_price = IntegerField(validators=[DataRequired(), NumberRange()], render_kw={'placeholder': 'sell asking price'})
    sell_shares_amount = IntegerField(validators=[DataRequired()], render_kw={'placeholder': 'sell shares amount'})
    submit_sale_offer = SubmitField('Submit sale offer')

class BuyBids(FlaskForm):

    buy_asking_price = IntegerField(validators=[DataRequired()], render_kw={'placeholder': 'Buy asking price'})
    buy_shares_amount = IntegerField(validators=[DataRequired()], render_kw={'placeholder': 'Buy asking price'})
    submit_buy_offer = SubmitField('Submit buy offer')
