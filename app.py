from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json

app = Flask(__name__)
app.secret_key = '123'  # Замените на ваш уникальный секретный ключ

# Настройки Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def load_tickets():
    try:
        with open('tickets.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_tickets(tickets):
    with open('tickets.json', 'w') as file:
        json.dump(tickets, file, indent=4)

def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            return User(user['id'], user['username'], user['password'], user['role'])
    return None

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        user = current_user.username
        issue = request.form['issue']
        tickets = load_tickets()
        ticket_id = len(tickets) + 1
        tickets.append({'id': ticket_id, 'user': user, 'issue': issue, 'status': 'not_started', 'comments': []})
        save_tickets(tickets)
        flash('Тикет успешно отправлен', 'success')
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/tickets')
@login_required
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                user_obj = User(user['id'], username, user['password'], user['role'])
                login_user(user_obj)
                return redirect(url_for('index'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        users = load_users()
        user_id = f"{len(users) + 1}"
        users.append({'id': user_id, 'username': username, 'password': password, 'role': role})
        save_users(users)
        flash('Пользователь добавлен', 'success')
        return redirect(url_for('add_user'))
    return render_template('add_user.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        users = load_users()
        for user in users:
            if user['id'] == current_user.id:
                if user['password'] == old_password:
                    user['password'] = new_password
                    save_users(users)
                    flash('Пароль успешно изменен', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Неверный старый пароль', 'danger')
        flash('Ошибка изменения пароля', 'danger')
    return render_template('change_password.html')


if __name__ == '__main__':
    app.run(debug=True)
