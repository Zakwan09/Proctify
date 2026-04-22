#!/usr/bin/env python3
"""
Seed script — run once to populate the database with test data.
Usage:  cd backend && python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.exam import Exam, Question, ExamAssignment, ExamStatus
from app.core.security import hash_password
import uuid

db = SessionLocal()

print("Seeding database...")

# ── Create examiner ───────────────────────────────────────────────────────────
examiner = db.query(User).filter(User.email == "examiner@proctify.com").first()
if not examiner:
    examiner = User(
        email="examiner@proctify.com",
        full_name="Dr. Sarah Johnson",
        password=hash_password("Examiner@123"),
        role=UserRole.examiner,
        is_active=True,
    )
    db.add(examiner)
    db.commit()
    db.refresh(examiner)
    print(f"  Created examiner: examiner@proctify.com / Examiner@123")
else:
    print(f"  Examiner already exists: {examiner.email}")

# ── Create candidates ─────────────────────────────────────────────────────────
candidates = []
candidate_data = [
    ("alice@student.com",   "Alice Chen",    "Student@123"),
    ("bob@student.com",     "Bob Martinez",  "Student@123"),
    ("charlie@student.com", "Charlie Singh", "Student@123"),
]
for email, name, pwd in candidate_data:
    c = db.query(User).filter(User.email == email).first()
    if not c:
        c = User(
            email=email, full_name=name,
            password=hash_password(pwd),
            role=UserRole.candidate, is_active=True,
        )
        db.add(c)
        db.commit()
        db.refresh(c)
        print(f"  Created candidate: {email} / {pwd}")
    else:
        print(f"  Candidate already exists: {email}")
    candidates.append(c)

# ── Create exams ──────────────────────────────────────────────────────────────
exam1 = db.query(Exam).filter(Exam.code == "CS-401").first()
if not exam1:
    exam1 = Exam(
        code="CS-401",
        title="Data Structures & Algorithms",
        subject="Computer Science",
        duration_mins=90,
        passing_score=70,
        status=ExamStatus.active,
        randomize=True,
        created_by=examiner.id,
    )
    db.add(exam1)
    db.commit()
    db.refresh(exam1)
    print(f"  Created exam: CS-401")

    questions_data = [
        ("What is the time complexity of accessing an element in a hash table (average case)?",
         ["O(1)", "O(log n)", "O(n)", "O(n²)"], 0),
        ("Which data structure uses LIFO ordering?",
         ["Queue", "Stack", "Linked List", "Binary Tree"], 1),
        ("In a BST, in-order traversal produces nodes in:",
         ["Random order", "Descending order", "Ascending sorted order", "Only leaf nodes"], 2),
        ("Worst-case time complexity of QuickSort?",
         ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 1),
        ("Space complexity of Merge Sort?",
         ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 2),
        ("Which traversal uses a queue internally?",
         ["DFS", "BFS", "Inorder", "PostOrder"], 1),
        ("Height of a balanced binary tree with n nodes:",
         ["O(n)", "O(√n)", "O(log n)", "O(n log n)"], 2),
        ("Which sorting algorithm is stable?",
         ["Quick Sort", "Heap Sort", "Merge Sort", "Selection Sort"], 2),
        ("Adjacency matrix space complexity for V vertices:",
         ["O(V)", "O(E)", "O(V+E)", "O(V²)"], 3),
        ("A min-heap guarantees:",
         ["Sorted array", "Root is smallest", "O(1) search", "Balanced tree"], 1),
    ]
    for i, (text, opts, correct) in enumerate(questions_data):
        db.add(Question(exam_id=exam1.id, text=text, options=opts, correct_idx=correct, order_idx=i))
    db.commit()
    print(f"  Added 10 questions to CS-401")
else:
    print(f"  Exam CS-401 already exists")

exam2 = db.query(Exam).filter(Exam.code == "MATH-201").first()
if not exam2:
    exam2 = Exam(
        code="MATH-201",
        title="Calculus Fundamentals",
        subject="Mathematics",
        duration_mins=60,
        passing_score=65,
        status=ExamStatus.scheduled,
        randomize=False,
        created_by=examiner.id,
    )
    db.add(exam2)
    db.commit()
    db.refresh(exam2)
    print(f"  Created exam: MATH-201")

    math_questions = [
        ("What is the derivative of sin(x)?",
         ["cos(x)", "-cos(x)", "sin(x)", "-sin(x)"], 0),
        ("∫x dx equals:",
         ["x²", "x²/2 + C", "2x + C", "x + C"], 1),
        ("The limit of (sin x)/x as x→0 is:",
         ["0", "∞", "1", "undefined"], 2),
        ("Which rule is used for derivative of f(g(x))?",
         ["Product rule", "Quotient rule", "Chain rule", "Power rule"], 2),
        ("Derivative of eˣ is:",
         ["xeˣ⁻¹", "eˣ", "eˣ⁺¹", "ln(x)"], 1),
    ]
    for i, (text, opts, correct) in enumerate(math_questions):
        db.add(Question(exam_id=exam2.id, text=text, options=opts, correct_idx=correct, order_idx=i))
    db.commit()
    print(f"  Added 5 questions to MATH-201")
else:
    print(f"  Exam MATH-201 already exists")

# ── Assign candidates to exams ────────────────────────────────────────────────
from app.models.exam import ExamAssignment
for c in candidates:
    for exam in [exam1, exam2]:
        exists = db.query(ExamAssignment).filter(
            ExamAssignment.exam_id == exam.id,
            ExamAssignment.candidate_id == c.id,
        ).first()
        if not exists:
            db.add(ExamAssignment(exam_id=exam.id, candidate_id=c.id))
print(f"  Assigned all candidates to both exams")
db.commit()

print()
print("✅ Seed complete!")
print()
print("Login credentials:")
print("  EXAMINER:  examiner@proctify.com  /  Examiner@123")
print("  CANDIDATE: alice@student.com      /  Student@123")
print("  CANDIDATE: bob@student.com        /  Student@123")
print("  CANDIDATE: charlie@student.com    /  Student@123")

db.close()
