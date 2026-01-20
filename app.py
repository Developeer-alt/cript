#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Crypto - Aplicação de Criptografia e Gerenciamento de Arquivos
Backend Flask com API REST para upload, criptografia AES-256 e persistência
"""

import os
import json
import mimetypes
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets
import base64

# ============================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ============================================

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configurações
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'png', 'jpg', 'jpeg', 'json', 'js', 'css', 'html', 'txt', 'pdf', 'wav', 'aac', 'flac', 'gif', 'webp', 'bmp', 'xml', 'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ============================================
# CONSTANTES E MAPEAMENTOS
# ============================================

# Chave fixa para criptografia AES-256
ENCRYPTION_KEY_STRING = 'FileCryptoSecure2024KeyForAES256BitEncryption'

# Mapeamento de extensões personalizadas → extensões reais
EXTENSION_MAP = {
    'ad3': 'mp3',
    'vd4': 'mp4',
    'ph': 'png',
    'sz': 'jpg',
    'ssz': 'jpeg',
    'jsn': 'json',
    'sc': 'js',
    'sty': 'css',
    'hyp': 'html'
}

# Mapeamento reverso
REVERSE_EXTENSION_MAP = {v: k for k, v in EXTENSION_MAP.items()}

# Categorias de tipos de arquivo
FILE_CATEGORIES = {
    'audio': ['mp3', 'wav', 'aac', 'flac'],
    'image': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'],
    'json': ['json'],
    'encrypted': ['crypt', 'ad3', 'vd4', 'ph', 'sz', 'ssz', 'jsn', 'sc', 'sty', 'hyp'],
    'other': ['txt', 'pdf', 'js', 'css', 'html', 'xml', 'csv']
}

# ============================================
# FUNÇÕES DE CRIPTOGRAFIA
# ============================================

def derive_key(key_string: str, salt: bytes = None) -> tuple:
    """Deriva uma chave AES-256 a partir de uma string usando PBKDF2"""
    if salt is None:
        salt = b'\x00' * 16  # Salt vazio para consistência
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits para AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(key_string.encode())
    return key, salt

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Criptografa dados usando AES-256-GCM"""
    # Gera um IV aleatório de 96 bits (12 bytes) para GCM
    iv = secrets.token_bytes(12)
    
    # Criptografa os dados
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    
    # Combina IV + dados criptografados + tag
    result = iv + encryptor.tag + ciphertext
    return result

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Descriptografa dados usando AES-256-GCM"""
    # Extrai IV (primeiros 12 bytes)
    iv = encrypted_data[:12]
    # Extrai tag de autenticação (próximos 16 bytes)
    tag = encrypted_data[12:28]
    # Dados criptografados (resto)
    ciphertext = encrypted_data[28:]
    
    # Descriptografa os dados
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    return plaintext

# ============================================
# FUNÇÕES UTILITÁRIAS
# ============================================

def get_file_category(filename: str, mime_type: str = None) -> str:
    """Determina a categoria de um arquivo"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # Se é arquivo criptografado
    if ext in EXTENSION_MAP or ext == 'crypt':
        return 'encrypted'
    
    # Verifica por tipo MIME
    if mime_type:
        if mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('image/'):
            return 'image'
        elif 'json' in mime_type:
            return 'json'
    
    # Verifica por extensão
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'other'

