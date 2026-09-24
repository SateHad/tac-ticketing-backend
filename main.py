from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

import tac_backend

app = FastAPI()

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

class AddCustomer(BaseModel):
    company_name: str
    account_tier: int
    contact_email: str
    company_phone_number: str

@app.post("/customers/", status_code=201)
def create_customer(customer: AddCustomer):
    try:
        new_id = tac_backend.add_customer(
            customer.company_name,
            customer.account_tier,
            customer.contact_email,
            customer.company_phone_number
        )

        if new_id is None:
            raise HTTPException(status_code=500, detail="Database failed")

        return {"message": "Customer created successfully.", "customer_id": new_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")

class AddAgent(BaseModel):
    agent_name: str
    technical_tier: int
    location_id: int
    skill_ids: list [int]

@app.post("/agent/", status_code=201)
def create_agent(tac: AddAgent):
    try:
        new_id = tac_backend.add_agent(
            tac.agent_name,
            tac.technical_tier,
            tac.location_id,
            tac.skill_ids
        )

        if new_id is None:
            raise HTTPException(status_code=500, detail="Database failed")

        return {"message": "Agent created successfully.", "agent_id": new_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")
    
class AddTicket(BaseModel):
    company_name: str
    agent_name: str
    ticket_subject: str
    severity_level: int
    status: str

@app.post("/ticket/", status_code=201)
def create_ticket(ticket: AddTicket):
    try:
        new_id = tac_backend.add_ticket(
            ticket.company_name,
            ticket.agent_name,
            ticket.ticket_subject,
            ticket.severity_level,
            ticket.status
        )

        if new_id is None:
            raise HTTPException(status_code=500, detail="Database failed")

        return {"message": "Ticket created successfully.", "ticket_id": new_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")
    
@app.put("/ticket/{ticket_id}/closing/", status_code=200)
def close_ticket(ticket_id: int):
    try:
        success = tac_backend.ticket_closing(ticket_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ticket Not Found.")
        return {"message": f"Ticktet {ticket_id} successfuly closed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")
    
class ChangeAgent(BaseModel):
    agent_id: int

@app.put("/ticket/{ticket_id}/change/", status_code=200)
def agent_change(ticket_id: int, agent: ChangeAgent):
    try:
        success = tac_backend.new_agent(
            ticket_id,
            agent.agent_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="ID's (Agent/Ticket) Not Found.")
        return {"message": f"Agent {agent.agent_id} is now assigned to ticket {ticket_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")

class AddFeedback(BaseModel):
    ticket_id: int
    rating: int
    customer_comment: str | None = None

@app.post("/feedback/", status_code=201)
def add_feedback(feedback: AddFeedback):
    try:
        new_feedback_id = tac_backend.add_feedback(
            feedback.ticket_id,
            feedback.rating,
            feedback.customer_comment
        )

        if new_feedback_id is None:
            raise HTTPException(status_code=500, detail="Database failed")

        return {"message": "Feedback added successfully", "feedback_id": new_feedback_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")

@app.get("/customers/query/", status_code=200)
def get_customers():
    return tac_backend.get_all_customers()  

@app.get("/agents/query/", status_code=200)
def get_agents():
    return tac_backend.get_all_agents()

@app.get("/tickets/query/", status_code=200)
def get_tickets():
    return tac_backend.get_all_tickets()

@app.get("/tickets/page/", status_code=200)
def get_tickets_page(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    try:
        rows, total = tac_backend.get_tickets_page(limit, offset)
        return {"tickets": rows, "total": total, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")

@app.get("/feedback/query/", status_code=200)
def get_feedback():
    return tac_backend.get_all_feedback()

@app.get("/feedback/page/", status_code=200)
def get_feedback_page(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    try:
        rows, total = tac_backend.get_feedback_page(limit, offset)
        return {"feedback": rows, "total": total, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database failed")