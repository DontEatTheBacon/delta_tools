import json
from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional

import requests

url = 'https://api.collegescheduler.com/graphql'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
}

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
class Course:
    """ Object representation of a SJDC course """
    id: str
    subject_id: str
    course_number: str
    title: str

    def __repr__(self):
        return '<Course {} {}>'.format(self.subject_id, self.course_number)

    @classmethod
    def _from_graphql(cls, data: dict) -> 'Course':
        return cls(
            id=data['courseId'],
            subject_id=data['subjectId'],
            course_number=data['courseNumber'],
            title=data['title']
        )

def get_sections(course_id, count=100, include_full=True) -> List[Section]:
    r = requests.post(
        url = url,
        headers = headers,
        json = {
            'query': 'query CourseDetailsQuery_Query(\n  $environment: String!\n  $courseId: ID!\n  $count: Int\n  $cursor: String\n  $facets: [SearchFacetCriteria]\n  $includeFullCourses: Boolean\n  $registrationNumber: String\n  $freeTextbook: Boolean\n  $lowCostTextbook: Boolean\n  $instructor: String\n) {\n  environment(name: $environment) {\n    ...CourseDetailsContainer_environment_1G22uz\n    id\n  }\n}\n\nfragment CourseDetailsContainer_environment_1G22uz on Environment {\n  publicSettings {\n    sectionFieldTextSettings {\n      credits\n    }\n    id\n  }\n  ...SectionTableContainer_environment_1G22uz\n}\n\nfragment SectionTableContainer_environment_1G22uz on Environment {\n  publicSettings {\n    styleSettings {\n      primaryColor\n      freeTextbookFlagColor\n      lowCostTextbookFlagColor\n    }\n    courseSearchSettings {\n      sectionFields\n      dropDownOptionsLimit\n    }\n    filterSettings {\n      campusSelectionPrefixes\n    }\n    courseSettings {\n      flags {\n        key\n        text\n        sectionText\n        sectionTooltip\n        showOnSection\n      }\n    }\n    sectionFieldTextSettings {\n      campus\n      component\n      credits\n      dates\n      days\n      freeTextbookIndicated\n      lowCostTextbookIndicated\n      instructionMode\n      careers\n      partsOfTerm\n      instructorPlural\n      location\n      openSeats\n      registrationNumber\n      rooms\n      times\n    }\n    sectionSettings {\n      locationFormat\n    }\n    textSettings {\n      academicCareerPlural\n      mondayAbbr\n      tuesdayAbbr\n      wednesdayAbbr\n      thursdayAbbr\n      fridayAbbr\n      saturdayAbbr\n      sundayAbbr\n    }\n    id\n  }\n  getCourseSections(courseId: $courseId, first: $count, after: $cursor, facets: $facets, includeFullSections: $includeFullCourses, registrationNumber: $registrationNumber, freeTextbook: $freeTextbook, lowCostTextbook: $lowCostTextbook, instructor: $instructor) {\n    totalSections\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    edges {\n      cursor\n      node {\n        id\n        registrationNumber\n        instructors\n        instructionMode\n        careers\n        openSeats\n        totalSeats\n        campus\n        location\n        component\n        freeTextbookAvailable\n        lowCostTextbookAvailable\n        meetings {\n          room\n          building\n          buildingCode\n          buildingDescription\n          days\n          startDate\n          endDate\n          startTime\n          endTime\n        }\n        __typename\n      }\n    }\n    ...SectionFacetsContainer_getCourseSections\n  }\n  ...FacetsSettingsContainer_environment\n}\n\nfragment SectionFacetsContainer_getCourseSections on SearchSectionConnection {\n  facetFieldResults {\n    facetField\n    facetFieldValueResults {\n      value\n      selected\n      sectionCount\n    }\n  }\n}\n\nfragment FacetsSettingsContainer_environment on Environment {\n  publicSettings {\n    textSettings {\n      campus\n      campusPlural\n      courseStatus\n      academicCareerPlural\n      freeTextbook\n      freeTextbookInstructions\n      partsOfTermPlural\n      sessionPlural\n      instructionModePlural\n      instructor\n      locationPlural\n    }\n    sectionFieldTextSettings {\n      registrationNumber\n    }\n    courseSearchSettings {\n      courseSearchFilters\n      dropDownOptionsLimit\n    }\n    filterSettings {\n      campusSelectionPrefixes\n    }\n    id\n  }\n}\n',
            'variables': {
                'environment': 'deltacollege',
                'courseId': course_id,
                'count': count,
                'cursor': None,
                'facets': [],
                'includeFullCourses': include_full,
                'registrationNumber': None,
                'freeTextbook': None,
                'lowCostTextbook': None,
                'instructor': ''
            }
        })

    try:
        data = json.loads(r.text)['data']['environment']['getCourseSections']['edges']
        course_name = get_course_name(course_id)

        sections = []
        for section_data in map(lambda item: item['node'], data):
            section = Section._from_graphql(section_data)
            section._set_course_name(course_name)
            section._set_course_id(course_id)
            sections.append(section)
        return sections
    except Exception as e:
        print(e)
        return []

