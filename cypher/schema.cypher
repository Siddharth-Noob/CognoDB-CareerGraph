// CareerGraph data model
// (:Person)-[:HAS_SKILL]->(:Skill)<-[:REQUIRES]-(:Role)-[:OFFERED_BY]->(:Company)

CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name);
CREATE INDEX role_id IF NOT EXISTS FOR (r:Role) ON (r.id);
