import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from neo4j import GraphDatabase

load_dotenv()

app = Flask(__name__)

URI = os.getenv("COGNODB_URI", "")
USERNAME = os.getenv("COGNODB_USERNAME", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD", "")


def get_driver():
    if not URI or not PASSWORD:
        return None
    return GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def run_query(query, params=None):
    driver = get_driver()
    if driver is None:
        raise RuntimeError("CognoDB is not configured. Set COGNODB_URI and COGNODB_PASSWORD.")
    try:
        with driver.session() as session:
            return [record.data() for record in session.run(query, params or {})]
    finally:
        driver.close()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    try:
        rows = run_query("RETURN 1 AS ok")
        return jsonify({"status": "ok", "database": "connected", "result": rows[0]["ok"]})
    except Exception as exc:
        return jsonify({"status": "degraded", "database": "unavailable", "message": str(exc)}), 503


@app.get("/api/roles")
def roles():
    try:
        rows = run_query("""
            MATCH (r:Role)
            OPTIONAL MATCH (r)-[:REQUIRES]->(s:Skill)
            RETURN r.id AS id, r.title AS title, r.level AS level,
                   collect(s.name) AS skills
            ORDER BY r.title
        """)
        return jsonify(rows)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


@app.get("/api/roles/<role_id>/path")
def role_path(role_id):
    query = """
        MATCH (target:Role {id: $role_id})
        OPTIONAL MATCH (target)-[:REQUIRES]->(s:Skill)<-[:HAS_SKILL]-(person:Person)
        WITH target, s, collect(DISTINCT person.name) AS people
        WITH target, collect(DISTINCT {name: s.name, people: people}) AS skill_data
        RETURN target {.*, skills: skill_data} AS role
    """
    try:
        rows = run_query(query, {"role_id": role_id})
        return jsonify(rows[0]["role"] if rows else None)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


@app.get("/api/recommendations")
def recommendations():
    skill = request.args.get("skill", "").strip()
    if not skill:
        return jsonify({"error": "skill is required"}), 400

    query = """
        MATCH (s:Skill)
        WHERE toLower(s.name) CONTAINS toLower($skill)
        MATCH (s)<-[:HAS_SKILL]-(person:Person)
        MATCH (role:Role)-[:REQUIRES]->(s)
        MATCH (role)-[:OFFERED_BY]->(company:Company)
        OPTIONAL MATCH (role)-[:REQUIRES]->(other:Skill)
        WITH role, company, collect(DISTINCT other.name) AS skills,
             collect(DISTINCT person.name) AS people
        RETURN role.id AS id, role.title AS title, role.level AS level,
               company.name AS company, skills, people
        ORDER BY role.title
        LIMIT 12
    """
    try:
        return jsonify(run_query(query, {"skill": skill}))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


@app.get("/api/network")
def network():
    query = """
        MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)<-[:REQUIRES]-(r:Role)-[:OFFERED_BY]->(c:Company)
        RETURN p.name AS person, s.name AS skill, r.title AS role, c.name AS company
        ORDER BY person, role
        LIMIT 80
    """
    try:
        return jsonify(run_query(query))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
