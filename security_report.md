# Relatório de Inspeção de Segurança - LordCRM

**Data da Inspeção:** 24/05/2026
**Nível de Profundidade:** PROFUNDA
**Alvo:** Código-fonte `projeto_h`

---

## 1. Resumo Executivo

Esta inspeção avaliou o projeto LordCRM com base no OWASP Top 10 e práticas de desenvolvimento seguro. O sistema apresenta vulnerabilidades críticas que permitem a exploração direta, comprometendo a integridade, confidencialidade e disponibilidade dos dados.

### Contagem de Achados por Severidade

| Severidade | Quantidade |
| :--- | :--- |
| Crítica | 2 |
| Alta | 2 |
| Média | 1 |
| Baixa | 0 |
| **Total** | **5** |

### Top 5 Ações Mais Urgentes
1.  Desabilitar `FLASK_DEBUG` no ambiente de produção.
2.  Remover credenciais padrão (Admin/Owner) do código-fonte.
3.  Implementar cabeçalhos de segurança HTTP (CSP, X-Content-Type-Options, etc.).
4.  Fixar (pinning) versões das dependências no `requirements.txt`.
5.  Configurar uma `SECRET_KEY` forte e gerida via ambiente.

---

## 2. Detalhamento das Vulnerabilidades

### 2.1. Debug Mode Ativo em Produção (A02:2021)
*   **Localização:** `docker-compose.yml`, linha 8.
*   **Descrição:** O sistema está configurado com `FLASK_DEBUG=1`. Isso ativa o modo de depuração do Flask, que expõe o código-fonte através de stack traces interativos e permite a execução de código arbitrário no contexto da aplicação caso um erro ocorra.
*   **Evidência:** `FLASK_DEBUG=1`
*   **Impacto:** Execução remota de código (RCE) e exposição de informações sensíveis do sistema.
*   **Severidade:** **Crítica**
*   **Recomendação:** Remover ou alterar para `FLASK_DEBUG=0` em todos os ambientes que não sejam de desenvolvimento local.
*   **Referências:** [OWASP A02:2021](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/), [CWE-489](https://cwe.mitre.org/data/definitions/489.html)

### 2.2. Credenciais Padrão Hardcoded (A07:2021)
*   **Localização:** `app/__init__.py`, linhas 54-79.
*   **Descrição:** O sistema realiza o seed de usuários Admin e Owner utilizando credenciais padrão (`admin123`, `owner123`) caso não estejam definidas no `.env`. Isso é uma falha grave de segurança que facilita o acesso não autorizado.
*   **Evidência:** `admin.set_password(os.getenv('ADMIN_DEFAULT_PASSWORD', 'admin123'))`
*   **Impacto:** Acesso privilegiado imediato por atacantes que conheçam as credenciais padrão.
*   **Severidade:** **Crítica**
*   **Recomendação:** Remover valores padrão no código. O sistema deve falhar ao iniciar caso as variáveis de ambiente necessárias não estejam configuradas.
*   **Referências:** [OWASP A07:2021](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/), [CWE-798](https://cwe.mitre.org/data/definitions/798.html)

### 2.3. Segredo de Sessão Inseguro (A04:2021)
*   **Localização:** `app/__init__.py`, linha 22.
*   **Descrição:** A `SECRET_KEY` do Flask possui um valor padrão (`'dev-key'`) caso a variável de ambiente não esteja configurada.
*   **Evidência:** `app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')`
*   **Impacto:** Permite que atacantes forjem tokens de sessão, resultando em sequestro de conta (account takeover).
*   **Severidade:** **Alta**
*   **Recomendação:** Remover o valor padrão. Garantir que o sistema só inicie se uma `SECRET_KEY` complexa e aleatória estiver definida.

### 2.4. Dependências Não Fixadas (A03:2021)
*   **Localização:** `requirements.txt`.
*   **Descrição:** As dependências são listadas apenas pelo nome (ex: `Flask`), sem definição de versão. Isso permite que atualizações automáticas ou builds futuros instalem versões vulneráveis ou maliciosas das bibliotecas.
*   **Evidência:** `Flask` (em vez de `Flask==3.1.3`)
*   **Impacto:** Comprometimento da cadeia de suprimentos de software (Software Supply Chain Poisoning).
*   **Severidade:** **Alta**
*   **Recomendação:** Fixar as versões de todas as dependências no `requirements.txt` utilizando o formato `pacote==versao`.
*   **Referências:** [OWASP A03:2021](https://owasp.org/Top10/A03_2021-Injection/), [CWE-1395](https://cwe.mitre.org/data/definitions/1395.html)

### 2.5. Falta de Cabeçalhos de Segurança HTTP (A02:2021)
*   **Localização:** Aplicação como um todo (configuração).
*   **Descrição:** A aplicação não envia cabeçalhos de segurança básicos (CSP, X-Frame-Options, X-Content-Type-Options) que protegem contra XSS e Clickjacking.
*   **Impacto:** Aumenta a probabilidade de ataques XSS (Cross-Site Scripting) e Clickjacking.
*   **Severidade:** **Média**
*   **Recomendação:** Utilizar extensões como `Flask-Talisman` para configurar cabeçalhos de segurança automaticamente.
*   **Exemplo:**
  ```python
  from flask_talisman import Talisman
  Talisman(app)
  ```
*   **Referências:** [OWASP A05:2021](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
