# 🔐 File Crypto - Gerenciador de Arquivos Criptografados

Uma aplicação web moderna para criptografia, gerenciamento e visualização de arquivos com segurança de nível empresarial.

## ✨ Características

- **Criptografia AES-256-GCM**: Algoritmo de criptografia de nível militar
- **Upload em Tempo Real**: Drag-and-drop com feedback visual de progresso
- **Extensões Personalizadas**: Disfarça arquivos com extensões customizadas
- **Categorização Automática**: Organiza arquivos por tipo (áudio, imagem, JSON, criptografado)
- **Visualizadores Integrados**: Preview de imagens, áudio, JSON e texto
- **Interface Moderna**: Design limpo com fonte tecnológica JetBrains Mono
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Gerenciamento Completo**: Upload, download, preview e deleção de arquivos

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Extraia o arquivo ZIP**
   ```bash
   unzip FileCryptoApp.zip
   cd FileCryptoApp
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicie a aplicação**
   ```bash
   python app.py
   ```

4. **Acesse a aplicação**
   - Abra seu navegador e acesse: `http://localhost:5000`
   - A aplicação estará pronta para uso!

## 📁 Estrutura do Projeto

```
FileCryptoApp/
├── app.py                 # Backend Flask principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── uploads/              # Pasta para armazenar arquivos criptografados
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS moderno
│   └── js/
│       └── script.js     # Lógica JavaScript do frontend
└── templates/
    └── index.html        # Página HTML principal
```

## 🔐 Como Funciona

### Processo de Criptografia

1. **Upload do Arquivo**: Selecione ou arraste um arquivo para a área de upload
2. **Criptografia**: O arquivo é criptografado usando AES-256-GCM
3. **Armazenamento**: O arquivo criptografado é salvo na pasta `uploads/`
4. **Extensão Personalizada**: A extensão é alterada para uma extensão customizada
5. **Metadados**: Informações do arquivo são armazenadas para categorização

### Mapeamento de Extensões

| Extensão Original | Extensão Personalizada |
|------------------|----------------------|
| .mp3 | .ad3 |
| .mp4 | .vd4 |
| .png | .ph |
| .jpg | .sz |
| .jpeg | .ssz |
| .json | .jsn |
| .js | .sc |
| .css | .sty |
| .html | .hyp |

## 🎯 Funcionalidades Principais

### 1. Upload de Arquivos
- Drag-and-drop intuitivo
- Validação de tipo e tamanho
- Barra de progresso em tempo real
- Limite de 50MB por arquivo

### 2. Categorização
- **Todos**: Exibe todos os arquivos
- **Criptografados**: Arquivos com extensões personalizadas
- **Áudios**: Arquivos de áudio (MP3, WAV, AAC, FLAC)
- **Imagens**: Arquivos de imagem (PNG, JPG, JPEG, GIF, WEBP, BMP)
- **JSON**: Arquivos JSON

### 3. Visualização
- **Imagens**: Preview inline com zoom
- **Áudio**: Player HTML5 integrado
- **JSON**: Visualizador com formatação
- **Texto**: Visualizador de código com syntax highlighting

### 4. Gerenciamento
- **Preview**: Visualize arquivos descriptografados sem fazer download
- **Download**: Baixe arquivos descriptografados
- **Deletar**: Remova arquivos da aplicação
- **Busca**: Filtre arquivos por categoria

## 🔒 Segurança

- **Criptografia AES-256-GCM**: Padrão de criptografia militar
- **PBKDF2 Key Derivation**: Derivação segura de chaves
- **IV Aleatório**: Vetor de inicialização único para cada arquivo
- **Autenticação de Tag**: Validação de integridade dos dados
- **Armazenamento Seguro**: Arquivos armazenados criptografados no servidor

## 🎨 Design

- **Fonte Tecnológica**: JetBrains Mono para código, Inter para interface
- **Tema Dark**: Reduz fadiga ocular e transmite profissionalismo
- **Gradientes Modernos**: Cores vibrantes com transições suaves
- **Responsivo**: Adapta-se a qualquer tamanho de tela
- **Acessibilidade**: Contraste adequado e navegação intuitiva

## 📊 Especificações Técnicas

- **Backend**: Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Criptografia**: cryptography 41.0.7
- **Servidor**: Werkzeug 3.0.1
- **CORS**: Flask-CORS 4.0.0

## 🐛 Troubleshooting

### Porta 5000 já em uso
```bash
# Use uma porta diferente
python app.py --port 8000
```

### Erro de permissão na pasta uploads
```bash
# Crie a pasta manualmente
mkdir uploads
chmod 755 uploads
```

### Erro ao instalar dependências
```bash
# Atualize pip
pip install --upgrade pip
# Instale novamente
pip install -r requirements.txt
```

## 📝 Notas Importantes

1. **Chave de Criptografia**: A chave é derivada de uma string fixa. Para produção, considere usar uma chave por usuário.
2. **Limite de Arquivo**: O limite padrão é 50MB. Ajuste em `app.py` se necessário.
3. **Pasta de Upload**: Certifique-se de que a pasta `uploads/` tem permissões de escrita.
4. **Backup**: Faça backup regular da pasta `uploads/` para não perder dados.

## 🚀 Próximas Melhorias

- [ ] Autenticação de usuários
- [ ] Chaves de criptografia por usuário
- [ ] Integração com cloud storage (S3, Google Drive)
- [ ] Compartilhamento seguro de arquivos
- [ ] Histórico de versões
- [ ] Compressão de arquivos

## 📄 Licença

Este projeto é fornecido como está, para uso educacional e pessoal.

## 👨‍💻 Desenvolvido por

**Manus AI** - Assistente de IA para desenvolvimento web

---

**Aproveite o File Crypto! 🔐**
