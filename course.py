
class Course:
    def __init__(self, subject, code, section, previousState):
        self.subject = subject
        self.code = code
        self.section = section
        self.previousState = previousState
    
    def makeID(self, subject, code, section):
        return str(subject) + str(code) + str(section)
