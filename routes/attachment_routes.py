from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from models.models import Task, Attachment
from __init__ import db
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
        return redirect(request.referrer or url_for('task_bp.view_task', task_id=task_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(request.referrer or url_for('task_bp.view_task', task_id=task_id))
    
    if file and allowed_file(file.filename):
        # Gerar nome único para o arquivo
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Salvar arquivo
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Criar registro no banco
        attachment = Attachment(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type or 'application/octet-stream',
            task_id=task_id,
            uploaded_by_id=1  # TODO: usar current_user.id quando login estiver implementado
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        flash(f'Arquivo "{original_filename}" enviado com sucesso!', 'success')
    else:
        flash('Tipo de arquivo não permitido', 'error')
    
    return redirect(request.referrer or url_for('task_bp.view_task', task_id=task_id))

@attachment_bp.route('/attachments/<int:attachment_id>/download')
def download_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    
    try:
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.original_filename
        )
    except FileNotFoundError:
        flash('Arquivo não encontrado', 'error')
        return redirect(request.referrer or url_for('project_bp.list_projects'))

@attachment_bp.route('/attachments/<int:attachment_id>/delete', methods=['POST'])
def delete_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    task_id = attachment.task_id
    
    # Deletar arquivo físico
    try:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    except OSError:
        pass  # Arquivo já foi deletado ou não existe
    
    # Deletar registro do banco
    db.session.delete(attachment)
    db.session.commit()
    
    flash('Anexo deletado com sucesso!', 'success')
    return redirect(request.referrer or url_for('task_bp.view_task', task_id=task_id))