def allowed_file(filename: str) -> bool:
    """Verifica se o arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files_metadata() -> list:
    """Retorna metadados de todos os arquivos"""
    files_data = []
    
    if not os.path.exists(UPLOAD_FOLDER):
        return files_data
    
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            
            # Tenta obter o nome original do arquivo
            original_name = filename
            if ext in EXTENSION_MAP:
                original_name = filename.rsplit('.', 1)[0]
            
            files_data.append({
                'id': filename,
                'filename': filename,
                'originalName': original_name,
                'extension': ext,
                'realExtension': EXTENSION_MAP.get(ext, ext),
                'size': stat.st_size,
                'sizeFormatted': format_file_size(stat.st_size),
                'uploadedAt': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'category': get_file_category(filename),
                'mimeType': mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            })
    
    return sorted(files_data, key=lambda x: x['uploadedAt'], reverse=True)

def format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo em formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

# ============================================
# ROTAS - FRONTEND
# ============================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    return send_from_directory(app.static_folder, filename)

# ============================================
# ROTAS - API REST
# ============================================

@app.route('/api/files', methods=['GET'])
def get_files():
    """Retorna lista de arquivos com filtro por categoria"""
    category = request.args.get('category', 'all')
    files = get_files_metadata()
    
    if category != 'all':
        files = [f for f in files if f['category'] == category]
    
    return jsonify({
        'success': True,
        'files': files,
        'total': len(files)
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Faz upload de arquivo e o criptografa"""
    try:
        # Verifica se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nome de arquivo vazio'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido'}), 400
        
        # Lê o conteúdo do arquivo
        file_content = file.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'Arquivo muito grande'}), 400
        
        # Obtém informações do arquivo
        original_filename = secure_filename(file.filename)
        original_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'unknown'
        file_name_without_ext = original_filename.rsplit('.', 1)[0]
        
        # Determina extensão personalizada
        custom_ext = REVERSE_EXTENSION_MAP.get(original_ext, 'crypt')
        
        # Criptografa os dados
        derived_key, _ = derive_key(ENCRYPTION_KEY_STRING)
        encrypted_data = encrypt_data(file_content, derived_key)
        
        # Salva arquivo criptografado
        encrypted_filename = f"{file_name_without_ext}.{custom_ext}"
        encrypted_filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)
        
        # Evita sobrescrita
        counter = 1
        base_name = file_name_without_ext
        while os.path.exists(encrypted_filepath):
            encrypted_filename = f"{base_name}_{counter}.{custom_ext}"
            encrypted_filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)
            counter += 1
        
        with open(encrypted_filepath, 'wb') as f:
            f.write(encrypted_data)
        
        return jsonify({
            'success': True,
            'message': 'Arquivo criptografado e salvo com sucesso',
            'file': {
                'id': encrypted_filename,
                'filename': encrypted_filename,
                'originalName': file_name_without_ext,
                'extension': custom_ext,
                'realExtension': original_ext,
                'size': len(file_content),
                'sizeFormatted': format_file_size(len(file_content)),
                'uploadedAt': datetime.now().isoformat(),
                'category': get_file_category(encrypted_filename),
                'mimeType': file.content_type or 'application/octet-stream'
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/decrypt/<filename>', methods=['GET'])
def decrypt_file(filename):
    """Descriptografa e retorna um arquivo"""
    try:
        secure_name = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, secure_name)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 404
        
        # Lê arquivo criptografado
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
        
        # Descriptografa
        derived_key, _ = derive_key(ENCRYPTION_KEY_STRING)
        decrypted_data = decrypt_data(encrypted_data, derived_key)
        
        # Determina extensão real
        ext = secure_name.rsplit('.', 1)[1].lower() if '.' in secure_name else 'unknown'
        real_ext = EXTENSION_MAP.get(ext, ext)
        original_name = secure_name.rsplit('.', 1)[0]
        
        # Retorna arquivo descriptografado
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype=mimetypes.guess_type(f"file.{real_ext}")[0] or 'application/octet-stream',
            as_attachment=True,
            download_name=f"{original_name}.{real_ext}"
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """Retorna preview de um arquivo descriptografado"""
    try:
        secure_name = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, secure_name)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 404
        
        # Lê arquivo criptografado
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
        
        # Descriptografa
        derived_key, _ = derive_key(ENCRYPTION_KEY_STRING)
        decrypted_data = decrypt_data(encrypted_data, derived_key)
        
        # Determina tipo de arquivo
        ext = secure_name.rsplit('.', 1)[1].lower() if '.' in secure_name else 'unknown'
        real_ext = EXTENSION_MAP.get(ext, ext)
        
        # Para imagens, retorna como base64
        if real_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp']:
            b64_data = base64.b64encode(decrypted_data).decode('utf-8')
            mime_type = mimetypes.guess_type(f"file.{real_ext}")[0] or 'image/png'
            return jsonify({
                'success': True,
                'type': 'image',
                'data': f"data:{mime_type};base64,{b64_data}"
            })
        
        # Para áudio, retorna como base64
        elif real_ext in ['mp3', 'wav', 'aac', 'flac']:
            b64_data = base64.b64encode(decrypted_data).decode('utf-8')
            mime_type = mimetypes.guess_type(f"file.{real_ext}")[0] or 'audio/mpeg'
            return jsonify({
                'success': True,
                'type': 'audio',
                'data': f"data:{mime_type};base64,{b64_data}"
            })
        
        # Para JSON, retorna como texto
        elif real_ext == 'json':
            try:
                json_data = json.loads(decrypted_data.decode('utf-8'))
                return jsonify({
                    'success': True,
                    'type': 'json',
                    'data': json_data
                })
            except:
                return jsonify({
                    'success': True,
                    'type': 'json',
                    'data': decrypted_data.decode('utf-8', errors='ignore')
                })
        
        # Para texto, retorna como string
        elif real_ext in ['txt', 'js', 'css', 'html', 'xml', 'csv']:
            text_data = decrypted_data.decode('utf-8', errors='ignore')
            return jsonify({
                'success': True,
                'type': 'text',
                'data': text_data
            })
        
        else:
            return jsonify({'success': False, 'error': 'Tipo de arquivo não suportado para preview'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Deleta um arquivo"""
    try:
        secure_name = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, secure_name)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Arquivo deletado com sucesso'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# INICIALIZAÇÃO
# ============================================

import io

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 File Crypto - Aplicação de Criptografia de Arquivos")
    print("=" * 60)
    print(f"📁 Pasta de uploads: {UPLOAD_FOLDER}")
    print(f"🔑 Criptografia: AES-256-GCM")
    print(f"🌐 Servidor iniciando em http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
