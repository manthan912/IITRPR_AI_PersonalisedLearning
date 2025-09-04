"""
Sample data generator for testing the personalized learning system
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.database import SessionLocal, engine, Base
from app.models.student import Student
from app.models.learning_material import LearningMaterial, ContentType, DifficultyLevel
from app.models.progress import Progress
from app.models.learning_style import LearningStyle
from app.api.auth import get_password_hash


def create_sample_learning_materials(db: Session):
    """Create diverse sample learning materials"""
    
    materials = [
        # Python Programming
        {
            "title": "Python Basics: Variables and Data Types",
            "description": "Introduction to Python variables, strings, numbers, and basic data types",
            "content_type": ContentType.TEXT,
            "subject": "Python Programming",
            "topic": "Basic Syntax",
            "difficulty_level": DifficultyLevel.BEGINNER,
            "estimated_duration": 45,
            "learning_styles": ["reading_writing", "visual"],
            "tags": ["python", "basics", "variables", "data-types"],
            "complexity_score": 0.3,
            "content_text": "Variables are containers for storing data values. Python has different data types including strings, integers, floats, and booleans."
        },
        {
            "title": "Python Programming Video Tutorial",
            "description": "Interactive video tutorial covering Python fundamentals with hands-on examples",
            "content_type": ContentType.VIDEO,
            "subject": "Python Programming", 
            "topic": "Basic Syntax",
            "difficulty_level": DifficultyLevel.BEGINNER,
            "estimated_duration": 60,
            "learning_styles": ["visual", "auditory"],
            "tags": ["python", "tutorial", "video"],
            "complexity_score": 0.3,
            "content_url": "https://example.com/python-basics-video"
        },
        {
            "title": "Python Loops Interactive Exercise",
            "description": "Hands-on practice with for loops, while loops, and loop control statements",
            "content_type": ContentType.INTERACTIVE,
            "subject": "Python Programming",
            "topic": "Control Structures",
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "estimated_duration": 90,
            "learning_styles": ["kinesthetic", "visual"],
            "prerequisites": [1, 2],  # Requires basic syntax materials
            "tags": ["python", "loops", "practice", "interactive"],
            "complexity_score": 0.6
        },
        {
            "title": "Advanced Python: Object-Oriented Programming",
            "description": "Deep dive into classes, inheritance, polymorphism, and design patterns",
            "content_type": ContentType.TEXT,
            "subject": "Python Programming",
            "topic": "Object-Oriented Programming",
            "difficulty_level": DifficultyLevel.ADVANCED,
            "estimated_duration": 120,
            "learning_styles": ["reading_writing", "visual"],
            "prerequisites": [3],  # Requires control structures
            "tags": ["python", "oop", "classes", "inheritance"],
            "complexity_score": 0.9
        },
        
        # Mathematics
        {
            "title": "Algebra Fundamentals",
            "description": "Basic algebraic operations, equations, and problem-solving strategies",
            "content_type": ContentType.TEXT,
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty_level": DifficultyLevel.BEGINNER,
            "estimated_duration": 50,
            "learning_styles": ["reading_writing", "visual"],
            "tags": ["math", "algebra", "equations"],
            "complexity_score": 0.4
        },
        {
            "title": "Calculus Visualization",
            "description": "Interactive visualizations of derivatives, integrals, and limits",
            "content_type": ContentType.INTERACTIVE,
            "subject": "Mathematics",
            "topic": "Calculus",
            "difficulty_level": DifficultyLevel.ADVANCED,
            "estimated_duration": 75,
            "learning_styles": ["visual", "kinesthetic"],
            "prerequisites": [5],  # Requires algebra
            "tags": ["math", "calculus", "visualization"],
            "complexity_score": 0.8
        },
        
        # Data Science
        {
            "title": "Introduction to Data Analysis",
            "description": "Learn data analysis fundamentals using pandas and numpy",
            "content_type": ContentType.VIDEO,
            "subject": "Data Science",
            "topic": "Data Analysis",
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "estimated_duration": 80,
            "learning_styles": ["visual", "auditory"],
            "prerequisites": [1, 2],  # Requires Python basics
            "tags": ["data-science", "pandas", "analysis"],
            "complexity_score": 0.7
        },
        {
            "title": "Machine Learning Quiz",
            "description": "Assessment quiz covering supervised and unsupervised learning concepts",
            "content_type": ContentType.QUIZ,
            "subject": "Data Science",
            "topic": "Machine Learning",
            "difficulty_level": DifficultyLevel.ADVANCED,
            "estimated_duration": 30,
            "learning_styles": ["reading_writing"],
            "prerequisites": [7],  # Requires data analysis
            "tags": ["machine-learning", "quiz", "assessment"],
            "complexity_score": 0.9
        },
        
        # Web Development
        {
            "title": "HTML & CSS Basics",
            "description": "Learn the fundamentals of web markup and styling",
            "content_type": ContentType.TEXT,
            "subject": "Web Development",
            "topic": "Frontend Basics",
            "difficulty_level": DifficultyLevel.BEGINNER,
            "estimated_duration": 60,
            "learning_styles": ["visual", "reading_writing"],
            "tags": ["html", "css", "web", "frontend"],
            "complexity_score": 0.4
        },
        {
            "title": "JavaScript Interactive Coding",
            "description": "Hands-on JavaScript programming with real-time feedback",
            "content_type": ContentType.INTERACTIVE,
            "subject": "Web Development",
            "topic": "JavaScript",
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "estimated_duration": 100,
            "learning_styles": ["kinesthetic", "visual"],
            "prerequisites": [9],  # Requires HTML/CSS
            "tags": ["javascript", "programming", "interactive"],
            "complexity_score": 0.6
        }
    ]
    
    for i, material_data in enumerate(materials, 1):
        material = LearningMaterial(
            id=i,
            **material_data,
            average_rating=random.uniform(3.5, 5.0),
            completion_rate=random.uniform(0.6, 0.95),
            effectiveness_score=random.uniform(0.7, 0.95),
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        
        # Check if material already exists
        existing = db.query(LearningMaterial).filter(LearningMaterial.id == i).first()
        if not existing:
            db.add(material)
    
    db.commit()


def create_sample_students(db: Session):
    """Create sample students with different learning profiles"""
    
    students = [
        {
            "username": "alice_chen",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Chen",
            "age": 22,
            "learning_style_scores": {"visual": 0.4, "auditory": 0.2, "kinesthetic": 0.1, "reading_writing": 0.3},
            "dominant_learning_style": "visual",
            "difficulty_preference": "intermediate",
            "performance_score": 85.0,
            "learning_rate": 1.2,
            "retention_rate": 0.85
        },
        {
            "username": "bob_garcia",
            "email": "bob@example.com", 
            "first_name": "Bob",
            "last_name": "Garcia",
            "age": 19,
            "learning_style_scores": {"visual": 0.2, "auditory": 0.4, "kinesthetic": 0.3, "reading_writing": 0.1},
            "dominant_learning_style": "auditory",
            "difficulty_preference": "beginner",
            "performance_score": 72.0,
            "learning_rate": 0.9,
            "retention_rate": 0.75
        },
        {
            "username": "carol_smith", 
            "email": "carol@example.com",
            "first_name": "Carol",
            "last_name": "Smith",
            "age": 25,
            "learning_style_scores": {"visual": 0.25, "auditory": 0.15, "kinesthetic": 0.45, "reading_writing": 0.15},
            "dominant_learning_style": "kinesthetic",
            "difficulty_preference": "advanced",
            "performance_score": 92.0,
            "learning_rate": 1.5,
            "retention_rate": 0.9
        }
    ]
    
    for i, student_data in enumerate(students, 1):
        # Check if student already exists
        existing = db.query(Student).filter(Student.username == student_data["username"]).first()
        if not existing:
            student = Student(
                **student_data,
                hashed_password=get_password_hash("password123"),  # Default password for demo
                total_study_time=random.randint(500, 2000),
                learning_streak=random.randint(1, 15),
                created_at=datetime.now() - timedelta(days=random.randint(7, 60))
            )
            db.add(student)
    
    db.commit()


def create_sample_progress(db: Session):
    """Create sample progress records"""
    
    students = db.query(Student).all()
    materials = db.query(LearningMaterial).all()
    
    if not students or not materials:
        return
    
    for student in students:
        # Create 5-10 progress records per student
        num_records = random.randint(5, 10)
        selected_materials = random.sample(materials, min(num_records, len(materials)))
        
        for i, material in enumerate(selected_materials):
            # Vary completion and performance based on student's learning style
            style_match = material.learning_styles and student.dominant_learning_style in material.learning_styles
            
            if style_match:
                completion_pct = random.uniform(70, 100)
                score = random.uniform(75, 95)
                engagement = random.uniform(0.7, 1.0)
            else:
                completion_pct = random.uniform(30, 85)
                score = random.uniform(55, 80)
                engagement = random.uniform(0.4, 0.7)
            
            completion_status = "completed" if completion_pct >= 95 else "in_progress"
            time_spent = random.randint(20, material.estimated_duration + 30) if material.estimated_duration else random.randint(20, 90)
            
            # Check if progress already exists
            existing = db.query(Progress).filter(
                Progress.student_id == student.id,
                Progress.learning_material_id == material.id
            ).first()
            
            if not existing:
                progress = Progress(
                    student_id=student.id,
                    learning_material_id=material.id,
                    completion_status=completion_status,
                    completion_percentage=completion_pct,
                    time_spent=time_spent,
                    score=score,
                    attempts=random.randint(1, 3),
                    mastery_level=min(1.0, score / 100.0) if completion_status == "completed" else completion_pct / 200.0,
                    engagement_score=engagement,
                    confidence_score=random.uniform(0.5, 0.9),
                    difficulty_rating=random.uniform(2.0, 5.0),
                    started_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    completed_at=datetime.now() - timedelta(days=random.randint(0, 5)) if completion_status == "completed" else None,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 20))
                )
                db.add(progress)
    
    db.commit()


def populate_sample_data():
    """Main function to populate the database with sample data"""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        print("Creating sample learning materials...")
        create_sample_learning_materials(db)
        
        print("Creating sample students...")
        create_sample_students(db)
        
        print("Creating sample progress records...")
        create_sample_progress(db)
        
        print("Sample data creation completed!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    populate_sample_data()