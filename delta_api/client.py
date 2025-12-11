from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional
from functools import lru_cache

import requests

from delta_api.queries import (
    COURSE_DETAILS_QUERY,
    GET_COURSE_NAME_QUERY,
    GET_TERMS_QUERY,
    SEARCH_COURSE_QUERY,
    GET_SECTION_QUERY,
    GET_INSTRUCTOR_QUERY,
)

from delta_api.models import Course, Section, Term, Instructor

class DeltaAPI:
    def __init__(self):
        self.environment = 'deltacollege'
        self.url = 'https://api.collegescheduler.com/graphql'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            ' AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/141.0.0.0 Safari/537.36'
        }

    @property
    def current_term(self) -> Term:
        if not hasattr(self, '_current_term'):
            terms = self.get_terms()
            self._current_term = terms[0] if terms else None
        return self._current_term

    def _request(self, query: str, variables: dict):
        r = requests.post(
            url = self.url,
            headers = self.headers,
            json= {
                'query': query, 
                'variables': variables
            }
        )
        data = r.json()
        if "errors" in data:
            raise Exception(data["errors"][0]["message"])
        return data
    
    def get_sections(self, course_id, count=100, include_full=True) -> List[Section]:
        data = self._request(
            COURSE_DETAILS_QUERY,                        
            {
                'environment': self.environment,
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
        )

        try:
            course_name = self.get_course_name(course_id) or 'null'

            sections = []
            for section_data in map(lambda section: section['node'], data['data']['environment']['getCourseSections']['edges']):
                section = Section._from_graphql(section_data)
                section._set_course_name(course_name)
                section._set_course_id(course_id)
                sections.append(section)
            return sections
        except Exception as e:
            print(f"Error fetching sections for course {course_id}: {e}")
            return []

    @lru_cache(maxsize=128)
    def get_course_name(self, course_id) -> Optional[str]:
        data = self._request(
            GET_COURSE_NAME_QUERY,
            {
                "courseId": course_id
            }
        )

        try:
            course_data = data['data']['course']
            return '{} {}'.format(course_data['subject']['id'], course_data['courseNumber'])
        except Exception as e:
            print(f"Error fetching course name for {course_id}: {e}")
            return None

    def get_terms(self) -> List[Term]:
        data = self._request(
            GET_TERMS_QUERY,
            {
                "environment": self.environment            
            }
        )
        try:
            search_terms_data = data['data']['environment']['courseSearchTerms']
            terms = []
            for term_data in search_terms_data:
                terms.append(
                    Term._from_graphql(term_data)
                )
            # newest term first
            terms.sort(key=lambda term: term.code, reverse=True)
            return terms
        except Exception as e:
            print(f"Error fetching terms: {e}")
            return []

    @lru_cache(maxsize=128)
    def search_course(self, query: str, count=100, term: Optional[Term]=None) -> List[Course]:
        data = self._request(
            SEARCH_COURSE_QUERY,
            {
                "environment":self.environment,
                "termCode": term.code if term else self.current_term.code,
                "prefix": query,
                "size": count
            }
        )

        try:
            search_data = data['data']['environment']['courses']

            courses = []
            for course_data in search_data:
                courses.append(
                    Course._from_graphql(course_data)
                )
            courses.sort(key=lambda course: course.course_number)
            return courses
        except Exception as e:
            print(f"Error searching courses with query '{query}': {e}")
            return []

    def get_section(self, course_id: str, section_id: str) -> Optional[Section]:
        data = self._request(
            GET_SECTION_QUERY,
            {
                "environment": self.environment,
                "courseId": course_id,
                "sectionId": section_id
            }
        )

        try:
            section_data = data['data']['section']
            section = Section._from_graphql(section_data)
            course_name = self.get_course_name(course_id) or 'null'
            section._set_course_name(course_name)
            section._set_course_id(course_id)
            return section
        except Exception as e:
            print(f"Error fetching section {course_id} {section_id}: {e}")
            return None

    @lru_cache(maxsize=128)
    def get_instructor(self, name: str, term: Optional[Term]=None) -> Optional[Instructor]:
        data = self._request(
            GET_INSTRUCTOR_QUERY,
            {
                "environment": self.environment,
                "termCode": term.code if term else self.current_term.code,
                "count": 100,
                "cursor": None,
                "facets":
                [
                    {
                        "facetField": "INSTRUCTOR",
                        "selectedFilterValues":[name]
                    }
                ],
                "includeFullCourses": True
            }
        )

        try:
            instructor_data = data['data']['environment']
            instructor = Instructor._from_graphql(instructor_data)
            instructor._set_term(self.current_term)
            instructor._set_name(name)
            return instructor
        except Exception as e:
            print(f"Error fetching instructor {name}: {e}")
            return None

if __name__ == '__main__':
    delta_api = DeltaAPI()
    print(delta_api.search_course('math'))
    print(delta_api.get_terms())