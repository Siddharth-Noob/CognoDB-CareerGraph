// 1. Explore roles and their required skills.
MATCH (r:Role)-[:REQUIRES]->(s:Skill)
RETURN r.title AS role, r.level AS level, collect(s.name) AS skills
ORDER BY role;

// 2. Multi-hop: discover roles and companies connected to a skill through people.
MATCH (s:Skill)<-[:HAS_SKILL]-(p:Person)
MATCH (r:Role)-[:REQUIRES]->(s)
MATCH (r)-[:OFFERED_BY]->(c:Company)
RETURN s.name AS skill, p.name AS person, r.title AS role, c.name AS company
ORDER BY skill, role;

// 3. Graph-native recommendation: roles sharing skills with a person.
MATCH (p:Person {name: $person_name})-[:HAS_SKILL]->(s:Skill)<-[:REQUIRES]-(r:Role)
MATCH (r)-[:REQUIRES]->(other:Skill)
RETURN r.title AS role, count(DISTINCT s) AS matched_skills,
       collect(DISTINCT other.name) AS required_skills
ORDER BY matched_skills DESC, role
LIMIT 10;

// 4. A relationally awkward query: identify people who form a skill bridge
// between two roles, then return the company pair they connect.
MATCH (r1:Role)-[:REQUIRES]->(shared:Skill)<-[:HAS_SKILL]-(p:Person)-[:HAS_SKILL]->(shared2:Skill)<-[:REQUIRES]-(r2:Role)
WHERE r1.id < r2.id AND shared.name <> shared2.name
MATCH (r1)-[:OFFERED_BY]->(c1:Company)
MATCH (r2)-[:OFFERED_BY]->(c2:Company)
RETURN p.name AS connector, r1.title AS role_a, c1.name AS company_a,
       r2.title AS role_b, c2.name AS company_b,
       collect(DISTINCT shared.name) + collect(DISTINCT shared2.name) AS bridge_skills
ORDER BY connector;
