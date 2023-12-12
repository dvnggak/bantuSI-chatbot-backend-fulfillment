import mysql.connector

global cnx

# create a connection to the database
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="chatbotadmin"
)

def check_user_exists(nim: int):
    # create a cursor object 
    cursor = cnx.cursor()
    
    # create a query to check if the user exists in the database
    query = "SELECT name FROM students WHERE nim = %s"
    # execute the query
    cursor.execute(query, (nim,))

    # fetch the result
    result = cursor.fetchone()

    # close the cursor and connection
    cursor.close()

    # if the user exists, return the user's name
    if result:
        return result[0]   
    else:
        return None

def get_subjects(subject_code: int):
    # create a cursor object 
    cursor = cnx.cursor()
    
    # create a query to check if the user exists in the database
    query = "SELECT * FROM subjects WHERE subject_code = %s"
    # execute the query
    cursor.execute(query, (subject_code,))

    # fetch the result
    result = cursor.fetchone()

    # close the cursor and connection
    cursor.close()

    # return all the subjects 
    return result

def get_lecturers():
    # create a cursor object 
    cursor = cnx.cursor()
    
    # create a query to check if the user exists in the database
    query = "SELECT * FROM lecturers"
    # execute the query
    cursor.execute(query)

    # fetch the result
    result = cursor.fetchall()

    # close the cursor and connection
    cursor.close()

    # return all the lecturers 
    return result

def get_profile():
    # create a cursor object 
    cursor = cnx.cursor()
    
    # create a query to check if the user exists in the database
    query = "SELECT * FROM majoring_profiles"
    # execute the query
    cursor.execute(query)

    # fetch the result
    result = cursor.fetchone()

    # close the cursor and connection
    cursor.close()

    # return all the profile 
    return result

def get_newest_announcements():
    # create a cursor object 
    cursor = cnx.cursor()
    
    # create a query to get 1 newest announcements
    query = "SELECT * FROM announcements ORDER BY id DESC LIMIT 1"

    # execute the query
    cursor.execute(query)

    # fetch the result
    result = cursor.fetchone()

    # close the cursor and connection
    cursor.close()

    # return all the announcements
    return result

def get_announcements_with_category(category: str):
    # create a cursor object 
    cursor = cnx.cursor()
    
    # create a query to get all announcements with category
    query = "SELECT * FROM announcements WHERE category = %s"

    # execute the query
    cursor.execute(query, (category,))

    # fetch the result
    result = cursor.fetchall()

    # close the cursor and connection
    cursor.close()

    # return all the announcements
    return result