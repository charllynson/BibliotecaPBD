# gui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QPushButton, QLabel,
    QVBoxLayout, QGridLayout, QHBoxLayout, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy,
    QComboBox, QGroupBox, QListWidget, QListWidgetItem, QRadioButton,
    QDialog, QDialogButtonBox, QTextEdit
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDate
from functools import partial
import os
import re
from datetime import datetime, timedelta

# Importe suas classes de lógica de negócio
from Biblioteca import Biblioteca
from MaterialBibliografico import Livro, Ebook, Revista, Apostila, Trabalho, Resenha
from dados import criar_tabelas

DB_NAME = 'Biblioteca.db'

# === NOVA PALETA DE CORES ===
PRIMARY_COLOR = "#9B27B0"
PRIMARY_LIGHT = "#BA68C8"
PRIMARY_DARK = "#6A0080"
SECONDARY_COLOR = "#3F51B5"
SECONDARY_LIGHT = "#6573C3"
SECONDARY_DARK = "#2C387E"

BG_COLOR = "#F5F5F5"
DARK_BG_COLOR = "#212121"
TITLE_COLOR = "#212121"
TEXT_COLOR = "#212121"
BUTTON_BG_COLOR = PRIMARY_COLOR
BUTTON_TEXT_COLOR = "#FFFFFF"
ACCENT_BG_COLOR = PRIMARY_LIGHT
ACCENT_TEXT_COLOR = "#212121"
ACCENT_BUTTON_COLOR = "#FF4081"
SUCCESS_COLOR = "#4CAF50"
WARNING_COLOR = "#FFC107"
ERROR_COLOR = "#F44336"

