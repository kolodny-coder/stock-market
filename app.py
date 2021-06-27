from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from forms import RegisterPlayers, SalesBids, BuyBids
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
db = SQLAlchemy(app)



# Setting players table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    number_of_shares = db.Column(db.Integer())

    def __repr__(self):
        return f"Users(user_name: '{self.user_name}', number_of_shares: '{self.number_of_shares}')"


# Setting bids Table
class TradeBids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bid_type = db.Column(db.String(80), nullable=False)
    price_per_share = db.Column(db.Integer())
    share_amount = db.Column(db.Integer())
    trader_name = db.Column(db.String(80), nullable=False)
    bid_status = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"TradeBids(id: '{self.id}', bid type: '{self.bid_type}', price_per_share: '{self.price_per_share}', share_amount: '{self.share_amount}', trader_name: '{self.trader_name}')"


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterPlayers()
    if register_form.validate_on_submit():
        player = Users(user_name=register_form.user_name.data)
        user_name = player.user_name
        all = Users.query.all()
        for name in all:
            if player.user_name in name.user_name:
                return redirect(url_for('user_page', user_name=user_name))
        player.number_of_shares = 0
        db.session.add(player)
        db.session.commit()
        return redirect(url_for('user_page', user_name=user_name))
    return render_template('register.html', form=register_form)


@app.route('/user_page/<user_name>', methods=['GET', 'POST'])
def user_page(user_name):
    user = Users.query.filter_by(user_name=user_name).first()
    # session['name'] = 'my_value'
    # session['name'] = user.user_name
    # session.pop('name', None)
    # session['user'] = user
    sales_bid_form = SalesBids()
    buy_bids_form = BuyBids()
    if buy_bids_form.validate_on_submit():
        # Save the bid on memory
        bid = TradeBids(bid_type='buy', price_per_share=buy_bids_form.buy_asking_price.data,
                        share_amount=buy_bids_form.buy_shares_amount.data,
                        trader_name=user.user_name,
                        bid_status='pending')

        # handle the bid before it saves to data base
        look_for_match = TradeBids.query.filter(TradeBids.bid_type == 'sell',
                                                TradeBids.price_per_share <= bid.price_per_share,
                                                TradeBids.share_amount >= bid.share_amount,
                                                TradeBids.trader_name != user.user_name,
                                                TradeBids.bid_status == 'pending'
                                                ).order_by(TradeBids.price_per_share).first()

        # we dont have a deal save the bid
        if not look_for_match:
            db.session.add(bid)
            db.session.commit()
            return render_template('user_page.html', user=user, sell_form=sales_bid_form, buy_form=buy_bids_form)

        # we have a deal !!!! exchange shares
        if look_for_match:
            diff = bid.share_amount
            # Update the seller total share
            Users.query.filter_by(user_name=look_for_match.trader_name).update(
                dict(number_of_shares=look_for_match.share_amount - bid.share_amount))
            db.session.commit()

            # Update the buyer total share
            Users.query.filter_by(user_name=user.user_name).update(
                dict(number_of_shares=user.number_of_shares + bid.share_amount))
            db.session.commit()

            # Update the seller bid
            bid_id_to_update = look_for_match.id
            TradeBids.query.filter_by(id=bid_id_to_update).update(
                dict(share_amount=look_for_match.share_amount - bid.share_amount))

            if TradeBids.query.filter_by(id=bid_id_to_update).first().share_amount == 0:
                TradeBids.query.filter_by(id=bid_id_to_update).update(
                    dict(bid_status='expired'))

            db.session.commit()

    if sales_bid_form.validate_on_submit():
        if sales_bid_form.sell_shares_amount.data >= user.number_of_shares:
            flash("insufficient number of shares", 'error')
            return render_template('user_page.html', user=user, sell_form=sales_bid_form, buy_form=buy_bids_form)

        # Save the bid to the memory
        bid = TradeBids(bid_type='sell', price_per_share=sales_bid_form.sell_asking_price.data,
                        share_amount=sales_bid_form.sell_shares_amount.data,
                        trader_name=user.user_name,
                        bid_status='pending')

        # Handle the bid before it saves to Database
        look_for_match = TradeBids.query.filter(TradeBids.bid_type == 'buy',
                                                TradeBids.price_per_share >= bid.price_per_share,
                                                TradeBids.share_amount >= bid.share_amount,
                                                TradeBids.trader_name != user.user_name,
                                                TradeBids.bid_status == 'pending'
                                                ).order_by(TradeBids.price_per_share).first()

        # We dont have a deal save the bid to DB
        if not look_for_match:
            db.session.add(bid)
            db.session.commit()
            return render_template('user_page.html', user=user, sell_form=sales_bid_form, buy_form=buy_bids_form)

        # We have a deal !!!! exchange shares
        if look_for_match:

            # Update the buyer total share
            buyer = Users.query.filter_by(user_name=look_for_match.trader_name).first()
            Users.query.filter_by(user_name=look_for_match.trader_name).update(
                dict(number_of_shares=buyer.number_of_shares + bid.share_amount))
            db.session.commit()

            # Update the seller total share
            Users.query.filter_by(user_name=user.user_name).update(
                dict(number_of_shares=user.number_of_shares - bid.share_amount))
            db.session.commit()

            # Update the buyer bid
            bid_id_to_update = look_for_match.id
            TradeBids.query.filter_by(id=bid_id_to_update).update(
                dict(share_amount=look_for_match.share_amount - bid.share_amount))
            if TradeBids.query.filter_by(id=bid_id_to_update).first().share_amount == 0:
                TradeBids.query.filter_by(id=bid_id_to_update).update(
                    dict(bid_status='expired'))

            db.session.commit()

    return render_template('user_page.html', user=user, sell_form=sales_bid_form, buy_form=buy_bids_form)


@app.route('/users_and_bids_tables')
def users_and_bids_tables():
    users = Users.query.all()
    bids = TradeBids.query.all()
    return render_template('all.html', users=users, bids=bids)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_values')
def get_values():
    pass
    # user_name = session.get('name', None)
    # a = Users.query.filter_by(user_name=user_name).first()
    # user_number_of_shaers = a.number_of_shares
    #
    return jsonify(result='hi')


@app.route('/get_monty')
def get_monty():
    a = session.get('my_var', None)
    # a = Users.query.filter_by(user_name=user).first()
    # user_number_of_shaers = a.number_of_shares
    print(a)

    return jsonify(result=a)


@app.route('/table')
def table():
    headings = ('Id', 'User Name', 'Bid Type', 'Price Per Share' 'Share Amount', 'Bid Status')
    data = TradeBids.query.all()
    users_headings = ('Id', 'User Name', 'Number Of Shares')
    users_data = Users.query.all()
    return render_template('table.html', headings=headings, data=data, users_headings=users_headings,
                           users_data=users_data)


if __name__ == '__main__':
    app.run(debug=True)
