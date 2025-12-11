# ============================
#  Course Sections Query
# ============================
COURSE_DETAILS_QUERY = """
query CourseDetailsQuery_Query(
  $environment: String!
  $courseId: ID!
  $count: Int
  $cursor: String
  $facets: [SearchFacetCriteria]
  $includeFullCourses: Boolean
  $registrationNumber: String
  $freeTextbook: Boolean
  $lowCostTextbook: Boolean
  $instructor: String
) {
  environment(name: $environment) {
    ...CourseDetailsContainer_environment_1G22uz
    id
  }
}

fragment CourseDetailsContainer_environment_1G22uz on Environment {
  publicSettings {
    sectionFieldTextSettings {
      credits
    }
    id
  }
  ...SectionTableContainer_environment_1G22uz
}

fragment SectionTableContainer_environment_1G22uz on Environment {
  publicSettings {
    styleSettings {
      primaryColor
      freeTextbookFlagColor
      lowCostTextbookFlagColor
    }
    courseSearchSettings {
      sectionFields
      dropDownOptionsLimit
    }
    filterSettings {
      campusSelectionPrefixes
    }
    courseSettings {
      flags {
        key
        text
        sectionText
        sectionTooltip
        showOnSection
      }
    }
    sectionFieldTextSettings {
      campus
      component
      credits
      dates
      days
      freeTextbookIndicated
      lowCostTextbookIndicated
      instructionMode
      careers
      partsOfTerm
      instructorPlural
      location
      openSeats
      registrationNumber
      rooms
      times
    }
    sectionSettings {
      locationFormat
    }
    textSettings {
      academicCareerPlural
      mondayAbbr
      tuesdayAbbr
      wednesdayAbbr
      thursdayAbbr
      fridayAbbr
      saturdayAbbr
      sundayAbbr
    }
    id
  }
  getCourseSections(
    courseId: $courseId,
    first: $count,
    after: $cursor,
    facets: $facets,
    includeFullSections: $includeFullCourses,
    registrationNumber: $registrationNumber,
    freeTextbook: $freeTextbook,
    lowCostTextbook: $lowCostTextbook,
    instructor: $instructor
  ) {
    totalSections
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      cursor
      node {
        id
        registrationNumber
        instructors
        instructionMode
        careers
        openSeats
        totalSeats
        campus
        location
        component
        freeTextbookAvailable
        lowCostTextbookAvailable
        meetings {
          room
          building
          buildingCode
          buildingDescription
          days
          startDate
          endDate
          startTime
          endTime
        }
        __typename
      }
    }
    ...SectionFacetsContainer_getCourseSections
  }
  ...FacetsSettingsContainer_environment
}

fragment SectionFacetsContainer_getCourseSections on SearchSectionConnection {
  facetFieldResults {
    facetField
    facetFieldValueResults {
      value
      selected
      sectionCount
    }
  }
}

fragment FacetsSettingsContainer_environment on Environment {
  publicSettings {
    textSettings {
      campus
      campusPlural
      courseStatus
      academicCareerPlural
      freeTextbook
      freeTextbookInstructions
      partsOfTermPlural
      sessionPlural
      instructionModePlural
      instructor
      locationPlural
    }
    sectionFieldTextSettings {
      registrationNumber
    }
    courseSearchSettings {
      courseSearchFilters
      dropDownOptionsLimit
    }
    filterSettings {
      campusSelectionPrefixes
    }
    id
  }
}
"""
# ============================
#  Get Course Name
# ============================
GET_COURSE_NAME_QUERY = """
query routes_CourseContainer_Query($courseId: ID!) {
  course: node(id: $courseId) {
    __typename
    ...CourseContainer_course
    id
  }
}

fragment CourseContainer_course on SearchCourse {
  id
  subject { id }
  term { code id }
  courseNumber
  title
  description
  creditsMin
  creditsMax
}
"""
# ============================
#  Get Terms Query
# ============================
GET_TERMS_QUERY = """
query routes_Landing_Query($environment: String!) {
  environment(name: $environment) {
    ...LandingContainer_environment
    id
  }
}

fragment LandingContainer_environment on Environment {
  ...SearchBarContainer_environment
  publicSettings {
    styleSettings { logoUrl }
    id
  }
}

fragment SearchBarContainer_environment on Environment {
  publicSettings {
    courseSearchSettings {
      searchPlaceholder
      dropDownOptionsLimit
    }
    styleSettings { primaryColor }
    id
  }
  courseSearchTerms {
    code
    name
    id
  }
}
"""

