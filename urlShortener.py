#-------------------------------------------
#   URL Shortner - Flask
#   
#   Author: Brian Walheim
#   Version: 1.0
#
#   Description: Creates a Flask webpage that acts as landing page to handle 
#       creating new short urls and then stores them in SQLite database. 
#       Flask and the SQLite database are also used to handle the url redirects.
#



#------------------------------
#   Imports

import string
import sqlite3
import pathlib
from flask import Flask, request, render_template, redirect

#-------------------------------
#   Variables


#List of 62 chars that can be used in short URL [0-9][a-z][A-z]
legalChars = string.digits + string.ascii_lowercase + string.ascii_uppercase

#Name of base url of application
host = 'http://localhost:5000/'

#Path to where database should be located
dbPath = str(pathlib.Path().absolute()) + "\\urls.db"


#-------------------------------
#   Base 62 Conversion Functions


'''
Recursive function that converts int to string representing 
    Base 62 number [0-9][a-z][A-Z]
Input:
    num- int to be converted to base 62
'''
def convertToBase62(num):
    remainder = num % 62
    quotient = num//62
    if quotient:
        return convertToBase62(quotient) + legalChars[remainder]
    return legalChars[remainder]
    

'''
Takes a string that represents base 62 number
   Converts the string to base 10 integer and returns it
Input
    num - string representing base 62 number
'''
def convertToBase10(num):
    sum = 0
    for i in range(len(num)):
        sum += legalChars.find(num[len(num)-1-i]) * 62**i
    return sum


#------------------------------
#   SQL Functs


'''
Connects to the SQL database and returns connection
'''
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

    return connection


'''
Executes a query on the SQLite database
Input:
    connection - connection to database
    query - SQL command to be executed
'''
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


'''
Creates links table unless it has already been created
Input:
    connection - connection to database
'''
def create_table(connection):
    create_users_table = """
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        longURL TEXT NOT NULL
    );
    """
    execute_query(connection, create_users_table)


'''
Adds a new link entry to SQL links table and returns shortened link
Input:
    link - String representing new URL
'''
def addNewLink(link):
    
    #SQL command for adding entry to table
    add_link = """
    INSERT INTO
        links (longURL)
    VALUES
        ('{}')
    """.format(link)

    #Connects to database and adds_link
    with sqlite3.connect(dbPath) as conn:
        cursor = conn.cursor()
        result_cursor = cursor.execute(add_link)
        shortLink = host + convertToBase62(result_cursor.lastrowid)

    return shortLink


'''
Retrieves longURL from 
'''
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

'''Starts flask application'''
app = Flask(__name__, template_folder="templates")

'''This creates the home page and handles post requests
    For form submissions to shorten URL
'''
@app.route('/', methods=['GET', 'POST'])
def home():

    #Handles form submissions for URL shorterning
    if request.method == 'POST':
        original_url = request.form.get('url')
        shortURL = addNewLink(original_url)
        return render_template("home.html",short_url= shortURL)

    #If get request renders template
    return render_template("home.html")


'''Handles the redirecting of short URLS'''
@app.route('/<short_url>')
def redirect_short_url(short_url):
    long_url = getLongLink(convertToBase10(short_url))
    if "http://" not in long_url:
        return redirect("http://"+long_url, code=302)
    return redirect(long_url, code=302)

#----------------------------
#   Main

if __name__ == '__main__':
    
    #Connects to url database
    print("Connecting to Database...")
    connection = create_connection(dbPath)
    
    #Creates tAble
    print("\nChecking Tables")
    create_table(connection)

    print("\nLaunching Website")
    app.run(debug=True)
