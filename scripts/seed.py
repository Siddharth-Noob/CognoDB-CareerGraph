import os
from neo4j import GraphDatabase

URI = os.getenv("COGNODB_URI", "")
USERNAME = os.getenv("COGNODB_USERNAME", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD", "")

if not URI or not PASSWORD:
    raise SystemExit("Set COGNODB_URI and COGNODB_PASSWORD before seeding.")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

people = [
    {"id": "p1", "name": "Aarav Mehta", "skills": ["Python", "GraphQL", "Docker"]},
    {"id": "p2", "name": "Maya Singh", "skills": ["Python", "SQL", "Machine Learning"]},
    {"id": "p3", "name": "Kabir Rao", "skills": ["Java", "Spring Boot", "Docker"]},
    {"id": "p4", "name": "Ishita Shah", "skills": ["TypeScript", "React", "GraphQL"]},
    {"id": "p5", "name": "Rohan Kapoor", "skills": ["Python", "SQL", "Docker"]},
    {"id": "p6", "name": "Ananya Das", "skills": ["Java", "Spring Boot", "SQL"]},
]

skills = ["Python", "GraphQL", "Docker", "SQL", "Machine Learning", "Java", "Spring Boot", "TypeScript", "React"]
companies = [
    {"id": "c1", "name": "Nova Systems", "industry": "Developer Tools"},
    {"id": "c2", "name": "Vertex Labs", "industry": "AI & Data"},
    {"id": "c3", "name": "Orbit Commerce", "industry": "E-commerce"},
]
roles = [
    {"id": "r1", "title": "Backend Engineer", "level": "Mid", "company": "c1", "skills": ["Python", "Docker", "SQL"]},
    {"id": "r2", "title": "Graph Platform Engineer", "level": "Senior", "company": "c1", "skills": ["Python", "GraphQL", "Docker"]},
    {"id": "r3", "title": "ML Engineer", "level": "Mid", "company": "c2", "skills": ["Python", "Machine Learning", "SQL"]},
    {"id": "r4", "title": "Full Stack Engineer", "level": "Mid", "company": "c3", "skills": ["TypeScript", "React", "SQL"]},
    {"id": "r5", "title": "Java Platform Engineer", "level": "Senior", "company": "c2", "skills": ["Java", "Spring Boot", "Docker"]},
]

with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    session.run("""
        UNWIND $skills AS name
        CREATE (:Skill {name: name})
    """, skills=skills)
    session.run("""
        UNWIND $companies AS c
        CREATE (:Company {id: c.id, name: c.name, industry: c.industry})
    """, companies=companies)
    session.run("""
        UNWIND $roles AS r
        MATCH (c:Company {id: r.company})
        CREATE (role:Role {id: r.id, title: r.title, level: r.level})
        CREATE (role)-[:OFFERED_BY]->(c)
        WITH role, r
        UNWIND r.skills AS skill_name
        MATCH (s:Skill {name: skill_name})
        CREATE (role)-[:REQUIRES]->(s)
    """, roles=roles)
    session.run("""
        UNWIND $people AS p
        CREATE (person:Person {id: p.id, name: p.name})
        WITH person, p
        UNWIND p.skills AS skill_name
        MATCH (s:Skill {name: skill_name})
        CREATE (person)-[:HAS_SKILL]->(s)
    """, people=people)
    session.run("CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name)")
    session.run("CREATE INDEX role_id IF NOT EXISTS FOR (r:Role) ON (r.id)")

print("Seeded CareerGraph successfully.")
driver.close()
