"""Sample data population script for SJSU database"""

from src.database.db_manager import DatabaseManager
from src.utils.logger import logger


def populate_sample_data():
    """Populate database with sample SJSU data"""
    
    db = DatabaseManager()
    
    logger.info("Populating sample data")
    
    # Programs
    programs_data = [
        ("Computer Science", "BS", "Computer Science", 
         "Bachelor of Science in Computer Science provides comprehensive education in software development, algorithms, and computing systems.",
         "https://www.sjsu.edu/cs/"),
        ("Computer Science", "MS", "Computer Science",
         "Master of Science in Computer Science with focus on advanced topics including AI, systems, and software engineering.",
         "https://www.sjsu.edu/cs/"),
        ("Computer Engineering", "BS", "Computer Engineering",
         "Bachelor of Science in Computer Engineering combines hardware and software design.",
         "https://www.sjsu.edu/cmpe/"),
        ("Computer Engineering", "MS", "Computer Engineering",
         "Master of Science in Computer Engineering with specializations in embedded systems, IoT, and computer architecture.",
         "https://www.sjsu.edu/cmpe/"),
        ("Software Engineering", "MS", "Computer Science",
         "Master of Science in Software Engineering focused on large-scale software development practices.",
         "https://www.sjsu.edu/cs/"),
        ("Business Administration", "BS", "Lucas College of Business",
         "Bachelor of Science in Business Administration with various concentrations.",
         "https://www.sjsu.edu/lcob/"),
        ("Data Science", "MS", "Computer Science",
         "Master of Science in Data Science covering machine learning, big data analytics, and statistical methods.",
         "https://www.sjsu.edu/cs/"),
        ("Electrical Engineering", "BS", "Electrical Engineering",
         "Bachelor of Science in Electrical Engineering covering circuits, signals, and systems.",
         "https://www.sjsu.edu/ee/"),
        ("Mechanical Engineering", "BS", "Mechanical Engineering",
         "Bachelor of Science in Mechanical Engineering with focus on design and manufacturing.",
         "https://www.sjsu.edu/me/"),
        ("Nursing", "BS", "Nursing",
         "Bachelor of Science in Nursing preparing students for nursing practice.",
         "https://www.sjsu.edu/nursing/"),
    ]
    
    sql = """
        INSERT INTO programs (program_name, degree_type, department, description, website_url)
        VALUES (?, ?, ?, ?, ?)
    """
    db.execute_many(sql, programs_data)
    logger.info(f"Inserted {len(programs_data)} programs")
    
    # Admission Requirements
    admission_reqs = [
        (1, "Undergraduate", 3.0, None, None, 0, None, None, "High school GPA of 3.0 or higher, SAT/ACT scores, completion of A-G requirements"),
        (2, "Graduate", 3.0, 80, 6.5, 0, None, None, "Bachelor's degree in CS or related field, minimum 3.0 GPA, programming experience required"),
        (3, "Undergraduate", 3.0, None, None, 0, None, None, "High school GPA of 3.0, strong math and science background"),
        (4, "Graduate", 3.0, 80, 6.5, 0, None, None, "Bachelor's in Computer Engineering or related field, programming and hardware experience"),
        (5, "Graduate", 3.0, 80, 6.5, 0, None, None, "Bachelor's degree, 2+ years software development experience preferred"),
        (6, "Undergraduate", 2.5, None, None, 0, None, None, "High school GPA of 2.5 or higher, completion of A-G requirements"),
        (7, "Graduate", 3.0, 80, 6.5, 0, None, None, "Bachelor's degree, strong quantitative background, programming skills"),
        (8, "Undergraduate", 3.0, None, None, 0, None, None, "Strong math and science background, minimum 3.0 GPA"),
        (9, "Undergraduate", 3.0, None, None, 0, None, None, "Strong physics and math background"),
        (10, "Undergraduate", 3.0, None, None, 0, None, None, "Prerequisite coursework in sciences, minimum 3.0 GPA"),
    ]
    
    sql = """
        INSERT INTO admission_requirements 
        (program_id, degree_level, min_gpa, toefl_score, ielts_score, gre_required, 
         gre_verbal, gre_quantitative, additional_requirements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    db.execute_many(sql, admission_reqs)
    logger.info(f"Inserted {len(admission_reqs)} admission requirements")
    
    # Prerequisites
    prerequisites = [
        ("CMPE 259", "Machine Learning", "Computer Engineering", 
         "CMPE 140, CMPE 180", "", "Advanced topics in machine learning algorithms and applications", 3),
        ("CMPE 140", "Computer Architecture", "Computer Engineering",
         "CS 46B", "", "Introduction to computer organization and architecture", 3),
        ("CMPE 180", "Data Structures and Algorithms", "Computer Engineering",
         "CS 46B", "", "Advanced data structures and algorithm analysis", 3),
        ("CS 46B", "Introduction to Data Structures", "Computer Science",
         "CS 46A", "", "Object-oriented programming and data structures", 4),
        ("CS 46A", "Introduction to Programming", "Computer Science",
         "", "", "Introduction to programming in Java", 4),
        ("MATH 161A", "Calculus I", "Mathematics",
         "", "", "Differential calculus and applications", 3),
        ("PHYS 50", "General Physics", "Physics",
         "MATH 30 or MATH 19", "", "Mechanics, wave motion, and thermodynamics", 4),
    ]
    
    sql = """
        INSERT INTO prerequisites 
        (course_code, course_name, department, prerequisite_courses, 
         corequisite_courses, description, units)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    db.execute_many(sql, prerequisites)
    logger.info(f"Inserted {len(prerequisites)} prerequisites")
    
    # Deadlines
    deadlines = [
        ("Fall 2025", 2025, "Application", "2025-06-30", "Application deadline for Fall 2025 admission", "Undergraduate"),
        ("Fall 2025", 2025, "Application", "2025-05-01", "Application deadline for Fall 2025 admission", "Graduate"),
        ("Fall 2025", 2025, "Registration", "2025-08-15", "Priority registration opens", "All"),
        ("Fall 2025", 2025, "Drop/Add", "2025-09-15", "Last day to add/drop classes without a W", "All"),
        ("Fall 2025", 2025, "Refund", "2025-09-08", "Last day to drop with full refund", "All"),
        ("Fall 2025", 2025, "Withdrawal", "2025-11-15", "Last day to withdraw with a W", "All"),
        ("Spring 2026", 2026, "Application", "2025-11-30", "Application deadline for Spring 2026 admission", "All"),
        ("Spring 2026", 2026, "Registration", "2026-01-10", "Priority registration opens", "All"),
        ("Spring 2026", 2026, "Drop/Add", "2026-02-10", "Last day to add/drop classes without a W", "All"),
        ("Spring 2026", 2026, "Refund", "2026-02-03", "Last day to drop with full refund", "All"),
    ]
    
    sql = """
        INSERT INTO deadlines 
        (semester, year, deadline_type, deadline_date, description, applies_to)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    db.execute_many(sql, deadlines)
    logger.info(f"Inserted {len(deadlines)} deadlines")
    
    # Campus Resources
    resources = [
        ("Academic Advising Center", "Advising", 
         "Provides academic advising for undergraduate students on course selection, major requirements, and graduation planning.",
         "Student Services Center", "SSC", "100", "408-924-2000", "advising@sjsu.edu",
         "Monday-Friday: 8:30 AM - 5:00 PM", "https://www.sjsu.edu/advising/"),
        
        ("Student Health Center", "Health",
         "Provides medical services, counseling, and wellness programs for SJSU students.",
         "Student Wellness Center", "SWC", "Main Floor", "408-924-6120", "health@sjsu.edu",
         "Monday-Friday: 8:00 AM - 5:00 PM", "https://www.sjsu.edu/studenthealth/"),
        
        ("Dr. Martin Luther King Jr. Library", "Library",
         "Joint library serving SJSU students and San José residents with extensive resources and study spaces.",
         "King Library", "MLK", "1st-8th Floor", "408-808-2000", "king-questions@sjsu.edu",
         "Monday-Thursday: 8:00 AM - 11:00 PM, Friday: 8:00 AM - 6:00 PM, Saturday: 10:00 AM - 6:00 PM, Sunday: 12:00 PM - 11:00 PM",
         "https://library.sjsu.edu/"),
        
        ("Financial Aid Office", "Financial Aid",
         "Assists students with financial aid applications, scholarships, grants, and loans.",
         "Student Services Center", "SSC", "120", "408-283-7500", "financialaid@sjsu.edu",
         "Monday-Friday: 9:00 AM - 4:00 PM", "https://www.sjsu.edu/faso/"),
        
        ("Housing Office", "Housing",
         "Manages on-campus housing applications and assignments.",
         "Joe West Hall", "JWH", "Office", "408-924-6160", "housing@sjsu.edu",
         "Monday-Friday: 8:00 AM - 5:00 PM", "https://www.sjsu.edu/housing/"),
        
        ("Career Center", "Student Services",
         "Provides career counseling, job search assistance, and internship opportunities.",
         "Student Services Center", "SSC", "600", "408-924-6031", "career-center@sjsu.edu",
         "Monday-Friday: 9:00 AM - 5:00 PM", "https://www.sjsu.edu/careercenter/"),
        
        ("Accessible Education Center", "Student Services",
         "Provides disability accommodations and support services for students with disabilities.",
         "Administration Building", "ADM", "110", "408-924-6000", "aec-info@sjsu.edu",
         "Monday-Friday: 8:00 AM - 5:00 PM", "https://www.sjsu.edu/aec/"),
        
        ("International Student Services", "Student Services",
         "Supports international students with visa issues, orientation, and cultural adjustment.",
         "Student Services Center", "SSC", "250", "408-924-5910", "isso@sjsu.edu",
         "Monday-Friday: 9:00 AM - 5:00 PM", "https://www.sjsu.edu/isss/"),
    ]
    
    sql = """
        INSERT INTO campus_resources 
        (resource_name, category, description, location, building, room_number, 
         phone, email, hours, website_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    db.execute_many(sql, resources)
    logger.info(f"Inserted {len(resources)} campus resources")
    
    # FAQs
    faqs = [
        ("What undergraduate programs are available at SJSU?",
         "SJSU offers over 145 areas of study including Computer Science, Engineering, Business, Nursing, and many more. Visit sjsu.edu/academics for a complete list.",
         "Admissions", "programs, majors, undergraduate", 1),
        
        ("What are the admission requirements for Computer Science?",
         "For undergraduate: 3.0 GPA, completion of A-G requirements. For graduate: Bachelor's in CS or related field, 3.0 GPA, TOEFL 80+ for international students.",
         "Admissions", "computer science, requirements, GPA", 2),
        
        ("What is the deadline to apply for Fall 2025?",
         "Undergraduate applications due June 30, 2025. Graduate applications due May 1, 2025. Apply early as some programs fill quickly.",
         "Admissions", "deadline, fall, application", None),
        
        ("How do I transfer credits from another college?",
         "Submit official transcripts to SJSU Admissions. Credits from regionally accredited institutions are evaluated. Contact Academic Advising for transfer credit evaluation.",
         "Academic", "transfer, credits, transcripts", 1),
        
        ("What GPA do I need to maintain my scholarship?",
         "Most scholarships require a minimum 3.0 GPA, but requirements vary. Check your specific scholarship award letter or contact Financial Aid.",
         "Financial", "scholarship, GPA, maintain", 4),
        
        ("When does course registration open?",
         "Registration dates vary by semester and student classification. Fall 2025 priority registration opens August 15. Check MySJSU for your specific registration date.",
         "Registration", "registration, course, schedule", None),
        
        ("How can I make an appointment with an academic advisor?",
         "Schedule appointments through Navigate or visit the Academic Advising Center (SSC 100). Walk-ins available during drop-in hours.",
         "Academic", "advising, advisor, appointment", 1),
        
        ("What are the tuition fees for graduate students?",
         "For 2024-25, graduate tuition is approximately $7,734/year for California residents and $16,848/year for non-residents (based on full-time enrollment).",
         "Financial", "tuition, fees, graduate, cost", 4),
        
        ("How do I apply for on-campus housing?",
         "Apply online through the Housing Portal. Priority given to first-year students. Application opens in April for Fall semester.",
         "Campus Life", "housing, dorms, residence", 5),
        
        ("What is the last day to drop a class with a refund?",
         "For Fall 2025, September 8 is the last day to drop with full refund. After this, tuition fees are not refundable.",
         "Registration", "drop, refund, deadline, withdrawal", None),
        
        ("How can I find information about financial aid?",
         "Visit the Financial Aid Office (SSC 120), call 408-283-7500, or check sjsu.edu/faso. Complete FAFSA at fafsa.gov to apply.",
         "Financial", "financial aid, FAFSA, scholarships", 4),
        
        ("What prerequisites do I need to take CMPE 259?",
         "CMPE 259 requires completion of CMPE 140 (Computer Architecture) and CMPE 180 (Data Structures and Algorithms) with grade C or better.",
         "Academic", "prerequisites, CMPE 259, requirements", None),
        
        ("What student clubs are available for engineering majors?",
         "Many engineering clubs including IEEE, ACM, SHPE, SWE, and ASME. Visit Student Involvement for complete list and meeting schedules.",
         "Campus Life", "clubs, engineering, organizations", None),
        
        ("How can I request my transcripts?",
         "Order official transcripts through the National Student Clearinghouse website. Unofficial transcripts available on MySJSU.",
         "Academic", "transcript, records, grades", None),
        
        ("What are the library hours during finals week?",
         "King Library extends hours during finals week, typically open 24/5. Check library.sjsu.edu for exact hours each semester.",
         "Campus Life", "library, hours, finals, study", 3),
        
        ("Can you list all deadlines for Spring 2026 registration?",
         "Application deadline: Nov 30, 2025. Registration opens: Jan 10, 2026. Last day to add/drop: Feb 10, 2026. Refund deadline: Feb 3, 2026.",
         "Registration", "deadlines, spring, registration", None),
        
        ("How do I change my major?",
         "Meet with an advisor in your current department and desired major. Complete Change of Major form and submit to Admissions and Records.",
         "Academic", "change major, switch, transfer", 1),
        
        ("What is the minimum TOEFL score required for international students?",
         "Minimum TOEFL iBT score is 80 for most graduate programs, 71 for undergraduate. IELTS 6.5 also accepted.",
         "Admissions", "TOEFL, IELTS, international, English", 8),
        
        ("Where can I find campus health services?",
         "Student Health Center in the Student Wellness Center. Services include medical care, counseling, and wellness programs. Call 408-924-6120.",
         "Campus Life", "health, medical, counseling, wellness", 2),
        
        ("Who should I contact for disability accommodations?",
         "Contact the Accessible Education Center (AEC) in ADM 110. Call 408-924-6000 or email aec-info@sjsu.edu to register for services.",
         "Student Services", "disability, accommodations, AEC", 7),
    ]
    
    sql = """
        INSERT INTO faqs (question, answer, category, keywords, related_resource_id)
        VALUES (?, ?, ?, ?, ?)
    """
    db.execute_many(sql, faqs)
    logger.info(f"Inserted {len(faqs)} FAQs")
    
    # Student Clubs
    clubs = [
        ("ACM Student Chapter", "Academic", "Computer Science",
         "Association for Computing Machinery student chapter focused on CS topics and networking.",
         "acm@sjsu.edu", "Weekly meetings", "https://acmsjsu.org/"),
        
        ("IEEE Student Branch", "Academic", "Electrical Engineering",
         "Institute of Electrical and Electronics Engineers student branch for EE students.",
         "ieee@sjsu.edu", "Bi-weekly", "https://ieeesjsu.org/"),
        
        ("Society of Women Engineers", "Academic", "Engineering",
         "Supports women in engineering through mentorship and professional development.",
         "swe@sjsu.edu", "Monthly meetings", "https://swesjsu.org/"),
        
        ("Society of Hispanic Professional Engineers", "Academic", "Engineering",
         "Promotes Hispanic engineering students and professionals.",
         "shpe@sjsu.edu", "Bi-weekly", "https://shpesjsu.org/"),
        
        ("American Society of Mechanical Engineers", "Academic", "Mechanical Engineering",
         "Professional organization for mechanical engineering students.",
         "asme@sjsu.edu", "Monthly", "https://asmesjsu.org/"),
        
        ("Business Student Association", "Academic", "Business",
         "Connects business students with industry professionals and career opportunities.",
         "bsa@sjsu.edu", "Weekly", "https://www.sjsu.edu/lcob/"),
        
        ("Data Science Club", "Academic", "Computer Science",
         "Explores data science, machine learning, and analytics projects.",
         "datascience@sjsu.edu", "Weekly", None),
    ]
    
    sql = """
        INSERT INTO student_clubs 
        (club_name, category, department, description, contact_email, meeting_schedule, website_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    db.execute_many(sql, clubs)
    logger.info(f"Inserted {len(clubs)} student clubs")
    
    # Scholarships
    scholarships = [
        ("Presidential Scholarship", 15000, "Fixed",
         "Outstanding academic achievement, leadership, and community service", 3.8, "All",
         "2025-03-01", "https://www.sjsu.edu/scholarships", "Merit-based, four years", 1),
        
        ("Engineering Excellence Award", 5000, "Fixed",
         "Engineering majors with strong academic record", 3.5, "Engineering",
         "2025-04-15", "https://www.sjsu.edu/engineering/scholarships", "One year", 0),
        
        ("Dean's Scholarship", 3000, "Fixed",
         "Academic excellence in specific colleges", 3.5, "All",
         "2025-03-15", "https://www.sjsu.edu/scholarships", "One year", 0),
        
        ("Transfer Student Scholarship", 2500, "Fixed",
         "Outstanding transfer students from community colleges", 3.3, "All",
         "2025-05-01", "https://www.sjsu.edu/scholarships", "One year", 0),
    ]
    
    sql = """
        INSERT INTO scholarships 
        (scholarship_name, amount, amount_type, eligibility, min_gpa, major_restriction,
         deadline, application_url, description, renewable)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    db.execute_many(sql, scholarships)
    logger.info(f"Inserted {len(scholarships)} scholarships")
    
    logger.info("Sample data population complete!")


if __name__ == "__main__":
    # Initialize database and populate with sample data
    db = DatabaseManager()
    db.initialize_database()
    populate_sample_data()
    
    print("\nDatabase initialized and populated successfully!")
    print(f"Database location: {db.db_path}")
