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
        Query the database using full-text search on FAQs table
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            
        Returns:
            List of matching results
        """
        results = []
        cursor = self.connection.cursor()
        
        try:
            # Search FAQs using FTS table
            cursor.execute("""
                SELECT f.question, f.answer, f.category
                FROM faqs f
                JOIN faqs_fts fts ON f.faq_id = fts.rowid
                WHERE faqs_fts MATCH ?
                LIMIT ?
            """, (query_text, n_results))
            
            for row in cursor.fetchall():
                results.append({
                    'content': f"Q: {row['question']}\nA: {row['answer']}",
                    'category': row['category'] or 'general',
                    'source': 'faq',
                    'score': 0.9
                })
        except Exception as e:
            # If FTS fails, fall back to LIKE search
            print(f"FTS search failed, using LIKE: {e}")
            cursor.execute("""
                SELECT question, answer, category
                FROM faqs
                WHERE LOWER(question) LIKE ? OR LOWER(answer) LIKE ?
                LIMIT ?
            """, (f'%{query_text.lower()}%', f'%{query_text.lower()}%', n_results))
            
            for row in cursor.fetchall():
                results.append({
                    'content': f"Q: {row['question']}\nA: {row['answer']}",
                    'category': row['category'] or 'general',
                    'source': 'faq',
                    'score': 0.9
                })
        
        # If not enough results, search prerequisites
        if len(results) < n_results:
            keywords = query_text.lower().split()
            for keyword in keywords:
                cursor.execute("""
                    SELECT course_code, course_name, prerequisite_courses, description
                    FROM prerequisites
                    WHERE LOWER(course_code) LIKE ? OR LOWER(course_name) LIKE ? OR LOWER(description) LIKE ?
                    LIMIT ?
                """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', n_results - len(results)))
                
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
        
        # If still not enough, search programs
        if len(results) < n_results:
            keywords = query_text.lower().split()
            for keyword in keywords:
                cursor.execute("""
                    SELECT program_name, degree_type, department, description
                    FROM programs
                    WHERE LOWER(program_name) LIKE ? OR LOWER(description) LIKE ?
                    LIMIT ?
                """, (f'%{keyword}%', f'%{keyword}%', n_results - len(results)))
                
                for row in cursor.fetchall():
                    results.append({
                        'content': f"{row['program_name']} ({row['degree_type']}): {row['description'] or ''}",
                        'category': 'academics',
                        'source': 'programs',
                        'score': 0.7
                    })
                    
                    if len(results) >= n_results:
                        break
                        
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