# ============================
#  Search Course Query
# ============================
SEARCH_COURSE_QUERY = """
query SearchAutoCompleteQuery_Query(
  $environment: String!
  $termCode: String!
  $prefix: String!
  $size: Int
) {
  environment(name: $environment) {
    courses: suggestCourses(
      termCode: $termCode,
      prefix: $prefix,
      size: $size
    ) {
      courseId
      subjectId
      courseNumber
      title
    }
    id
  }
}
"""

# ============================
#  Get Specific Section Query
# ============================
GET_SECTION_QUERY = """
query routes_SectionContainer_Query(
  $environment: String!
  $courseId: ID!
  $sectionId: ID!
) {
  environment(name: $environment) {
    ...SectionContainer_environment
    id
  }
  course: node(id: $courseId) {
    __typename
    ...SectionContainer_course
    id
  }
  section: node(id: $sectionId) {
    __typename
    ...SectionContainer_section
    id
  }
}

fragment SectionContainer_environment on Environment {
  publicSettings {
    styleSettings {
      freeTextbookImageFileName
      lowCostTextbookImageFileName
    }
    courseSearchSettings {
      sectionFields
      sectionFooterEntries
      dropDownOptionsLimit
    }
    filterSettings { campusSelectionPrefixes }
    sectionSettings { locationFormat }
    sectionFieldTextSettings {
      campus
      component
      credits
      dates
      days
      freeTextbookIndicated
      lowCostTextbookIndicated
      instructionMode
      careers
      instructorPlural
      location
      openSeats
      registrationNumber
      rooms
      times
    }
    textSettings {
      academicCareerPlural
      mondayAbbr
      tuesdayAbbr
      wednesdayAbbr
      thursdayAbbr
      fridayAbbr
      saturdayAbbr
      sundayAbbr
    }
    id
  }
}

fragment SectionContainer_course on Node {
  ... on SearchCourse {
    courseNumber
    title
    subject { id }
    term { code id }
  }
}

fragment SectionContainer_section on Node {
  ... on SearchSection {
    id
    registrationNumber
    sectionNumber
    startDate
    endDate
    instructors
    instructionMode
    careers
    partsOfTerm
    courseTypeDescription
    creditsMin
    creditsMax
    openSeats
    totalSeats
    campus
    location
    component
    freeTextbookAvailable
    lowCostTextbookAvailable
    meetings {
      room
      building
      buildingCode
      buildingDescription
      days
      startDate
      endDate
      startTime
      endTime
    }
  }
}
"""

# ============================
#  Instructor Lookup Query
# ============================
GET_INSTRUCTOR_QUERY = """
query routes_InstructorCourses_Query(
  $environment: String!
  $termCode: String!
  $count: Int
  $cursor: String
  $facets: [SearchFacetCriteria]
  $includeFullCourses: Boolean
) {
  environment(name: $environment) {
    ...InstructorCoursesPagination_environment_1G22uz
    id
  }
}

fragment InstructorCoursesPagination_environment_1G22uz on Environment {
  publicSettings {
    textSettings { sectionPlural }
    id
  }
  findCourses(
    termCode: $termCode,
    first: $count,
    after: $cursor,
    facets: $facets,
    includeFullCourses: $includeFullCourses
  ) {
    pageInfo { hasNextPage endCursor }
    edges {
      node { id __typename }
      cursor
    }
    ...CourseListContainer_courseConnection
  }
}

fragment CourseListContainer_courseConnection on SearchCourseConnection {
  edges {
    node {
      id
      ...CourseContainer_course
    }
  }
}

fragment CourseContainer_course on SearchCourse {
  id
  subject { id }
  term { code id }
  courseNumber
  title
  description
  creditsMin
  creditsMax
}
"""