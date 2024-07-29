from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import json

app = Flask(__name__)

TICKETS_FILE = 'tickets.json'
app.secret_key = '1qazxsw2'

def load_tickets():
    with open(TICKETS_FILE, 'r') as file:
        return json.load(file)

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w') as file:
        json.dump(tickets, file, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form['user']
        issue = request.form['issue']
        tickets = load_tickets()
        ticket_id = len(tickets) + 1
        tickets.append({'id': ticket_id, 'user': user, 'issue': issue, 'status': 'not_started', 'comments': []})
        save_tickets(tickets)
        flash('Тикет успешно отправлен', 'success')
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/tickets', methods=['GET'])
def tickets():
    tickets = load_tickets()
    return render_template('tickets.html', tickets=tickets)

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def ticket_detail(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        return render_template('ticket_modal_content.html', ticket=ticket)
    return 'Ticket not found', 404

@app.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
def add_comment(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        comment = request.form.get('comment', '').strip()
        if comment:
            if 'comments' not in ticket:
                ticket['comments'] = []
            ticket['comments'].append(comment)
            save_tickets(tickets)
    return redirect(url_for('tickets'))

@app.route('/tickets/<int:ticket_id>/status', methods=['POST'])
def update_status(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        new_status = request.form.get('status')
        if new_status in ['not_started', 'in_progress', 'closed', 'cannot_resolve']:
            ticket['status'] = new_status
            save_tickets(tickets)
    return redirect(url_for('tickets'))

if __name__ == '__main__':
    app.run(debug=True)
