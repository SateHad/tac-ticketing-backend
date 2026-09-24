-- Wipe everything cleanly
TRUNCATE TABLE ticket_feedback, ticket_audit_log, tickets, agent_skills, tac, skills, customers, locations RESTART IDENTITY CASCADE;

-- 1. Insert 3 Base Locations
INSERT INTO locations (City, Country, Timezone) VALUES
('Amman', 'Jordan', '+03:00'),
('Düsseldorf', 'Germany', '+01:00'),
('London', 'UK', '+00:00');

-- 2. Insert 15 Realistic Customers
INSERT INTO customers (Company_Name, Account_Tier, Contact_Email, Company_Phone_Number)
SELECT
    (ARRAY['Apex Managed Services', 'NeuroTech Enterprise', 'Global Logistics Co', 'Pinnacle Data Systems', 'NextGen Communications'])[floor(random() * 5 + 1)::int] || ' ' || i,
    floor(random() * 3 + 1)::smallint,
    'noc@company' || i || '.com',
    '+9627900000' || lpad(i::text, 2, '0')
FROM generate_series(1, 15) i;

-- 3. Insert 5 Core Skills
INSERT INTO skills (Skill_Name) VALUES
('Unified Communications (CUCM)'), ('VSaaS & Cloud Storage'), ('Linux & Server Admin'), ('Database Architecture'), ('AI Workflow Automation');

-- 4. Insert 10 Realistic Agents
INSERT INTO tac (Agent_Name, Technical_Tier, Location_Id)
SELECT
    (ARRAY['Tariq Haddad', 'Sarah Müller', 'Yazan Al-Fayed', 'Layla Mansour', 'Marcus Schmidt', 'Omar Zaid', 'Elena Weber', 'Kareem Naser', 'Jana Weiss', 'Ali Mahmoud'])[i],
    floor(random() * 3 + 1)::smallint,
    floor(random() * 3 + 1)::int
FROM generate_series(1, 10) i;

-- 5. Give every agent a random skill
INSERT INTO agent_skills (Skill_Id, Agent_Id)
SELECT floor(random() * 5 + 1)::int, Agent_Id FROM tac;

-- 6. Disable protection trigger and insert 3000 Realistic Tickets
ALTER TABLE tickets DISABLE TRIGGER closed_ticket_protection;

INSERT INTO tickets (Customer_Id, Agent_Id, Ticket_Subject, Severity_Level, Status, Created_Timestamp, Solved_Timestamp)
SELECT
    floor(random() * 15 + 1)::int,
    floor(random() * 10 + 1)::int,
    (ARRAY[
        'CUCM routing failure on main SIP trunk',
        'VSaaS cloud storage synchronization dropping frames',
        'n8n RAG webhook timing out during client queries',
        'PostgreSQL Docker container crashing on high load',
        'Scapy packet sniffer script dropping 802.1Q tags',
        'Cisco Unity voicemail provisioning error',
        'Arch Linux kernel panic on workstation reboot',
        'Adminer GUI rejecting valid database credentials'
    ])[floor(random() * 8 + 1)::int],
    floor(random() * 4 + 1)::smallint,
    (ARRAY['Open', 'In Progress', 'Closed', 'Closed'])[floor(random() * 4 + 1)::int],
    NOW() - (random() * 180 || ' days')::interval,
    NULL
FROM generate_series(1, 3000) i;

-- 7. Add Solved Timestamps to 'Closed' tickets
UPDATE tickets
SET Solved_Timestamp = Created_Timestamp + (random() * 5 || ' days')::interval
WHERE Status = 'Closed';

-- Re-enable protection trigger
ALTER TABLE tickets ENABLE TRIGGER closed_ticket_protection;

-- 8. Insert Realistic Feedback
INSERT INTO ticket_feedback (Ticket_Id, Rating, Customer_Comment)
SELECT
    Ticket_Id,
    floor(random() * 5 + 1)::smallint,
    (ARRAY['Resolved quickly, good comms.', 'Agent was helpful.', 'Took too long to escalate to Tier 2.', 'Clear updates provided throughout the outage.'])[floor(random() * 4 + 1)::int]
FROM tickets
WHERE Status = 'Closed'
LIMIT 1000;