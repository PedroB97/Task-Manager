# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from wtforms_sqlalchemy.fields import QuerySelectField # Importar QuerySelectField

# Importar User para validações e QuerySelectField
from .models.models import User

# Função para obter a lista de usuários para o QuerySelectField
def user_query():
    return User.query

class RegistrationForm(FlaskForm):
    username = StringField("Nome de Usuário",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmar Senha",
                                     validators=[DataRequired(), EqualTo("password", message="As senhas devem ser iguais.")])
    submit = SubmitField("Registrar")

    # Validações customizadas
    def validate_username(self, username):
         user = User.query.filter_by(username=username.data).first()
         if user:
             raise ValidationError("Este nome de usuário já está em uso. Escolha outro.")

    def validate_email(self, email):
         user = User.query.filter_by(email=email.data).first()
         if user:
             raise ValidationError("Este email já está em uso. Escolha outro.")

class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField("Lembrar-me")
    submit = SubmitField("Login")

# Novo Formulário para Tarefas
class TaskForm(FlaskForm):
    title = StringField("Título da Tarefa", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Descrição", validators=[Optional()])
    status = SelectField("Status", choices=[
        ("a_fazer", "A Fazer"),
        ("em_andamento", "Em Andamento"),
        ("finalizada", "Finalizada")
    ], validators=[DataRequired()])
    due_date = DateField("Data de Vencimento", format="%Y-%m-%d", validators=[Optional()])
    # Campo para selecionar o usuário responsável
    assigned_user = QuerySelectField(
        "Atribuir a",
        query_factory=user_query,
        get_label="username",
        allow_blank=True, # Permitir tarefas não atribuídas
        blank_text="-- Não atribuído --",
        validators=[Optional()]
    )
    submit = SubmitField("Salvar Tarefa")

# --- NOVOS FORMULÁRIOS PARA GERENCIAMENTO DE USUÁRIOS ---

class UserForm(FlaskForm):
    username = StringField("Nome de Usuário",
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    is_admin = BooleanField("Administrador") # Campo para definir se é admin
    submit = SubmitField("Salvar Usuário")

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user:
                raise ValidationError("Este nome de usuário já está em uso. Escolha outro.")

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                raise ValidationError("Este email já está em uso. Escolha outro.")

class CreateUserForm(UserForm):
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmar Senha",
                                     validators=[DataRequired(), EqualTo("password", message="As senhas devem ser iguais.")])
    submit = SubmitField("Criar Usuário")

class UpdateUserPasswordForm(FlaskForm):
    password = PasswordField("Nova Senha", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmar Nova Senha",
                                     validators=[DataRequired(), EqualTo("password", message="As senhas devem ser iguais.")])
    submit = SubmitField("Alterar Senha")
