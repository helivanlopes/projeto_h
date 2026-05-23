# LordCRM - Sistema de Gerenciamento de Chamados

Este é o ambiente de desenvolvimento do LordCRM, um sistema de CRM focado em atendimento via tickets.

## 🚀 Como Iniciar

### Pré-requisitos
- Docker e Docker Compose instalados.

### Passos para Rodar (Docker Compose)
1. Certifique-se de que o arquivo `.env` existe na raiz.
2. Execute:
   ```bash
   docker-compose up --build
   ```

### Passos para Rodar (Docker Nativo - Fallback)
Caso o `docker-compose` não esteja instalado:
1. Construa a imagem:
   ```bash
   docker build -t lordcrm .
   ```
2. Inicie o container:
   ```bash
   docker run -d -p 5000:5000 --env-file .env -v $(pwd):/app -e FLASK_DEBUG=1 --name lordcrm_dev lordcrm
   ```
   *(Substitua `$(pwd)` pelo caminho absoluto se necessário)*

4. Acesse a aplicação em: [http://localhost:5000](http://localhost:5000)

## 👤 Credenciais Padrão (Administrador)
- **Email:** `admin@lordcrm.com`
- **Senha:** `admin123`

## 🛠️ Desenvolvimento
- **Hot-Reload:** O ambiente está configurado para reiniciar automaticamente ao detectar mudanças no código (`app/`).
- **Banco de Dados:** Utiliza SQLite localizado em `instance/lordcrm.db`. Este volume é persistente.
- **Modo Debug:** Ativado por padrão no Docker Compose (`FLASK_DEBUG=1`).

## 📋 Comandos Úteis
- **Ver Logs:** `docker-compose logs -f`
- **Parar Ambiente:** `docker-compose down`
- **Rodar Testes (dentro do container):**
  ```bash
  docker-compose exec web python -m unittest discover tests
  ```

---
*Desenvolvido seguindo as especificações do LordCRM Spec.*
