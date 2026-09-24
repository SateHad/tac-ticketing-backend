import psycopg2
import psycopg2.extras
from datetime import datetime

connection = psycopg2.connect(
    database="postgres", 
    user="postgres", 
    password="securepass", 
    host="db", 
    port=5432
)

def add_agent(agent_name, technical_tier, location_id, skill_ids):
    with connection.cursor() as cursor:

        agent_query = """
            INSERT INTO tac (agent_name, technical_tier, location_id)
            VALUES (%s, %s, %s)
            RETURNING agent_id;
        """
        insert_skill_query = """
            INSERT INTO agent_skills (skill_id, agent_id)
            VALUES (%s, %s)
        """
        skill_query = """
            SELECT skill_name FROM skills
            WHERE skill_id = %s;
        """

        try:
            cursor.execute(agent_query, (agent_name, technical_tier, location_id))
            new_agent_id = cursor.fetchone()[0]

            for skill in skill_ids:
                cursor.execute(insert_skill_query, (int(skill), new_agent_id))

            print(f"Agent {agent_name} added with ID {new_agent_id}")

            for i in skill_ids:
                cursor.execute(skill_query, (int(i),))
                row = cursor.fetchone()
                skill_name = row[0]
                print(f"Agent skills: {skill_name}")

            connection.commit() 
            return new_agent_id

        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()

def add_customer(company_name, account_tier, contact_email, company_phone_number):
    with connection.cursor() as cursor:

        customer_query = """
            INSERT INTO customers (company_name, account_tier, contact_email, company_phone_number)
            VALUES (%s, %s, %s, %s)
            RETURNING customer_id;
        """

        try:
            cursor.execute(customer_query, (company_name, account_tier, contact_email, company_phone_number))
            new_customer_id = cursor.fetchone()[0]

            print(f"Customer {company_name} with ID {new_customer_id}")

            connection.commit()
            return new_customer_id
        
        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()

def add_ticket(company_name, agent_name, ticket_subject, severity_level, status):
    with connection.cursor() as cursor:

        customer_id_query = """
            SELECT customer_id FROM customers
            WHERE company_name = %s;
        """

        agent_id_query = """
            SELECT agent_id FROM tac
            WHERE agent_name = %s; 
        """

        ticket_query = """
            INSERT INTO tickets (customer_id, agent_id, ticket_subject, severity_level, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING ticket_id;
        """

        try:
            cursor.execute(customer_id_query, (company_name,))
            row = cursor.fetchone()
            if not row:
                print(f"Error: Customer '{company_name}' not found.")
                return
            foreign_customer_id = row[0]
            
            cursor.execute(agent_id_query, (agent_name,))
            row = cursor.fetchone()
            if not row:
                print(f"Error: Agent '{agent_name}' not found.")
                return
            foreign_agent_id = row[0]

            cursor.execute(ticket_query, (foreign_customer_id, foreign_agent_id, ticket_subject, severity_level, status))
            new_ticket_id = cursor.fetchone()[0]
            print(f"Ticket Created #{new_ticket_id}: {company_name} needs help solving {ticket_subject}")

            connection.commit()
            return new_ticket_id

        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()

def ticket_closing(ticket_id):
    with connection.cursor() as cursor:

        ticket_query = """
            UPDATE tickets
            SET status = 'Closed',
                solved_timestamp = NOW()
            WHERE ticket_id = %s;
        """

        try:
            cursor.execute(ticket_query, (ticket_id,))

            if cursor.rowcount == 0:
                print(f"Warning: No ticket found with ID {ticket_id}.")
                return False

            now = datetime.now()
            print(f"Ticket {ticket_id} has been solved. Solve time: {now}")

            connection.commit()
            return True

        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()

def new_agent(ticket_id, agent_id):
    with connection.cursor() as cursor:

        agent_query = """
            UPDATE tickets
            SET agent_id = %s
            WHERE ticket_id = %s;
        """

        name_query = """
            SELECT agent_name
            FROM tac
            WHERE agent_id = %s;
        """

        try:
            cursor.execute(agent_query, (agent_id, ticket_id))

            if cursor.rowcount == 0:
                print(f"Warning: No ticket found with ID {ticket_id}.")
                return False

            cursor.execute(name_query, (agent_id,))
            row = cursor.fetchone()
            new_agent_name = row[0]
            
            print(f"Ticket {ticket_id} is now assigned to agent {new_agent_name}")

            connection.commit()
            return True

        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()

def add_feedback(ticket_id, rating, customer_comment=None):
    with connection.cursor() as cursor:

        feedback_query = """
            INSERT INTO ticket_feedback (ticket_id, rating, customer_comment)
            VALUES (%s, %s, %s)
            RETURNING feedback_id;
        """        

        try:
            cursor.execute(feedback_query, (ticket_id, rating, customer_comment))
            new_feedback_id = cursor.fetchone()[0]

            if customer_comment is not None:
                print(f"Feedback {new_feedback_id}: Achieved a {rating} rating with a comment '{customer_comment}'")
            else:
                print(f"Feedback {new_feedback_id}: Achieved a {rating} rating.")

            connection.commit()
            return new_feedback_id

        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()

def get_all_customers():
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM customers;")
        return cursor.fetchall()

def get_all_agents():
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM tac;")
        return cursor.fetchall()

def get_all_tickets():
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM tickets;")
        return cursor.fetchall()

def get_tickets_page(limit, offset):
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM tickets;")
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT * FROM tickets
            ORDER BY ticket_id
            LIMIT %s OFFSET %s;
            """,
            (limit, offset)
        )
        rows = cursor.fetchall()
        return rows, total

def get_all_feedback():
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM ticket_feedback;")
        return cursor.fetchall()

def get_feedback_page(limit, offset):
    with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM ticket_feedback;")
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT * FROM ticket_feedback
            ORDER BY feedback_id
            LIMIT %s OFFSET %s;
            """,
            (limit, offset)
        )
        rows = cursor.fetchall()
        return rows, total

if __name__ == "__main__":
    pass