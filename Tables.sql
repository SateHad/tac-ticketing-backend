CREATE TABLE locations (
    Location_Id SERIAL NOT NULL PRIMARY KEY,
    City TEXT NOT NULL,
    Country TEXT NOT NULL,
    Timezone TEXT NOT NULL
);

CREATE TABLE customers (
    Customer_Id          SERIAL NOT NULL PRIMARY KEY,
    Company_Name         TEXT         NOT NULL,
    Account_Tier         SMALLINT     NOT NULL,
    Contact_Email        VARCHAR(254) NOT NULL,
    Company_Phone_Number VARCHAR(15)  NOT NULL
);

CREATE TABLE skills (
    Skill_Id SERIAL NOT NULL PRIMARY KEY,
    Skill_Name TEXT NOT NULL
);

CREATE TABLE tac (
    Agent_Id SERIAL NOT NULL PRIMARY KEY,
    Agent_Name TEXT NOT NULL,
    Technical_Tier SMALLINT NOT NULL,
    Location_Id INT NOT NULL REFERENCES locations(Location_Id)
);

CREATE TABLE agent_skills (
    Skill_Id INT NOT NULL REFERENCES skills(Skill_Id),
    Agent_Id INT NOT NULL REFERENCES tac(Agent_Id),
    PRIMARY KEY (Skill_Id, Agent_Id)
);

CREATE TABLE tickets (
    Ticket_Id SERIAL NOT NULL PRIMARY KEY,
    Customer_Id INT NOT NULL REFERENCES customers(Customer_Id),
    Agent_Id INT NOT NULL REFERENCES tac(Agent_Id),
    Ticket_Subject TEXT NOT NULL,
    Severity_Level SMALLINT NOT NULL,
    Status TEXT NOT NULL,
    Created_Timestamp TIMESTAMP NOT NULL,
    Solved_Timestamp TIMESTAMP
);

CREATE TABLE ticket_feedback (
    Feedback_Id SERIAL NOT NULL PRIMARY KEY,
    Ticket_Id INT NOT NULL UNIQUE REFERENCES tickets(Ticket_Id),
    Rating SMALLINT NOT NULL,
    Customer_Comment TEXT
);

CREATE TABLE ticket_audit_log (
    Audit_Id SERIAL NOT NULL PRIMARY KEY,
    Ticket_Id INT NOT NULL REFERENCES tickets(Ticket_Id),
    Changed_Column TEXT NOT NULL,
    Old_Value TEXT NOT NULL,
    New_Value TEXT NOT NULL,
    Changed_Timestamp TIMESTAMP
);

CREATE INDEX index_tickets_status ON tickets (Status);
CREATE INDEX index_tickets_severity ON tickets (Severity_Level);
CREATE INDEX index_tickets_customer ON tickets (Customer_Id);
CREATE INDEX index_tickets_agent ON tickets (Agent_Id);
CREATE INDEX index_tac_locations ON tac (Location_Id);

CREATE OR REPLACE FUNCTION ticket_changes_log()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO ticket_audit_log(Ticket_Id, Changed_Column, Old_Value, New_Value, Changed_Timestamp)
        VALUES (NEW.Ticket_Id, 'Status', OLD.Status, NEW.Status, NOW());
    END IF;
    IF OLD.Severity_Level <> NEW.Severity_Level THEN
        INSERT INTO ticket_audit_log(Ticket_Id, Changed_Column, Old_Value, New_Value, Changed_Timestamp)
        VALUES (NEW.Ticket_Id, 'Severity_Level', OLD.Severity_Level::TEXT, NEW.Severity_Level::TEXT, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_audit_ticket
AFTER UPDATE on tickets
FOR EACH ROW
EXECUTE FUNCTION ticket_changes_log();

CREATE OR REPLACE FUNCTION lock_closed_tickets()
RETURNS TRIGGER AS $$
BEGIN
    IF Old.Status = 'Closed' THEN
        RAISE EXCEPTION 'Cannot modify a closed ticket. Ticket ID = %', OLD.Ticket_Id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER closed_ticket_protection
BEFORE UPDATE on tickets
FOR EACH ROW
EXECUTE FUNCTION lock_closed_tickets();