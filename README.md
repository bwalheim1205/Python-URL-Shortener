# Python URL Shortener
 Using Python's Flask module in oder to make a webpage for URL Shorterning. Long URLs are stored in SQL database using the sqlite3 module. The long urls are given index when added into SQL table which is then converted from int to string representing base 62 number which is used as short URL. Flask site also handles redirects by converting base 62 number back to integer index to access long url and redirect.
# Installation
Use these commands to install necessary packages
 ```
 pip install sqlite3
 pip install flask
 ```
# Base 62 Encoding
Uses recursion to convert integer to string representing base 62 number
```python
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
```

# Base 62 Decoding
Iteratively converts string representing base 62 number to integer
```python
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
```
# SQL Functions
Creates a connection to SQLite database. If db file does not exists it will create a db file.
```python
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
```
This functions takes connection to SQLlite database and a string which is SQL querry and executes it on the database
```python
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
```
# Create SQL Table
Creates a SQLite table with id which is uniquer integer and long url which is string for stored url
```python
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
```
# Adding URL to SQL Database
Takes input of a string and adds the url to SQLite database and returns short URL created by converting the index in database converted to base 62.
```python
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
```
# Retriving URL from SQL Database
Takes integer id and finds the corresponding url in SQLite database and returns URL.
```python
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
```

# Flask Home Page
Flask function that handles the home page which handles form for creating new short URL.
```python
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
```
# Flask Page Redirect
Flask page the redrection of short URL which is called when directed to host/[shortURL]
```python
'''Handles the redirecting of short URLS'''
@app.route('/<short_url>')
def redirect_short_url(short_url):
    long_url = getLongLink(convertToBase10(short_url))
    if "http://" not in long_url:
        return redirect("http://"+long_url, code=302)
    return redirect(long_url, code=302)
```
