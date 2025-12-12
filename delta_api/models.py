from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional


@dataclass
class Section:
    """ Object representation of a SJDC section """
    id: str
    section_number: int
    instructors: Optional[List[str]]
    instruction_mode: Optional[str]
    careers: List[str]
    open_seats: int
    total_seats: int
    campus: Optional[str]
    component: Optional[str]
    free_textbook: bool
    low_cost_textbook: bool
    room: Optional[int]
    building: Optional[str]
    days: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    # non-JSON initialized attributes
    course_name: Optional[str]
    course_id: Optional[str]

    def is_full(self) -> bool:
        return self.open_seats < 1
    
    def is_open(self) -> bool:
        return self.open_seats > 0

    def __repr__(self):
        return '<Section {}>'.format(self.section_number)

    def _set_course_name(self, course_name):
        self.course_name = course_name

    def _set_course_id(self, course_id):
        self.course_id = course_id

    @classmethod
    def _from_graphql(cls, data: dict) -> 'Section':
        def parse_time(time_data):
            hour = time_data // 100
            minute = time_data % 100
            return time(hour=hour, minute=minute)

        meeting_data: dict = data['meetings'][0]

        return cls(
            id=data['id'],
            section_number=int(data['registrationNumber']),
            instructors=data.get('instructors', []),
            instruction_mode=data.get('instructionMode', None),
            careers=data.get('careers', []),
            open_seats=data.get('openSeats', 0),
            total_seats=data.get('totalSeats', 0),
            campus=data.get('campus', None),
            component=data.get('component', None),
            free_textbook=data.get('freeTextbookAvailable', False),
            low_cost_textbook=data.get('lowCostTextbookAvailable', False),

            room=meeting_data['room'] if meeting_data.get('room') else None,
            building=meeting_data.get('buildingCode', None),
            days=meeting_data.get('days', ''),

            start_date=date.fromisoformat(meeting_data['startDate']),
            end_date=date.fromisoformat(meeting_data['endDate']),

            start_time=parse_time(meeting_data.get('startTime', 0)),
            end_time=parse_time(meeting_data.get('endTime', 0)),

            course_id=None,
            course_name=None
        )

@dataclass
class Term:
    """ Object representation of a SJDC term """
    code: int
    name: str
    id: str

    def __repr__(self):
        return '<Term {}>'.format(self.name)

    @classmethod
    def _from_graphql(cls, data: dict) -> 'Term':
        return cls(
            code=int(data['code']),
            name=data.get('name', 'null'),
            id=data['id']
        )
    
@dataclass
class Course:
    """ Object representation of a SJDC course """
    id: str
    subject_id: str
    course_number: str
    title: str
    
    term: Optional[Term] = None

    def __repr__(self):
        return '<Course {} {}>'.format(self.subject_id, self.course_number)

    def _set_term(self, term: Term):
        self.term = term

    @classmethod
    def _from_graphql(cls, data: dict) -> 'Course':
        return cls(
            id=data['courseId'],
            subject_id=data['subjectId'],
            course_number=data['courseNumber'],
            title=data['title']
        )
    
@dataclass
class Instructor:
    """ Object representation of a SJDC instructor """
    id: str
    courses: List[Course]
    name: str = 'null'
    term_code: Optional['Term'] = None

    def __repr__(self):
        return '<Instructor {}>'.format(self.name)
    
    def _set_term(self, term: Term):
        self.term = term
        for course in self.courses:
            course._set_term(term)
    
    def _set_name(self, name: str):
        self.name = name

    @classmethod
    def _from_graphql(cls, data: dict) -> 'Instructor':
        courses = []
        for course_data in data['findCourses']['edges']:
            courses.append(
                Course(id=course_data['node']['id'], 
                       subject_id=course_data['node']['subject']['id'], 
                       course_number=course_data['node']['courseNumber'], 
                       title=course_data['node']['title'])
            )
        courses.sort(key=lambda course: course.course_number)
        return cls(
            id=data['id'],
            courses=courses
        )