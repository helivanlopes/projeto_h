from app.models import db, Ticket
from datetime import datetime, timedelta

def cleanup_abandoned_tickets():
    # Example logic: Cancel tickets that have been 'aberto' for more than 7 days
    threshold_date = datetime.utcnow() - timedelta(days=7)
    abandoned_tickets = Ticket.query.filter(
        Ticket.status == 'aberto',
        Ticket.data_criacao < threshold_date
    ).all()
    
    for ticket in abandoned_tickets:
        ticket.status = 'cancelado'
    
    db.session.commit()
