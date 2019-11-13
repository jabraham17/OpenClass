
from database import Database
import send_email as email
import openclass
from pprint import pprint

def process_new_emails(db, emails):
    """
    Process new emails

    format for email is (sender, subject, body)

    if subject is track, add a track
    if subject is untrack, stop tracking
    """

    for m in emails:
        # if no sender, fail
        if m[0] == '':
            # cant recover with no email, fail
            # should never happen
            break
        course = parse_body(m[2])
        if len(course) != 3:
            # invalid course
            send_email(m[0], 'Course Track Failure', 'Failed to execute: invalid input')
        if m[1] == 'TRACK':
            track(db, m[0], course)
        elif m[1] == 'UNTRACK':
            untrack(db, m[0], course)
        else:
            send_email(m[0], 'Course Track Failure', 'Failed to execute: unknown command')

def parse_body(body):
    """
    convert body which is "subject code section" to a tuple
    """
    return tuple(body.split(" "))

def track(db, sender, course):
    """
    add the user if doesn't exist
    add the course if it doesn't exists
    add the row from the tracking table
    """
    db.open()
    # check if user exists
    if not db.get_user(sender):
        # no user, add the user
        db.add_user(sender)
    # check if course exists
    courseid = str(course[0])+str(course[1])+str(course[2])
    if not db.get_course(courseid):
        # no user, add the user, initial status is -1 for unknown
        db.add_course(course[0], course[1], course[2], -1)
    
    # check that not already tracking
    if not db.get_track(courseid, sender):
        # not already tracking, track
        db.watch_course(sender, courseid)

    db.close()

def untrack(db, sender, course):
    """
    remove the row from the tracking table
    remove the user if unused
    remove the course if unused
    """
    db.open()
    courseid = str(course[0])+str(course[1])+str(course[2])

    # check that row exists
    if db.get_track(courseid, sender):
        # not already tracking, track
        db.unwatch_course(sender, courseid)
    
    # check if user is unused
    if not db.user_used(sender):
        # unused, remove
        db.remove_user(sender)
    
    # check if course is unused
    if not db.course_used(courseid):
        # unused, remove
        db.remove_course(courseid)
    
    db.close()

def send_email(recp, subject, msg):
    creds = email.get_creds()
    sender = f'"COURSE TRACKER" <rpi.notify.system@gmail.com>'
    email.send_email(creds, sender, recp, subject, msg)

def check_status(course):
    """
    check the current status of the course
    """
    query = openclass.get_query_str()
    semester = '2201' # changes every semester
    html = openclass.get_html(query, course[0], course[1], course[2], semester)
    parser = openclass.get_parser(html)
    status = openclass.class_status(parser)
    return status

def main():
    """
    Runs everything

    Workflow:
    1. Check for new emails
    2. Apply actions from email (track/untrack)
    3. Check for status changes to watched class
    4. Update database with new status
    5. end notification emails

    Will run once, another program will be used to run periodically (cron)
    """

    # init the database
    db = Database()

    # check for new emails
    creds = email.get_creds()
    # STEP 1
    new_emails = email.check_email(creds)
    if new_emails:
        # we have new emails, need to mark them as unread and process
        ids = [m[1] for m in new_emails]
        email.mark_as_read(creds, ids)
        email_contents = [m[0] for m in new_emails]
        # STEP 2
        process_new_emails(db, email_contents)
    
    # STEP 3
    # get all courses
    db.open()
    all_courses = db.all_courses()
    # now we get the new status of all courses
    all_course_with_status = [c + (int(check_status(c[:3])),) for c in all_courses]
    db.close()

    # STEP 4
    # need to separate into 3 lists
    # list A: all courses with previous status -1, these are new course, they just get initlizated
    # list B: all courses with a change of status from open to close
    # list C: all courses with a change of status from close to open
    # everything else has no change, no need to do anything

    A = [c for c in all_course_with_status if c[-2] == -1]
    B = [c for c in all_course_with_status if c[-2] == 1 and c[-1] == 0]
    C = [c for c in all_course_with_status if c[-2] == 0 and c[-1] == 1]

    db.open()
    # for all lists, just update the status
    for c in (A+B+C):
        db.update_status(c[-1], c[-3])

    # for list B and C, need to figure out all users who care about it
    B = [c + (db.associated_users(c[-3]),) for c in B]
    C = [c + (db.associated_users(c[-3]),) for c in C]

    # for each course in B, inform the users the clsss is now closed
    for c in B:
        for u in c[-1]:
            # u is a tuple with 1 element
            user = u[0]
            send_email(user, "Course is closed", f"Your course {c[0]} {c[1]} {c[2]} is now closed")
    
    # for each course in B, inform the users the clsss is now open
    for c in C:
        for u in c[-1]:
            # u is a tuple with 1 element
            user = u[0]
            send_email(user, "Course is open", f"Your course {c[0]} {c[1]} {c[2]} is now open")

    db.close()


if __name__ == '__main__':
    main()