-- SJSU Virtual Assistant Database Schema

-- Programs Table
CREATE TABLE IF NOT EXISTS programs (
    program_id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_name TEXT NOT NULL,
    degree_type TEXT NOT NULL, -- BS, MS, PhD, Certificate
    department TEXT NOT NULL,
    description TEXT,
    website_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_programs_name ON programs(program_name);
CREATE INDEX idx_programs_department ON programs(department);

-- Admission Requirements Table
CREATE TABLE IF NOT EXISTS admission_requirements (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER,
    degree_level TEXT NOT NULL, -- Undergraduate, Graduate
    min_gpa REAL,
    toefl_score INTEGER,
    ielts_score REAL,
    gre_required BOOLEAN DEFAULT 0,
    gre_verbal INTEGER,
    gre_quantitative INTEGER,
    additional_requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE
);

CREATE INDEX idx_admission_program ON admission_requirements(program_id);

-- Prerequisites Table
CREATE TABLE IF NOT EXISTS prerequisites (
    prereq_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL UNIQUE,
    course_name TEXT NOT NULL,
    department TEXT,
    prerequisite_courses TEXT, -- JSON array or comma-separated
    corequisite_courses TEXT,
    description TEXT,
    units INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prereq_course ON prerequisites(course_code);
CREATE INDEX idx_prereq_dept ON prerequisites(department);

-- Deadlines Table
CREATE TABLE IF NOT EXISTS deadlines (
    deadline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester TEXT NOT NULL, -- Fall 2025, Spring 2026
    year INTEGER NOT NULL,
    deadline_type TEXT NOT NULL, -- Application, Registration, Drop/Add, Refund, Withdrawal
    deadline_date DATE NOT NULL,
    description TEXT,
    applies_to TEXT, -- Undergraduate, Graduate, All
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deadlines_semester ON deadlines(semester);
CREATE INDEX idx_deadlines_type ON deadlines(deadline_type);
CREATE INDEX idx_deadlines_date ON deadlines(deadline_date);

-- Campus Resources Table
CREATE TABLE IF NOT EXISTS campus_resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_name TEXT NOT NULL,
    category TEXT NOT NULL, -- Advising, Health, Library, Housing, Financial Aid, Student Services
    description TEXT,
    location TEXT,
    building TEXT,
    room_number TEXT,
    phone TEXT,
    email TEXT,
    hours TEXT,
    website_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resources_category ON campus_resources(category);
CREATE INDEX idx_resources_name ON campus_resources(resource_name);

-- FAQs Table
CREATE TABLE IF NOT EXISTS faqs (
    faq_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT, -- Admissions, Registration, Financial, Academic, Campus Life
    keywords TEXT, -- Comma-separated for search
    related_resource_id INTEGER,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (related_resource_id) REFERENCES campus_resources(resource_id) ON DELETE SET NULL
);

CREATE INDEX idx_faqs_category ON faqs(category);
CREATE INDEX idx_faqs_keywords ON faqs(keywords);

-- Enable full-text search on FAQs
CREATE VIRTUAL TABLE IF NOT EXISTS faqs_fts USING fts5(
    question,
    answer,
    keywords,
    content=faqs,
    content_rowid=faq_id
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS faqs_ai AFTER INSERT ON faqs BEGIN
    INSERT INTO faqs_fts(rowid, question, answer, keywords)
    VALUES (new.faq_id, new.question, new.answer, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS faqs_ad AFTER DELETE ON faqs BEGIN
    DELETE FROM faqs_fts WHERE rowid = old.faq_id;
END;

CREATE TRIGGER IF NOT EXISTS faqs_au AFTER UPDATE ON faqs BEGIN
    UPDATE faqs_fts SET 
        question = new.question,
        answer = new.answer,
        keywords = new.keywords
    WHERE rowid = new.faq_id;
END;

-- Student Clubs Table
CREATE TABLE IF NOT EXISTS student_clubs (
    club_id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_name TEXT NOT NULL,
    category TEXT, -- Engineering, Business, Cultural, Sports, Academic
    department TEXT,
    description TEXT,
    contact_email TEXT,
    meeting_schedule TEXT,
    website_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clubs_category ON student_clubs(category);
CREATE INDEX idx_clubs_dept ON student_clubs(department);

-- Scholarships Table
CREATE TABLE IF NOT EXISTS scholarships (
    scholarship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scholarship_name TEXT NOT NULL,
    amount REAL,
    amount_type TEXT, -- Fixed, Range, Variable
    eligibility TEXT,
    min_gpa REAL,
    major_restriction TEXT,
    deadline DATE,
    application_url TEXT,
    description TEXT,
    renewable BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scholarships_deadline ON scholarships(deadline);
CREATE INDEX idx_scholarships_gpa ON scholarships(min_gpa);
