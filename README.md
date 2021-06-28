# STOCK MARKET



The stock market app simulates a simple stock exchange broker where users can buy and sell shares.

### Installation
To install and run  this app, follow the following steps:

1. clone this repo to your chosen directory.
2. you will need to install python3 on your machine. You can follow this guide. `https://www.python.org/downloads/`
3. Install dependencies 'python -m pip install -r requirements.txt'
4. run 'flask run' from the repo directory. e.g `(venv) C:\Users\landa\Desktop\stock-market>flask run`

# Using the app:

First, you'll have to register or log in:
Go to ` http://127.0.0.1:5000/` and enter a user name, 
If the User exists, he will be redirected to his user page. If the User doesn't exist, it will create a new user and turn to his user page.

### initial user 
admin_1 User holds the initial amount of 1000 shares, consider the first login with admin_1 User and offer some shares for sale.

For trading in stocks, the assumption is that a user has an infinite amount of funds.

You can make a buy or sell offer given you have enough shares to sell.

Note:
The User can not sell shares he doesn't have and cannot offer more shares in total (even in different quotes) than he have.

After the User makes a bid, the stock market will look for an offer that meets the requirements (regarding price and share quantity),
If it finds a match, the deal is executed. Else the user offer will be pending and wait for a match from another user.

The "owner" of the app can find the admin dashboard at `http://127.0.0.1:5000/admin_dashboard` This dashboard is only for the admin to monitor all the bids and users.
For now, it is not secure.

Since this app runs locally on the machine:
For seeing the User shares updated "live" when other user exchange stocks with him, 
You will have to use the incognito tab for users or other browsers, not potentially mess up the session.
