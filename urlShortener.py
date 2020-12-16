#-------------------------------------------
#   URL Short
#
#
#
#



#------------------------------
#   Imports
#------------------------------

import string
import sqlite3
import pathlib
from flask import Flask, request, render_template, redirect

#-------------------------------
#   Variables
#-------------------------------

legalChars = string.digits + string.ascii_lowercase + string.ascii_uppercase
host = 'http://localhost:5000/'
dbPath = str(pathlib.Path().absolute()) + "\\urls.db"

#-------------------------------
#   Base 62 Conversion Functions
#--------------------------------

#Recursive function that converts int to string representing
#   Base 62 number [0-9][a-z][A-Z]
def convertToBase62(num):
    remainder = num % 62
    quotient = num//62
    if quotient:
        return convertToBase62(quotient) + legalChars[remainder]
    return legalChars[remainder]
    
#Takes a string that represents base 62-number
#   Converts the string to base 10 integer and returns it
def convertToBase10(num):
    sum = 0
    for i in range(len(num)):
        print(num[i] + ": Value = " + str(legalChars.find(num[i])))
        sum += legalChars.find(num[i]) * 62**i
    return sum

#------------------------------
#   SQL Functs
#------------------------------

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

def create_table(connection):
    create_users_table = """
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        longURL TEXT NOT NULL
    );
    """
    execute_query(connection, create_users_table)

def addNewLink(link):
    add_link = """
    INSERT INTO
        links (longURL)
    VALUES
        ('{}')
    """.format(link)
    with sqlite3.connect(dbPath) as conn:
        cursor = conn.cursor()
        result_cursor = cursor.execute(add_link)
        shortLink = host + convertToBase62(result_cursor.lastrowid)

    return shortLink

def getLongLink(id):
    longURL = host
    with sqlite3.connect(dbPath) as conn:
        cursor = conn.cursor()
        select_row = """
                SELECT longURL FROM links
                    WHERE ID=%s
                """%(id)
        result_cursor = cursor.execute(select_row)
        try:
            longURL = result_cursor.fetchone()[0]
        except Exception as e:
            print(e)
    return longURL



#------------------------------
#   Flask Functions
#------------------------------
app = Flask(__name__, template_folder="templates")

# This creates the home page and handles post requests
#   For form submissions to shorten URL
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form.get('url')
        # if urlparse(original_url).scheme == '':
        #     original_url = 'http://' + original_url
        shortURL = addNewLink(original_url)
            
        return render_template("home.html",short_url= shortURL)
    return render_template("home.html")

#Handles the accessing of short URLS
@app.route('/<short_url>')
def redirect_short_url(short_url):
    long_url = getLongLink(convertToBase10(short_url))
    print("Short: " + short_url)
    print("Long: " + long_url)
    if "http://" not in long_url:
        return redirect("http://"+long_url, code=302)
    return redirect(long_url, code=302)

#----------------------------
#   Main
#----------------------------

if __name__ == '__main__':
    
    #Connects to url database
    print("Connecting to Database...")
    connection = create_connection(dbPath)
    
    #Creates tAble
    print("\nChecking Tables")
    create_table(connection)

    print("\nLaunching Website")
    #app.run(debug=True)
    
    print(convertToBase62(63))
    print(convertToBase10("Z"))
    print(convertToBase10(convertToBase62(12345678)))
