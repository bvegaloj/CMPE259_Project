"""
Database Manager for SJSU Virtual Assistant
Manages SQLite database operations for SJSU information retrieval
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class DatabaseManager:
    """Manages the SQLite database for SJSU information"""
    
    def __init__(self, db_path: str = "./data/sjsu_database.db", collection_name: str = None):
        """
        Initialize the database manager
        
        Args:
            db_path: Path to SQLite database
            collection_name: Not used for SQLite (kept for compatibility)
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
        
        print(f"Database initialized: {db_path}")
        tables = self.get_tables()
        print(f"Available tables: {', '.join(tables)}")
        print(f"Document count: {self.get_collection_stats()['count']}")
    
    def _connect(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def get_tables(self) -> List[str]:
        """Get list of tables in database"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%'")
        return [row[0] for row in cursor.fetchall()]
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the database using intelligent table selection based on query content
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            
        Returns:
            List of matching results
        """
        results = []
        cursor = self.connection.cursor()
        query_lower = query_text.lower()
        
        # Determine which tables to search based on query content
        search_scholarships = any(word in query_lower for word in ['scholarship', 'financial aid', 'funding', 'grant', 'award'])
        search_deadlines = any(word in query_lower for word in ['deadline', 'due date', 'when', 'application date'])
        search_programs = any(word in query_lower for word in ['program', 'major', 'degree', 'department'])
        search_admission = any(word in query_lower for word in ['admission', 'requirement', 'gpa', 'apply', 'eligibility'])
        search_clubs = 'club' in query_lower or 'organization' in query_lower
        search_resources = any(word in query_lower for word in ['resource', 'service', 'health', 'career', 'library', 'counseling']) and not search_clubs
        search_prerequisites = any(word in query_lower for word in ['prerequisite', 'prereq', 'course', 'class']) or \
                               bool(__import__('re').search(r'\b[A-Z]{2,4}\s*\d{3}\b', query_text.upper()))
        
        # Search student clubs FIRST if query is about clubs
        if search_clubs and len(results) < n_results:
            cursor.execute("""
                SELECT club_name, category, department, description, contact_email, meeting_schedule
                FROM student_clubs
                LIMIT ?
            """, (n_results - len(results),))
            
            for row in cursor.fetchall():
                results.append({
                    'content': f"Club: {row['club_name']}\nCategory: {row['category']}\nDepartment: {row['department'] or 'University-wide'}\nDescription: {row['description'] or ''}\nContact: {row['contact_email'] or 'N/A'}\nMeetings: {row['meeting_schedule'] or 'Check website'}",
                    'category': 'student_clubs',
                    'source': 'student_clubs',
                    'score': 0.95
                })
        
        # Search scholarships table if relevant
        if search_scholarships and len(results) < n_results:
            cursor.execute("""
                SELECT scholarship_name, amount, eligibility, deadline, description, min_gpa, major_restriction
                FROM scholarships
                LIMIT ?
            """, (n_results,))
            
            for row in cursor.fetchall():
                gpa_req = f"Min GPA: {row['min_gpa']}" if row['min_gpa'] else ""
                major_req = f"Major: {row['major_restriction']}" if row['major_restriction'] else ""
                results.append({
                    'content': f"Scholarship: {row['scholarship_name']}\nAmount: ${row['amount']}\nEligibility: {row['eligibility']}\nDeadline: {row['deadline']}\n{gpa_req}\n{major_req}\nDescription: {row['description'] or ''}",
                    'category': 'financial_aid',
                    'source': 'scholarships',
                    'score': 0.95
                })
        
        # Search deadlines if relevant
        if search_deadlines and len(results) < n_results:
            cursor.execute("""
                SELECT deadline_type, deadline_date, semester, description, applies_to
                FROM deadlines
                ORDER BY deadline_date
                LIMIT ?
            """, (n_results - len(results),))
            
            for row in cursor.fetchall():
                results.append({
                    'content': f"Deadline: {row['deadline_type']}\nDate: {row['deadline_date']}\nSemester: {row['semester']}\nApplies to: {row['applies_to'] or 'All students'}\nDetails: {row['description'] or ''}",
                    'category': 'deadlines',
                    'source': 'deadlines',
                    'score': 0.9
                })
        
        # Search admission requirements if relevant
        if search_admission and len(results) < n_results:
            cursor.execute("""
                SELECT ar.*, p.program_name 
                FROM admission_requirements ar
                LEFT JOIN programs p ON ar.program_id = p.program_id
                LIMIT ?
            """, (n_results - len(results),))
            
            for row in cursor.fetchall():
                program = row['program_name'] or f"Program ID {row['program_id']}"
                gpa_info = f"Min GPA: {row['min_gpa']}" if row['min_gpa'] else ""
                gre_info = "GRE Required" if row['gre_required'] else "GRE Not Required"
                results.append({
                    'content': f"Program: {program}\nDegree Level: {row['degree_level']}\n{gpa_info}\n{gre_info}\nAdditional: {row['additional_requirements'] or 'None'}",
                    'category': 'admission',
                    'source': 'admission_requirements',
                    'score': 0.9
                })
        
        # Search campus resources if relevant
        if search_resources and len(results) < n_results:
            cursor.execute("""
                SELECT resource_name, category, location, building, phone, email, hours, description
                FROM campus_resources
                LIMIT ?
            """, (n_results - len(results),))
            
            for row in cursor.fetchall():
                location_info = f"{row['building'] or ''} {row['location'] or ''}".strip()
                contact_info = f"Phone: {row['phone'] or 'N/A'}, Email: {row['email'] or 'N/A'}"
                results.append({
                    'content': f"Resource: {row['resource_name']}\nCategory: {row['category']}\nLocation: {location_info}\nContact: {contact_info}\nHours: {row['hours'] or 'Check website'}\nDescription: {row['description'] or ''}",
                    'category': 'campus_resources',
                    'source': 'campus_resources',
                    'score': 0.85
                })
        
        # Search FAQs using FTS table
        if len(results) < n_results:
            try:
                cursor.execute("""
                    SELECT f.question, f.answer, f.category
                    FROM faqs f
                    JOIN faqs_fts fts ON f.faq_id = fts.rowid
                    WHERE faqs_fts MATCH ?
                    LIMIT ?
                """, (query_text, n_results - len(results)))
                
                for row in cursor.fetchall():
                    results.append({
                        'content': f"Q: {row['question']}\nA: {row['answer']}",
                        'category': row['category'] or 'general',
                        'source': 'faq',
                        'score': 0.9
                    })
            except Exception as e:
                # If FTS fails, fall back to LIKE search on FAQs
                print(f"FTS search failed, using LIKE: {e}")
                cursor.execute("""
                    SELECT question, answer, category
                    FROM faqs
                    WHERE LOWER(question) LIKE ? OR LOWER(answer) LIKE ?
                    LIMIT ?
                """, (f'%{query_text.lower()}%', f'%{query_text.lower()}%', n_results - len(results)))
                
                for row in cursor.fetchall():
                    results.append({
                        'content': f"Q: {row['question']}\nA: {row['answer']}",
                        'category': row['category'] or 'general',
                        'source': 'faq',
                        'score': 0.9
                    })
        
        # Only search prerequisites if query is about courses/prerequisites
        if search_prerequisites and len(results) < n_results:
            import re
            # Look for course codes in query
            course_pattern = r'\b([A-Z]{2,4})\s*(\d{3})\b'
            course_matches = re.findall(course_pattern, query_text.upper())
            
            if course_matches:
                # Search for specific course codes
                for dept, num in course_matches:
                    course_code = f"{dept} {num}"
                    cursor.execute("""
                        SELECT course_code, course_name, prerequisite_courses, description
                        FROM prerequisites
                        WHERE course_code = ? OR course_code = ?
                        LIMIT ?
                    """, (course_code, course_code.replace(' ', ''), n_results - len(results)))
                    
                    for row in cursor.fetchall():
                        prereqs = row['prerequisite_courses'] or 'None'
                        desc = row['description'] or ''
                        results.append({
                            'content': f"{row['course_code']} - {row['course_name']}: Prerequisites: {prereqs}. {desc}",
                            'category': 'academics',
                            'source': 'prerequisites',
                            'score': 0.95
                        })
            else:
                # General prerequisite search - only with specific keywords
                specific_keywords = ['prerequisite', 'prereq']
                for keyword in specific_keywords:
                    if keyword in query_lower:
                        cursor.execute("""
                            SELECT course_code, course_name, prerequisite_courses, description
                            FROM prerequisites
                            LIMIT ?
                        """, (n_results - len(results),))
                        
                        for row in cursor.fetchall():
                            prereqs = row['prerequisite_courses'] or 'None'
                            desc = row['description'] or ''
                            results.append({
                                'content': f"{row['course_code']} - {row['course_name']}: Prerequisites: {prereqs}. {desc}",
                                'category': 'academics',
                                'source': 'prerequisites',
                                'score': 0.8
                            })
                            
                            if len(results) >= n_results:
                                break
        
        # Search programs only if relevant and not enough results
        if search_programs and len(results) < n_results:
            cursor.execute("""
                SELECT program_name, degree_type, department, description
                FROM programs
                LIMIT ?
            """, (n_results - len(results),))
            
            for row in cursor.fetchall():
                results.append({
                    'content': f"{row['program_name']} ({row['degree_type']}): {row['description'] or ''}",
                    'category': 'academics',
                    'source': 'programs',
                    'score': 0.7
                })
                        
        return results[:n_results]
    
    def query_with_filter(self, query_text: str, category: str = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query with category filtering
        
        Args:
            query_text: Query string
            category: Category to filter by (optional)
            n_results: Number of results
            
        Returns:
            Query results
        """
        if category:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT question, answer, category
                FROM faqs
                WHERE category = ? AND faqs MATCH ?
                LIMIT ?
            """, (category, query_text, n_results))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'content': f"Q: {row['question']}\nA: {row['answer']}",
                    'category': row['category'],
                    'source': 'faq',
                    'score': 0.9
                })
            return results
        else:
            return self.query(query_text, n_results)
    
    def get_prerequisites(self, course_code: str) -> Optional[Dict[str, Any]]:
        """
        Get prerequisites for a specific course
        
        Args:
            course_code: Course code (e.g., 'CMPE 259')
            
        Returns:
            Course prerequisite information
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM prerequisites WHERE course_code = ?
        """, (course_code,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def search_courses(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for courses by keyword
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching courses
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM prerequisites
            WHERE LOWER(course_code) LIKE ? OR LOWER(course_name) LIKE ?
        """, (f'%{keyword.lower()}%', f'%{keyword.lower()}%'))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_programs(self, department: str = None) -> List[Dict[str, Any]]:
        """
        Get programs, optionally filtered by department
        
        Args:
            department: Department name (optional)
            
        Returns:
            List of programs
        """
        cursor = self.connection.cursor()
        if department:
            cursor.execute("SELECT * FROM programs WHERE department = ?", (department,))
        else:
            cursor.execute("SELECT * FROM programs")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_deadlines(self, semester: str = None) -> List[Dict[str, Any]]:
        """
        Get deadlines, optionally filtered by semester
        
        Args:
            semester: Semester (e.g., 'Fall 2025')
            
        Returns:
            List of deadlines
        """
        cursor = self.connection.cursor()
        if semester:
            cursor.execute("SELECT * FROM deadlines WHERE semester = ? ORDER BY deadline_date", (semester,))
        else:
            cursor.execute("SELECT * FROM deadlines ORDER BY deadline_date")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_campus_resources(self) -> List[Dict[str, Any]]:
        """Get all campus resources"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM campus_resources")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_faqs(self, category: str = None) -> List[Dict[str, Any]]:
        """
        Get FAQs, optionally filtered by category
        
        Args:
            category: FAQ category (optional)
            
        Returns:
            List of FAQs
        """
        cursor = self.connection.cursor()
        if category:
            cursor.execute("SELECT * FROM faqs WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM faqs")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database
        
        Returns:
            Dict with database statistics
        """
        cursor = self.connection.cursor()
        
        stats = {
            'db_path': self.db_path,
            'count': 0
        }
        
        for table in self.get_tables():
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
                stats['count'] += count
            except:
                pass
        
        return stats
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Add documents (compatibility method for ChromaDB-like interface)
        Not implemented for SQLite - use specific table insert methods instead
        """
        print("Warning: add_documents not implemented for SQLite. Use specific table methods.")
        pass
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
