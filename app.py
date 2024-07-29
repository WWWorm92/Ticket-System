from flask import Flask, request, render_template, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Убедитесь, что ключ достаточно сложный и уникальный

TICKETS_FILE = 'tickets.json'


# Функция для загрузки тикетов из файла
def load_tickets():
    if os.path.exists(TICKETS_FILE) and os.path.getsize(TICKETS_FILE) > 0:
        with open(TICKETS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []


# Функция для сохранения тикетов в файл
def save_tickets(tickets):
    with open(TICKETS_FILE, 'w', encoding='utf-8') as file:
        json.dump(tickets, file, ensure_ascii=False, indent=4)


# Главная страница для отправки тикетов
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form['user']
        issue = request.form['issue']
        status = 'not_started'  # Начальный статус тикета
        tickets = load_tickets()
        tickets.append({'user': user, 'issue': issue, 'status': status})
        save_tickets(tickets)
        flash('Ваш тикет был успешно отправлен!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html')


# Страница для просмотра всех тикетов
@app.route('/tickets', methods=['GET'])
def view_tickets():
    tickets = load_tickets()
    return render_template('tickets.html', tickets=tickets)


# Страница для просмотра деталей тикета
@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def view_ticket(ticket_id):
    tickets = load_tickets()
    if 0 <= ticket_id < len(tickets):
        ticket = tickets[ticket_id]
        return render_template('ticket_detail.html', ticket=ticket, ticket_id=ticket_id)
    return redirect(url_for('view_tickets'))


if __name__ == '__main__':
    # Инициализируем файл, если он не существует
    if not os.path.exists(TICKETS_FILE):
        save_tickets([])
    app.run(debug=True)
