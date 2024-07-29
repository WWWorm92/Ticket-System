from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Убедитесь, что ключ достаточно сложный и уникальный

TICKETS_FILE = 'tickets.json'


def load_tickets():
    if os.path.exists(TICKETS_FILE) and os.path.getsize(TICKETS_FILE) > 0:
        with open(TICKETS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []


def save_tickets(tickets):
    with open(TICKETS_FILE, 'w', encoding='utf-8') as file:
        json.dump(tickets, file, ensure_ascii=False, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form['user']
        issue = request.form['issue']
        status = 'not_started'
        tickets = load_tickets()
        tickets.append({'user': user, 'issue': issue, 'status': status, 'comments': []})
        save_tickets(tickets)
        flash('Ваш тикет был успешно отправлен!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html')


@app.route('/tickets', methods=['GET'])
def view_tickets():
    tickets = load_tickets()
    return render_template('tickets.html', tickets=tickets)


@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def view_ticket(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        return render_template('ticket_detail.html', ticket=ticket, ticket_id=ticket_id)
    return redirect(url_for('view_tickets'))


@app.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
def add_comment(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        comment = request.form.get('comment')
        if ticket.get('comments') is None:
            ticket['comments'] = []
        ticket['comments'].append(comment)
        save_tickets(tickets)  # Не забудьте сохранить изменения
        return redirect(url_for('view_tickets'))
    return '', 404



@app.route('/tickets/<int:ticket_id>')
def ticket_detail(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        return render_template('ticket_modal_content.html', ticket=ticket)
    return 'Ticket not found', 404



if __name__ == '__main__':
    if not os.path.exists(TICKETS_FILE):
        save_tickets([])
    app.run(debug=True)
