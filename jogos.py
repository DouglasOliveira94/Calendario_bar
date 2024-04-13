from flask import Flask, render_template, request
import datetime
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Arquivo CSV para armazenar os horários agendados
CSV_FILE = 'horarios_agendados.csv'

def check_availability(date):
    # Verifica se o dia é uma quinta-feira
    if date.weekday() == 3:
        return True
    else:
        return False

def load_scheduled_dates():
    scheduled_dates = set()
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Verifica se a lista não está vazia
                    scheduled_dates.add(datetime.datetime.strptime(row[0], '%Y-%m-%d'))
    except FileNotFoundError:
        pass
    return scheduled_dates

def save_scheduled_date(date):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date.strftime('%Y-%m-%d')])

# Lista para armazenar as datas selecionadas
selected_dates = load_scheduled_dates()

def send_confirmation_email(team_name, selected_date, recipient_email, phone):
    # Configurações do servidor SMTP do Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  # Porta para SSL
    smtp_username = ''  # Seu endereço de e-mail do Gmail
    smtp_password = ''  # Sua senha de aplicativo ou senha do Gmail

    # Construindo o e-mail
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = 'Confirmação de Agendamento de Jogo'

    body = f"""Olá {team_name},

Seu jogo foi agendado com sucesso para o dia {selected_date}.

O valor do jogo é R$ 37,50.
O número registrado é: {phone}
Dois dias antes do jogo entraremos em contato com o numero registrado para confirmar a presença do time adversário.
Caso tenha alguma duvida mande mensagem no whats para 5199858530
Atenciosamente,
Equipe Bar de Munique"""

    msg.attach(MIMEText(body, 'plain'))

    # Enviando o e-mail
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient_email, msg.as_string())
        print(f"E-mail de confirmação enviado com sucesso para {recipient_email}.")
    except smtplib.SMTPAuthenticationError:
        print("Erro de autenticação SMTP: As credenciais fornecidas são inválidas.")
    except smtplib.SMTPException as e:
        print(f"Erro ao enviar o e-mail de confirmação para {recipient_email}: {e}")
    finally:
        server.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    selected_date = request.form.get('selected_date')
    if selected_date:
        year, month, day = map(int, selected_date.split('-'))
        game_date = datetime.datetime(year, month, day)

        if game_date in selected_dates:
            return render_template('unavailable.html', selected_date=selected_date)
        elif check_availability(game_date):
            selected_dates.add(game_date)
            save_scheduled_date(game_date)
            return render_template('schedule.html', selected_date=selected_date)
        else:
            return render_template('unavailable.html', selected_date=selected_date)
    else:
        return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    team_name = request.form.get('team_name')
    phone = request.form.get('phone')
    selected_date = request.form.get('selected_date')
    recipient_email = request.form.get('email')

    if team_name and phone and selected_date and recipient_email:
        send_confirmation_email(team_name, selected_date, recipient_email, phone)
        send_confirmation_email(team_name, selected_date, '', phone) #coloque seu email para ir um email para voce tambem
        return render_template('confirmation.html', team_name=team_name, selected_date=selected_date)
    else:
        return 'Por favor, preencha todos os campos do formulário.'

if __name__ == "__main__":
    app.run(debug=True)
