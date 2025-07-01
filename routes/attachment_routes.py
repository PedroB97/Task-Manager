from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app
from ..models.models import Task, Attachment
from .. import db
from werkzeug.utils import secure_filename
import os
import uuid
import datetime

attachment_bp = Blueprint('attachment_bp', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@attachment_bp.route('/tasks/<int:task_id>/attachments/upload', methods=['POST'])
def upload_attachment(task_id):
    task = Task.query.get_or_404(task_id)

    if 'file' not in request.files:
        flash('Nenhum arquivo enviado', 'error')
        return redirect(url_for('project_bp.view_project', project_id=task.project_id))

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('project_bp.view_project', project_id=task.project_id))

    if file and allowed_file(file.filename):
        # Gerar nome de arquivo seguro e único
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

        # Salvar arquivo
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        # Criar registro de anexo
        attachment = Attachment(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_type=file_extension,
            task_id=task_id
        )

        db.session.add(attachment)
        db.session.commit()

        flash('Arquivo anexado com sucesso!', 'success')
        return redirect(url_for('task_bp.view_task', task_id=task_id))

    flash('Tipo de arquivo não permitido', 'error')
    return redirect(url_for('project_bp.view_project', project_id=task.project_id))

@attachment_bp.route('/attachments/<int:attachment_id>/download')
def download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        attachment.filename,
        download_name=attachment.original_filename,
        as_attachment=True
    )

@attachment_bp.route('/attachments/<int:attachment_id>/delete', methods=['POST'])
def delete_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    task_id = attachment.task_id

    # Remover arquivo físico
    try:
        os.remove(attachment.file_path)
    except OSError:
        pass  # Ignorar erro se o arquivo não existir

    # Remover registro do banco de dados
    db.session.delete(attachment)
    db.session.commit()

    flash('Anexo removido com sucesso!', 'success')
    return redirect(url_for('task_bp.view_task', task_id=task_id))