def get_course_name(course_id) -> str:
    r = requests.post(
        url = url,
        headers = headers,
        json = {
            "query":"query routes_CourseContainer_Query(\n  $courseId: ID!\n) {\n  course: node(id: $courseId) {\n    __typename\n    ...CourseContainer_course\n    id\n  }\n}\n\nfragment CourseContainer_course on SearchCourse {\n  id\n  subject {\n    id\n  }\n  term {\n    code\n    id\n  }\n  courseNumber\n  title\n  description\n  creditsMin\n  creditsMax\n}\n",
            "variables": {
                "courseId": course_id
            }
        }
    )

    try:
        data = json.loads(r.text)['data']['course']
        return '{} {}'.format(data['subject']['id'], data['courseNumber'])
    except:
        return 'Null'

def search_course(query, count=100) -> List[Course]:
    """ Find courses via a text query """
    r = requests.post(
        url = url,
        headers = headers,
        json = {
            "query": "query SearchAutoCompleteQuery_Query(\n  $environment: String!\n  $termCode: String!\n  $prefix: String!\n  $size: Int\n) {\n  environment(name: $environment) {\n    courses: suggestCourses(termCode: $termCode, prefix: $prefix, size: $size) {\n      courseId\n      subjectId\n      courseNumber\n      title\n    }\n    id\n  }\n}\n",
            "variables": {
                "environment":"deltacollege",
                "termCode":"2263",
                "prefix": query,
                "size": count
            }
        }
    )

    try:
        data = json.loads(r.text)['data']['environment']['courses']

        courses = []
        for course_data in data:
            courses.append(
                Course._from_graphql(course_data)
            )
        courses.sort(key=lambda course: course.course_number)
        return courses

    except:
        return []

def get_section(course_id, section_id) -> Optional[Section]:
    r = requests.post(
        url = url,
        headers = headers,
        json = {
            "query":"query routes_SectionContainer_Query(\n  $environment: String!\n  $courseId: ID!\n  $sectionId: ID!\n) {\n  environment(name: $environment) {\n    ...SectionContainer_environment\n    id\n  }\n  course: node(id: $courseId) {\n    __typename\n    ...SectionContainer_course\n    id\n  }\n  section: node(id: $sectionId) {\n    __typename\n    ...SectionContainer_section\n    id\n  }\n}\n\nfragment SectionContainer_environment on Environment {\n  publicSettings {\n    styleSettings {\n      freeTextbookImageFileName\n      lowCostTextbookImageFileName\n    }\n    courseSearchSettings {\n      sectionFields\n      sectionFooterEntries\n      dropDownOptionsLimit\n    }\n    filterSettings {\n      campusSelectionPrefixes\n    }\n    sectionSettings {\n      locationFormat\n    }\n    sectionFieldTextSettings {\n      campus\n      component\n      credits\n      dates\n      days\n      freeTextbookIndicated\n      lowCostTextbookIndicated\n      instructionMode\n      careers\n      instructorPlural\n      location\n      openSeats\n      registrationNumber\n      rooms\n      times\n    }\n    textSettings {\n      academicCareerPlural\n      mondayAbbr\n      tuesdayAbbr\n      wednesdayAbbr\n      thursdayAbbr\n      fridayAbbr\n      saturdayAbbr\n      sundayAbbr\n    }\n    id\n  }\n}\n\nfragment SectionContainer_course on Node {\n  ... on SearchCourse {\n    courseNumber\n    title\n    subject {\n      id\n    }\n    term {\n      code\n      id\n    }\n  }\n}\n\nfragment SectionContainer_section on Node {\n  ... on SearchSection {\n    id\n    registrationNumber\n    sectionNumber\n    startDate\n    endDate\n    instructors\n    instructionMode\n    careers\n    partsOfTerm\n    courseTypeDescription\n    creditsMin\n    creditsMax\n    openSeats\n    totalSeats\n    campus\n    location\n    component\n    freeTextbookAvailable\n    lowCostTextbookAvailable\n    meetings {\n      room\n      building\n      buildingCode\n      buildingDescription\n      days\n      startDate\n      endDate\n      startTime\n      endTime\n    }\n  }\n}\n",
            "variables": {
                "environment":"deltacollege",
                "courseId": course_id,
                "sectionId": section_id
            }
        }
    )

    try:
        data = json.loads(r.text)['data']
        section = Section._from_graphql(data['section'])
        course_name = get_course_name(course_id)
        section._set_course_name(course_name)
        section._set_course_id(course_id)
        return section
    except:
        return None

if __name__ == '__main__':
    section = get_section('U2VhcmNoQ291cnNlOmRlbHRhY29sbGVnZTpNakkxTnpwTlFWUklPak09', 'U2VhcmNoU2VjdGlvbjpkZWx0YWNvbGxlZ2U6TWpJMU56cE5RVlJJT2pNNk56QXlPRGc9')
    print(section)