class LoanDialog(QDialog):
    def __init__(self, biblioteca, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar empréstimo")
        self.biblioteca = biblioteca
        self.user_id = None
        self.duration_days = 15
        
        main_layout = QVBoxLayout()
        
        # Seleção de usuário para empréstimo
        user_label = QLabel("Selecionar usuário:")
        user_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 4px;")
        
        users = self.biblioteca.listar_usuarios()
        if users:
            for user in users:
                self.user_combo.addItem(f"{user['nome']} ({user['email']})", userData=user['id'])

        # Seleção de duração do empréstimo
        duration_label = QLabel("Duração do empréstimo:")
        duration_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.duration_group = QGroupBox()
        self.duration_group.setStyleSheet("border: none; margin: 0; padding: 0;")
        duration_layout = QHBoxLayout()
        self.radio_15 = QRadioButton("15 dias")
        self.radio_15.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.radio_15.setChecked(True)
        self.radio_30 = QRadioButton("30 dias")
        self.radio_30.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        duration_layout.addWidget(self.radio_15)
        duration_layout.addWidget(self.radio_30)
        self.duration_group.setLayout(duration_layout)
        
        main_layout.addWidget(user_label)
        main_layout.addWidget(self.user_combo)
        main_layout.addWidget(duration_label)
        main_layout.addWidget(self.duration_group)
        
        # Botões de OK/Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)

    def get_loan_details(self):
        self.user_id = self.user_combo.currentData()
        if self.radio_30.isChecked():
            self.duration_days = 30
        else:
            self.duration_days = 15
        return self.user_id, self.duration_days

class ReviewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fazer resenha e avaliar")
        self.review_text = ""
        self.rating = 0.0

        main_layout = QVBoxLayout()
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        review_label = QLabel("Escreva sua resenha:")
        review_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.review_text_edit = QTextEdit()
        self.review_text_edit.setPlaceholderText("Escreva sua resenha aqui...")
        self.review_text_edit.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")

        rating_label = QLabel("Nota (0 a 5):")
        rating_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("Ex: 4.5")
        self.rating_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")

        main_layout.addWidget(review_label)
        main_layout.addWidget(self.review_text_edit)
        main_layout.addWidget(rating_label)
        main_layout.addWidget(self.rating_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_review)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def accept_review(self):
        self.review_text = self.review_text_edit.toPlainText()
        try:
            self.rating = float(self.rating_input.text())
            if not (0 <= self.rating <= 5):
                QMessageBox.warning(self, "Erro", "A nota deve ser entre 0 e 5.")
                return
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Erro", "A nota deve ser um número válido.")
            return
            

class ResetPasswordScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        title_label = QLabel("Redefinir senha")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QGridLayout()
        form_layout.setContentsMargins(150, 40, 150, 20)

        email_label = QLabel("Email:")
        email_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite seu email")
        self.email_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")

        new_password_label = QLabel("Nova senha:")
        new_password_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Digite a nova senha")
        self.new_password_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        
        confirm_password_label = QLabel("Confirmar senha:")
        confirm_password_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirme a nova senha")
        self.confirm_password_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")

        form_layout.addWidget(email_label, 0, 0)
        form_layout.addWidget(self.email_input, 0, 1)
        form_layout.addWidget(new_password_label, 1, 0)
        form_layout.addWidget(self.new_password_input, 1, 1)
        form_layout.addWidget(confirm_password_label, 2, 0)
        form_layout.addWidget(self.confirm_password_input, 2, 1)

        main_layout.addLayout(form_layout)

        reset_button = QPushButton("Redefinir senha")
        reset_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        reset_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        reset_button.clicked.connect(self.reset_password)
        main_layout.addWidget(reset_button, alignment=Qt.AlignCenter)

        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.LOGIN_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def reset_password(self):
        email = self.email_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not all([email, new_password, confirm_password]):
            QMessageBox.warning(self, "Aviso", "Todos os campos são obrigatórios.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Erro", "A nova senha e a confirmação de senha não coincidem.")
            return

        if self.biblioteca.resetar_senha(email, new_password):
            QMessageBox.information(self, "Sucesso", "Sua senha foi redefinida com sucesso.")
            self.main_app.switch_to_screen(self.main_app.LOGIN_INDEX)
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível redefinir a senha. Verifique o e-mail informado.")


class LoginScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        # Adicionar o logo com fundo transparente
        logo_label = QLabel()
        logo_label.setStyleSheet("background-color: transparent;")
        pixmap = QPixmap("logo_UFPel.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(logo_label)
        
        title_label = QLabel("Acervo Digital \nSeja bem-vindo!")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setContentsMargins(150, 40, 150, 20)
        
        email_label = QLabel("Email:")
        email_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite seu email")
        self.email_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        
        password_label = QLabel("Senha:")
        password_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Crie uma senha")
        self.password_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        
        form_layout.addWidget(email_label, 0, 0)
        form_layout.addWidget(self.email_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        
        main_layout.addLayout(form_layout)
        
        login_button = QPushButton("Login")
        login_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        login_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        login_button.clicked.connect(self.fazer_login)
        main_layout.addWidget(login_button, alignment=Qt.AlignCenter)

        aux_buttons_layout = QHBoxLayout()
        aux_buttons_layout.setAlignment(Qt.AlignCenter)
        
        register_button = QPushButton("Cadastrar")
        register_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        register_button.setStyleSheet(f"background-color: {ACCENT_BG_COLOR}; color: {ACCENT_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        register_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.REGISTER_INDEX))
        aux_buttons_layout.addWidget(register_button)
        
        debug_button = QPushButton("Debug")
        debug_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        debug_button.setStyleSheet(f"background-color: {ACCENT_BG_COLOR}; color: {ACCENT_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        debug_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.DEBUG_INDEX))
        aux_buttons_layout.addWidget(debug_button)
        
        main_layout.addLayout(aux_buttons_layout)

        forgot_password_button = QPushButton("Esqueci minha senha?")
        forgot_password_button.setStyleSheet(f"background-color: transparent; color: {SECONDARY_COLOR}; border: none;")
        forgot_password_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.RESET_PASSWORD_INDEX))
        main_layout.addWidget(forgot_password_button, alignment=Qt.AlignCenter)


        self.setLayout(main_layout)

    def fazer_login(self):
        email = self.email_input.text()
        senha = self.password_input.text()
        
        if email and senha:
            user_id = self.biblioteca.login_usuario(email, senha)
            if user_id:
                QMessageBox.information(self, "Sucesso", "Login bem-sucedido!")
                self.main_app.usuario_logado_id = user_id
                self.main_app.switch_to_screen(self.main_app.MAIN_MENU_INDEX)
            else:
                QMessageBox.warning(self, "Erro", "E-mail ou senha incorretos.")
        else:
            QMessageBox.warning(self, "Aviso", "E-mail e senha são obrigatórios.")

class RegisterScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        title_label = QLabel("Cadastrar novo usuário")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setContentsMargins(150, 40, 150, 20)
        
        nome_label = QLabel("Nome:")
        nome_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Digite seu nome completo")
        self.nome_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")

        email_label = QLabel("Email:")
        email_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite um email válido")
        self.email_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        
        password_label = QLabel("Senha:")
        password_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Crie uma senha")
        self.password_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        
        form_layout.addWidget(nome_label, 0, 0)
        form_layout.addWidget(self.nome_input, 0, 1)
        form_layout.addWidget(email_label, 1, 0)
        form_layout.addWidget(self.email_input, 1, 1)
        form_layout.addWidget(password_label, 2, 0)
        form_layout.addWidget(self.password_input, 2, 1)
        
        main_layout.addLayout(form_layout)
        
        register_button = QPushButton("Cadastrar")
        register_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        register_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        register_button.clicked.connect(self.cadastrar_usuario)
        main_layout.addWidget(register_button, alignment=Qt.AlignCenter)
        
        back_button = QPushButton("Voltar para login")
        back_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.LOGIN_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)

    def cadastrar_usuario(self):
        nome = self.nome_input.text()
        email = self.email_input.text()
        senha = self.password_input.text()

        if not all([nome, email, senha]):
            QMessageBox.warning(self, "Aviso", "Todos os campos são obrigatórios.")
            return

        # Validação do formato de e-mail
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Aviso", "Por favor, insira um e-mail válido.")
            return
        
        sucesso = self.biblioteca.cadastrar_usuario(nome, email, senha)
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Usuário {nome} cadastrado com sucesso!")
            self.nome_input.clear()
            self.email_input.clear()
            self.password_input.clear()
            self.main_app.switch_to_screen(self.main_app.LOGIN_INDEX)
        else:
            QMessageBox.warning(self, "Erro", "Erro ao cadastrar usuário. O e-mail pode já estar em uso.")

class MainScreen(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        title_label = QLabel("Bem-vindo(a) ao Acervo!")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        button_layout = QGridLayout()
        button_layout.setContentsMargins(150, 40, 150, 20)
        
        btn_adicionar_material = QPushButton("Adicionar material")
        btn_acervo = QPushButton("Acervo")
        btn_recomendacoes = QPushButton("Recomendações")
        btn_perfil = QPushButton("Meu perfil")
        
        buttons = [btn_adicionar_material, btn_acervo, btn_recomendacoes, btn_perfil]
        for btn in buttons:
            btn.setFont(QFont("Montserrat", 12, QFont.Bold))
            btn.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 25px;")
            
        btn_adicionar_material.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.ADD_MATERIAL_INDEX))
        btn_acervo.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.ACERVO_INDEX))
        btn_recomendacoes.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.RECOMMENDATION_INDEX))
        btn_perfil.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.PROFILE_INDEX))
        
        button_layout.addWidget(btn_perfil, 0, 0, alignment=Qt.AlignCenter)
        button_layout.addWidget(btn_recomendacoes, 0, 1, alignment=Qt.AlignCenter)
        button_layout.addWidget(btn_adicionar_material, 1, 0, alignment=Qt.AlignCenter)
        button_layout.addWidget(btn_acervo, 1, 1, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(button_layout)
        
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        logout_button.clicked.connect(self.main_app.logout)
        main_layout.addWidget(logout_button, alignment=Qt.AlignRight)
        
        self.setLayout(main_layout)

class AddMaterialScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        title_label = QLabel("Adicionar novo material")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setContentsMargins(50, 20, 50, 20)
        
        self.fields = {}
        fields_names = ["Autor:", "Título:", "Ano:", "Gênero:", "Movimento:", "Editora:", "Link:", "Turma:"]
        for i, name in enumerate(fields_names):
            label = QLabel(name)
            label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
            line_edit = QLineEdit()
            line_edit.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(line_edit, i, 1)
            self.fields[name.replace(":", "")] = line_edit

        # Substituição do QComboBox por QRadioButtons
        type_label = QLabel("Tipo de material:")
        type_label.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
        
        type_group_box = QGroupBox()
        type_group_box.setStyleSheet("border: none; margin: 0; padding: 0;")
        type_layout = QVBoxLayout()
        
        self.radio_buttons = {
            "Livro": QRadioButton("Livro"),
            "Apostila": QRadioButton("Apostila"),
            "Ebook": QRadioButton("Ebook"),
            "Revista": QRadioButton("Revista"),
            "Trabalho": QRadioButton("Trabalho"),
            "Resenha": QRadioButton("Resenha"),
        }
        
        for name, radio_btn in self.radio_buttons.items():
            radio_btn.setStyleSheet(f"color: {TEXT_COLOR}; background-color: transparent;")
            type_layout.addWidget(radio_btn)
        
        self.radio_buttons["Livro"].setChecked(True) # Define um valor padrão
        
        type_group_box.setLayout(type_layout)
        
        form_layout.addWidget(type_label, len(fields_names), 0)
        form_layout.addWidget(type_group_box, len(fields_names), 1)

        main_layout.addLayout(form_layout)
        
        add_button = QPushButton("Adicionar material")
        add_button.setFont(QFont("Montserrat", 12, QFont.Bold))
        add_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        add_button.clicked.connect(self.adicionar_material)
        main_layout.addWidget(add_button, alignment=Qt.AlignCenter)
        
        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.MAIN_MENU_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)

    def adicionar_material(self):
        autor = self.fields["Autor"].text()
        titulo = self.fields["Título"].text()
        ano = self.fields["Ano"].text()
        genero = self.fields["Gênero"].text()
        movimento = self.fields.get("Movimento").text()
        editora = self.fields.get("Editora").text()
        link = self.fields.get("Link").text()
        turma = self.fields.get("Turma").text()
        
        tipo = None
        for name, radio_btn in self.radio_buttons.items():
            if radio_btn.isChecked():
                tipo = name
                break

        if not all([autor, titulo, ano, tipo]):
            QMessageBox.warning(self, "Aviso", "Todos os campos marcados como obrigatórios são necessários.")
            return

        try:
            ano_int = int(ano)
        except ValueError:
            QMessageBox.warning(self, "Erro", "O ano deve ser um número inteiro.")
            return
            
        material = None
        user_id = self.main_app.usuario_logado_id
        if tipo == "Livro":
            material = Livro(user_id, autor, titulo, ano_int, genero, movimento, editora)
        elif tipo == "Ebook":
            material = Ebook(user_id, autor, titulo, ano_int, genero, movimento, link)
        elif tipo == "Revista":
            material = Revista(user_id, autor, titulo, ano_int, editora)
        elif tipo == "Apostila":
            material = Apostila(user_id, autor, titulo, ano_int, turma, genero)
        elif tipo == "Trabalho":
            material = Trabalho(user_id, autor, titulo, ano_int)
        elif tipo == "Resenha":
            material = Resenha(user_id, autor, titulo, ano_int)
        
        if material:
            self.biblioteca.adicionar_material(material)
            QMessageBox.information(self, "Sucesso", f"Material '{titulo}' adicionado com sucesso!")
            for field in self.fields.values():
                field.clear()
            self.main_app.acervo_screen.refresh_acervo()
        else:
            QMessageBox.warning(self, "Erro", "Tipo de material inválido ou erro na criação.")

class AcervoScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        title_label = QLabel("Acervo de materiais")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por título...")
        self.search_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        search_button = QPushButton("Buscar")
        search_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        search_button.clicked.connect(self.search_materials)
        clear_button = QPushButton("Limpar Busca")
        clear_button.setStyleSheet(f"background-color: {ACCENT_BG_COLOR}; color: {ACCENT_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        clear_button.clicked.connect(self.refresh_acervo)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        main_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Título", "Autor", "Categoria", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(f"background-color: white; selection-background-color: {SECONDARY_LIGHT}; border: 1px solid #CCCCCC;")
        main_layout.addWidget(self.table)
        
        action_layout = QHBoxLayout()
        borrow_button = QPushButton("Emprestar")
        borrow_button.setStyleSheet(f"background-color: {SUCCESS_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        borrow_button.clicked.connect(self.borrow_material)
        
        return_button = QPushButton("Devolver")
        return_button.setStyleSheet(f"background-color: {WARNING_COLOR}; color: {TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        return_button.clicked.connect(self.return_material)

        review_button = QPushButton("Fazer Resenha")
        review_button.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        review_button.clicked.connect(self.write_review)

        details_button = QPushButton("Ver Detalhes")
        details_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        details_button.clicked.connect(self.show_details)

        remove_button = QPushButton("Remover Selecionado")
        remove_button.setStyleSheet(f"background-color: {ERROR_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        remove_button.clicked.connect(self.remove_material)
        
        action_layout.addWidget(borrow_button)
        action_layout.addWidget(return_button)
        action_layout.addWidget(review_button)
        action_layout.addWidget(details_button)
        action_layout.addWidget(remove_button)

        main_layout.addLayout(action_layout)
        
        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.MAIN_MENU_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)

    def refresh_acervo(self):
        self.search_input.clear()
        self.table.setRowCount(0)
        materiais = self.biblioteca.listar_acervo_com_status()
        if materiais:
            self.table.setRowCount(len(materiais))
            for i, material in enumerate(materiais):
                self.table.setItem(i, 0, QTableWidgetItem(str(material['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(material['titulo']))
                self.table.setItem(i, 2, QTableWidgetItem(material['autor']))
                self.table.setItem(i, 3, QTableWidgetItem(material['categoria']))
                self.table.setItem(i, 4, QTableWidgetItem(material['status']))

    def search_materials(self):
        query = self.search_input.text()
        self.table.setRowCount(0)
        if query:
            materiais = self.biblioteca.buscar_materiais_titulo(query)
            if materiais:
                self.table.setRowCount(len(materiais))
                for i, material in enumerate(materiais):
                    self.table.setItem(i, 0, QTableWidgetItem(str(material['id'])))
                    self.table.setItem(i, 1, QTableWidgetItem(material['titulo']))
                    self.table.setItem(i, 2, QTableWidgetItem(material['autor']))
                    self.table.setItem(i, 3, QTableWidgetItem(material['categoria']))
                    # status
                    status = self.biblioteca.verificar_status_material(material['id'])
                    self.table.setItem(i, 4, QTableWidgetItem(status))

            else:
                QMessageBox.information(self, "Aviso", f"Nenhum material encontrado com o título: '{query}'")
        else:
            self.refresh_acervo()
            
    def remove_material(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um material para remover.")
            return

        reply = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja remover o material selecionado?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            row = selected_rows[0].row()
            material_id = int(self.table.item(row, 0).text())
            if self.biblioteca.remover_material(material_id):
                QMessageBox.information(self, "Sucesso", "Material removido com sucesso!")
                self.refresh_acervo()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover o material.")
    
    def borrow_material(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um material para emprestar.")
            return
        
        row = selected_rows[0].row()
        material_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 4).text()

        if status == "Disponível":
            loan_dialog = LoanDialog(self.biblioteca, self)
            if loan_dialog.exec_() == QDialog.Accepted:
                user_id, duration_days = loan_dialog.get_loan_details()
                
                if user_id is None:
                    QMessageBox.warning(self, "Aviso", "Selecione um usuário para o empréstimo.")
                    return

                data_devolucao_prevista = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d %H:%M:%S')

                if self.biblioteca.registrar_emprestimo(user_id, material_id, data_devolucao_prevista):
                    QMessageBox.information(self, "Sucesso", "Empréstimo registrado com sucesso!")
                    self.refresh_acervo()
                else:
                    QMessageBox.critical(self, "Erro", "Não foi possível registrar o empréstimo.")
        else:
            QMessageBox.warning(self, "Aviso", "Este material não está disponível para empréstimo.")

    def return_material(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um material para devolver.")
            return
        
        row = selected_rows[0].row()
        material_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 4).text()
        
        if status == "Emprestado":
            emprestimo = self.biblioteca.buscar_emprestimo_aberto_material(material_id)
            if emprestimo:
                borrower_info = self.biblioteca.buscar_usuario(emprestimo['usuario_id'])
                reply = QMessageBox.question(self, "Confirmação de devolução", 
                                             f"Confirmar a devolução do material pelo usuário '{borrower_info['nome']}'?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if self.biblioteca.registrar_devolucao(emprestimo['id']):
                        QMessageBox.information(self, "Sucesso", "Devolução registrada com sucesso!")
                        self.refresh_acervo()
                    else:
                        QMessageBox.critical(self, "Erro", "Não foi possível registrar a devolução.")
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível encontrar um empréstimo em aberto para este material.")
        else:
            QMessageBox.warning(self, "Aviso", "Este material não pode ser devolvido, pois não está emprestado.")
    
    def write_review(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um material para fazer a resenha.")
            return

        row = selected_rows[0].row()
        material_id = int(self.table.item(row, 0).text())

        review_dialog = ReviewDialog(self)
        if review_dialog.exec_() == QDialog.Accepted:
            review_text = review_dialog.review_text
            rating = review_dialog.rating

            user_id = self.main_app.usuario_logado_id

            # Adicionar avaliação
            self.biblioteca.avaliar_material(user_id, material_id, rating)

            # Adicionar resenha
            self.biblioteca.escrever_resenha(user_id, material_id, review_text)

            QMessageBox.information(self, "Sucesso", "Resenha e avaliação salvas com sucesso!")
            self.main_app.user_profile_screen.refresh_profile()
    
    def show_details(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um material para ver os detalhes.")
            return
        
        row = selected_rows[0].row()
        material_id = int(self.table.item(row, 0).text())
        self.main_app.material_details_screen.load_details(material_id)
        self.main_app.switch_to_screen(self.main_app.MATERIAL_DETAILS_INDEX)


class MaterialDetailsScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.material_id = None
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.title_label = QLabel("Detalhes do Material")
        self.title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.details_layout = QGridLayout()
        self.details_layout.setContentsMargins(50, 20, 50, 20)

        main_layout.addLayout(self.details_layout)
        
        reviews_box = QGroupBox("Resenhas")
        reviews_box.setFont(QFont("Montserrat", 12, QFont.Bold))
        reviews_box.setStyleSheet(f"background-color: transparent; color: {TEXT_COLOR};")
        reviews_layout = QVBoxLayout()
        self.reviews_list = QListWidget()
        self.reviews_list.setStyleSheet("background-color: white; border-radius: 8px;")
        reviews_layout.addWidget(self.reviews_list)
        reviews_box.setLayout(reviews_layout)
        main_layout.addWidget(reviews_box)

        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.ACERVO_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def load_details(self, material_id):
        self.material_id = material_id
        
        # Limpar layout anterior
        for i in reversed(range(self.details_layout.count())): 
            self.details_layout.itemAt(i).widget().setParent(None)
        
        material = self.biblioteca.buscar_material_por_id(material_id)
        if material:
            self.title_label.setText(f"Detalhes: {material['titulo']}")
            
            self.details_layout.addWidget(QLabel(f"<b>Autor:</b> {material['autor']}"), 0, 0)
            self.details_layout.addWidget(QLabel(f"<b>Ano:</b> {material['ano']}"), 1, 0)
            self.details_layout.addWidget(QLabel(f"<b>Categoria:</b> {material['categoria']}"), 2, 0)
            
            # Limpar lista de resenhas anterior e carregar novas
            self.reviews_list.clear()
            reviews = self.biblioteca.listar_resenhas_material(material_id)
            if reviews:
                for review in reviews:
                    item_text = f"Por {review['nome']}: '{review['texto_resenha']}'"
                    self.reviews_list.addItem(QListWidgetItem(item_text))

class RecommendationScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        title_label = QLabel("Recomendações para você")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Título", "Autor", "Categoria"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(f"background-color: white; selection-background-color: {SECONDARY_LIGHT}; border: 1px solid #CCCCCC;")
        main_layout.addWidget(self.table)
        
        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.MAIN_MENU_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)

    def refresh_recommendations(self):
        self.table.setRowCount(0)
        recommendations = self.biblioteca.recomendar_por_genero(self.main_app.usuario_logado_id)
        if recommendations:
            self.table.setRowCount(len(recommendations))
            for i, rec in enumerate(recommendations):
                self.table.setItem(i, 0, QTableWidgetItem(str(rec['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(rec['titulo']))
                self.table.setItem(i, 2, QTableWidgetItem(rec['autor']))
                self.table.setItem(i, 3, QTableWidgetItem(rec['categoria']))
        else:
            QMessageBox.information(self, "Aviso", "Nenhuma recomendação disponível no momento.")


class UserProfileScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        title_label = QLabel("Meu perfil")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Informações do Usuário
        user_info_box = QGroupBox("Informações pessoais")
        user_info_box.setFont(QFont("Montserrat", 12, QFont.Bold))
        user_info_box.setStyleSheet(f"background-color: transparent; color: {TEXT_COLOR};")
        user_info_layout = QGridLayout()
        self.user_name_label = QLabel("Nome: ")
        self.user_email_label = QLabel("Email: ")
        user_info_layout.addWidget(self.user_name_label, 0, 0)
        user_info_layout.addWidget(self.user_email_label, 1, 0)
        user_info_box.setLayout(user_info_layout)
        main_layout.addWidget(user_info_box)

        # Meus Empréstimos
        borrowed_box = QGroupBox("Meus empréstimos")
        borrowed_box.setFont(QFont("Montserrat", 12, QFont.Bold))
        borrowed_box.setStyleSheet(f"background-color: transparent; color: {TEXT_COLOR};")
        self.borrowed_list = QListWidget()
        self.borrowed_list.setStyleSheet("background-color: white; border-radius: 8px;")
        borrowed_layout = QVBoxLayout()
        borrowed_layout.addWidget(self.borrowed_list)
        borrowed_box.setLayout(borrowed_layout)
        main_layout.addWidget(borrowed_box)

        # Resenhas
        reviews_box = QGroupBox("Minhas resenhas")
        reviews_box.setFont(QFont("Montserrat", 12, QFont.Bold))
        reviews_box.setStyleSheet(f"background-color: transparent; color: {TEXT_COLOR};")
        self.reviews_list = QListWidget()
        self.reviews_list.setStyleSheet("background-color: white; border-radius: 8px;")
        reviews_layout = QVBoxLayout()
        reviews_layout.addWidget(self.reviews_list)

        self.remove_review_button = QPushButton("Remover Resenha")
        self.remove_review_button.setStyleSheet(f"background-color: {ERROR_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        self.remove_review_button.clicked.connect(self.remove_review)
        reviews_layout.addWidget(self.remove_review_button)
        
        reviews_box.setLayout(reviews_layout)
        main_layout.addWidget(reviews_box)

        # Botão Voltar
        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.MAIN_MENU_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
    
    def refresh_profile(self):
        user_id = self.main_app.usuario_logado_id
        if user_id:
            user_info = self.biblioteca.buscar_usuario(user_id)
            if user_info:
                self.user_name_label.setText(f"Nome: {user_info['nome']}")
                self.user_email_label.setText(f"Email: {user_info['email']}")
            
            # Atualiza a lista de empréstimos
            self.borrowed_list.clear()
            borrowed_items = self.biblioteca.listar_emprestimos_usuario(user_id)
            if borrowed_items:
                for item in borrowed_items:
                    item_text = f"Título: {item['titulo']}\nDevolução prevista: {item['data_devolucao_prevista']}"
                    self.borrowed_list.addItem(QListWidgetItem(item_text))

            # Atualiza a lista de resenhas
            self.reviews_list.clear()
            reviews = self.biblioteca.listar_resenhas_usuario(user_id)
            if reviews:
                for review in reviews:
                    item_text = f"Título: {review['titulo']}\nResenha: {review['texto_resenha']}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, review['material_id'])
                    self.reviews_list.addItem(item)
    
    def remove_review(self):
        selected_item = self.reviews_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Aviso", "Selecione uma resenha para remover.")
            return

        reply = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja remover esta resenha?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            material_id = selected_item.data(Qt.UserRole)
            user_id = self.main_app.usuario_logado_id
            
            if self.biblioteca.remover_resenha(user_id, material_id):
                QMessageBox.information(self, "Sucesso", "Resenha removida com sucesso!")
                self.refresh_profile()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover a resenha.")


class DebugScreen(QWidget):
    def __init__(self, main_app, biblioteca_manager):
        super().__init__()
        self.main_app = main_app
        self.biblioteca = biblioteca_manager
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        title_label = QLabel("Debug de usuários")
        title_label.setFont(QFont("Montserrat", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {TITLE_COLOR}; background-color: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(f"background-color: white; selection-background-color: {SECONDARY_LIGHT}; border: 1px solid #CCCCCC;")
        main_layout.addWidget(self.table)
        
        update_layout = QHBoxLayout()
        self.update_name_input = QLineEdit()
        self.update_name_input.setPlaceholderText("Novo nome para o usuário selecionado...")
        self.update_name_input.setStyleSheet("background-color: white; border: 1px solid #D1D1D1; border-radius: 8px; padding: 8px;")
        
        update_button = QPushButton("Atualizar nome")
        update_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        update_button.clicked.connect(self.update_user_name)
        
        update_layout.addWidget(self.update_name_input)
        update_layout.addWidget(update_button)
        main_layout.addLayout(update_layout)
        
        action_layout = QHBoxLayout()
        refresh_button = QPushButton("Atualizar lista")
        refresh_button.setStyleSheet(f"background-color: {BUTTON_BG_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        refresh_button.clicked.connect(self.refresh_users)

        remove_button = QPushButton("Remover selecionado")
        remove_button.setStyleSheet(f"background-color: {ERROR_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 12px; padding: 8px;")
        remove_button.clicked.connect(self.remove_user)

        action_layout.addWidget(refresh_button)
        action_layout.addWidget(remove_button)
        main_layout.addLayout(action_layout)
        
        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {BUTTON_TEXT_COLOR}; border-radius: 20px; padding: 12px;")
        back_button.clicked.connect(partial(self.main_app.switch_to_screen, self.main_app.LOGIN_INDEX))
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)

    def refresh_users(self):
        self.table.setRowCount(0)
        users = self.biblioteca.listar_usuarios()
        if users:
            self.table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(user['nome']))
                self.table.setItem(i, 2, QTableWidgetItem(user['email']))

    def update_user_name(self):
        selected_rows = self.table.selectionModel().selectedRows()
        new_name = self.update_name_input.text()

        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário na tabela para atualizar.")
            return

        if not new_name:
            QMessageBox.warning(self, "Aviso", "Digite o novo nome no campo de texto.")
            return

        row = selected_rows[0].row()
        user_id = int(self.table.item(row, 0).text())

        if self.biblioteca.atualizar_nome_usuario(user_id, new_name):
            QMessageBox.information(self, "Sucesso", "Nome do usuário atualizado com sucesso!")
            self.update_name_input.clear()
            self.refresh_users()
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível atualizar o nome do usuário.")

    def remove_user(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário para remover.")
            return

        reply = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja remover o usuário selecionado?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            row = selected_rows[0].row()
            user_id = int(self.table.item(row, 0).text())
            if self.biblioteca.remover_usuario(user_id):
                QMessageBox.information(self, "Sucesso", "Usuário removido com sucesso!")
                self.refresh_users()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover o usuário.")

class AppBiblioteca(QWidget):
    # Índices das telas para navegação
    LOGIN_INDEX = 0
    REGISTER_INDEX = 1
    MAIN_MENU_INDEX = 2
    ADD_MATERIAL_INDEX = 3
    ACERVO_INDEX = 4
    DEBUG_INDEX = 5
    RECOMMENDATION_INDEX = 6
    PROFILE_INDEX = 7
    RESET_PASSWORD_INDEX = 8
    MATERIAL_DETAILS_INDEX = 9

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Biblioteca")
        self.setGeometry(100, 100, 1200, 900)
        
        self.biblioteca = Biblioteca(db_name=DB_NAME)
        self.usuario_logado_id = None
        
        main_layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        
        self.login_screen = LoginScreen(self, self.biblioteca)
        self.register_screen = RegisterScreen(self, self.biblioteca)
        self.main_screen = MainScreen(self)
        self.add_material_screen = AddMaterialScreen(self, self.biblioteca)
        self.acervo_screen = AcervoScreen(self, self.biblioteca)
        self.debug_screen = DebugScreen(self, self.biblioteca)
        self.recommendation_screen = RecommendationScreen(self, self.biblioteca)
        self.user_profile_screen = UserProfileScreen(self, self.biblioteca)
        self.reset_password_screen = ResetPasswordScreen(self, self.biblioteca)
        self.material_details_screen = MaterialDetailsScreen(self, self.biblioteca)

        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.register_screen)
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.add_material_screen)
        self.stacked_widget.addWidget(self.acervo_screen)
        self.stacked_widget.addWidget(self.debug_screen)
        self.stacked_widget.addWidget(self.recommendation_screen)
        self.stacked_widget.addWidget(self.user_profile_screen)
        self.stacked_widget.addWidget(self.reset_password_screen)
        self.stacked_widget.addWidget(self.material_details_screen)
        
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def switch_to_screen(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == self.ACERVO_INDEX:
            self.acervo_screen.refresh_acervo()
        elif index == self.DEBUG_INDEX:
            self.debug_screen.refresh_users()
        elif index == self.RECOMMENDATION_INDEX:
            self.recommendation_screen.refresh_recommendations()
        elif index == self.PROFILE_INDEX:
            self.user_profile_screen.refresh_profile()
    
    def logout(self):
        self.usuario_logado_id = None
        QMessageBox.information(self, "Logout", "Você foi desconectado.")
        self.switch_to_screen(self.LOGIN_INDEX)

if __name__ == "__main__":
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Banco de dados '{DB_NAME}' limpo.")

    criar_tabelas() 
    
    app = QApplication(sys.argv)
    main_window = AppBiblioteca()
    main_window.show()
    sys.exit(app.exec_())