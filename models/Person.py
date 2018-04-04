class Person:

    name = ''
    gender = ''
    dob = ''
    job = ''
    nationality = ''
    birthplace = ''
    desc = ''
    url = ''

    def __init__(self, name, gender, dob, job, nationality, birthplace, desc, url):
        self.name = name
        self.gender = gender,
        self.dob = dob,
        self.job = job,
        self.nationality = nationality,
        self.birthplace = birthplace,
        self.desc = desc,
        self.url = url

    def print_person(self):
        print("name: ", self.name)
