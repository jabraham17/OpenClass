import sqlite3
import os
import re

# this provides interface to database without need for sql statements elsewhere
# this class DOES NOT check user input
class Database:
    def __init__(self):
        self.filepath = 'openclass.db'
        self.connection = None
    
    # open the database
    def open(self):

        # check if file exists
        new_table = not os.path.exists(self.filepath)

        # if no existing connection
        if self.connection is None:
            self.connection = sqlite3.connect(self.filepath)

        # if we have a new table, run sql cmds to create a new table
        if new_table:
            self.create_new_table()
    
    def create_new_table(self):
        # create users table
        self.execute_sql("""
            CREATE TABLE user (
                email TEXT PRIMARY KEY
            );
        """)
        # create course table
        self.execute_sql("""
            CREATE TABLE course (
                subject TEXT NOT NULL,
                code TEXT NOT NULL,
                section TEXT NOT NULL,
                id TEXT PRIMARY KEY,
                previousStatus INTEGER NOT NULL DEFAULT 0
            );
        """)
        # create track table
        self.execute_sql("""
            CREATE TABLE track (
                user TEXT NOT NULL,
                course TEXT NOT NULL,
                id INTEGER PRIMARY KEY,
                FOREIGN KEY(user) REFERENCES user(email),
                FOREIGN KEY(course) REFERENCES course(id)
            );
        """)

    def execute_sql(self, statement):
        cursor = self.connection.cursor()
        cursor.execute(statement)
        return cursor.fetchall()

    def add_user(self, email):
        self.execute_sql(f"""
            INSERT INTO user (email)
            VALUES ('{email}');
        """)

    def remove_user(self, email):
        self.execute_sql(f"""
            DELETE FROM user
            WHERE user == '{email}';
        """)

    def remove_course(self, courseid):
        self.execute_sql(f"""
            DELETE FROM course
            WHERE id == '{courseid}';
        """)

    def add_course(self, subject, code, section, status):
        ID = str(subject) + str(code) + str(section)
        self.execute_sql(f"""
            INSERT INTO course (subject, code, section, id, previousStatus)
            VALUES ('{subject}', '{code}', '{section}', '{ID}', {int(status)});
        """)

    # add a track row
    # assumes course and id already exist
    def watch_course(self, userid, courseid):
        self.execute_sql(f"""
            INSERT INTO track (user, course)
            VALUES ('{userid}', '{courseid}');
        """)

    # remove a user from watching a course
    def unwatch_course(self, userid, courseid):
        self.execute_sql(f"""
            DELETE FROM track
            WHERE user == '{userid}' AND course == '{courseid}';
        """)

    def get_status(self, courseid):
        return self.execute_sql(f"""
            SELECT previousStatus FROM course
            WHERE id == '{courseid}';
        """)

    def update_status(self, newstatus, courseid):
        self.execute_sql(f"""
            UPDATE course
            SET previousStatus = '{newstatus}'
            WHERE id == '{courseid}';
        """)

    def all_courses(self):
        return self.execute_sql("""
            SELECT * FROM course;
        """)

    def all_users(self):
        return self.execute_sql("""
            SELECT * FROM user;
        """)

    def all_tracks(self):
        return self.execute_sql("""
            SELECT * FROM track;
        """)

    def get_user(self, email):
        return self.execute_sql(f"""
            SELECT * FROM user
            where email == '{email}';
        """)

    def get_course(self, ID):
        return self.execute_sql(f"""
            SELECT * FROM course
            where id == '{ID}';
        """)

    def get_track(self, courseid, userid):
        return self.execute_sql(f"""
            SELECT * FROM track
            where user == '{userid}' AND course == '{courseid}';
        """)
    
    # all tracks that are associated with the course
    def course_used(self, courseid):
        return self.execute_sql(f"""
            SELECT * FROM track
            where course == '{courseid}';
        """)
    
    # all users that are associated with this course
    def associated_users(self, courseid):
        return self.execute_sql(f"""
            SELECT user FROM track
            where course == '{courseid}';
        """)

    # all tracks that are associated with the user
    def user_used(self, userid):
        return self.execute_sql(f"""
            SELECT * FROM track
            where user == '{userid}';
        """)

    # close the database
    def close(self):
        # if there is a connection, close it
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
            self.connection = None