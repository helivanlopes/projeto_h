# Plano de Testes Automatizados - LordCRM (TDD First)

Este documento descreve a estratégia de testes para o LordCRM, focando na metodologia TDD (Test-Driven Development) para garantir a integridade das funcionalidades críticas e evitar regressões.

## 1. Estratégia de Teste
A estratégia baseia-se na pirâmide de testes, priorizando testes unitários e de integração que validam o comportamento do sistema conforme as especificações de negócio (RBAC e ciclo de vida de tickets).

- **Framework**: `pytest`
- **Ferramentas Adicionais**: `pytest-flask`, `pytest-sqlalchemy`, `coverage`, `playwright`.
- **Banco de Dados de Teste**: SQLite em memória (`:memory:`) para unitários; Banco dedicado para E2E.

## 2. Dependências de Teste (Adicionadas ao requirements.txt)
- `pytest`: Executor de testes.
- `pytest-flask`: Integração com Flask para testes de rotas.
- `coverage`: Medição de cobertura de código.
- `pytest-playwright`: Testes de interface e fluxo completo (E2E).

## 3. Matriz de Testes por Funcionalidade

### 3.1. Autenticação e Registro
| ID | Cenário | Prioridade | Descrição |
|---|---|---|---|
| AUTH-01 | Registro de Cliente | Crítica | Validar se um novo cliente pode se registrar com sucesso. |
| AUTH-02 | Login de Usuário | Crítica | Validar acesso com credenciais válidas. |
| AUTH-03 | Login Inválido | Alta | Garantir que credenciais incorretas não permitam acesso. |

### 3.2. Controle de Acesso (RBAC)
| ID | Cenário | Prioridade | Descrição |
|---|---|---|---|
| RBAC-01 | Acesso Restrito Admin | Crítica | Tentar acessar `/admin/equipe` com papel 'cliente' (deve negar). |
| RBAC-02 | Acesso Painel Atendente | Alta | Validar que apenas 'atendente' acessa a fila de tickets. |

### 3.3. Ciclo de Vida do Ticket
| ID | Cenário | Prioridade | Descrição |
|---|---|---|---|
| TKT-01 | Abertura de Ticket | Crítica | Cliente deve conseguir abrir um novo ticket. |
| TKT-02 | Assumir Ticket | Crítica | Atendente assume um ticket aberto; status muda para 'em_andamento'. |
| TKT-03 | Ticket Indisponível | Alta | Impedir que um atendente assuma um ticket já em andamento. |

### 3.4. Gestão de Equipe (Admin)
| ID | Cenário | Prioridade | Descrição |
|---|---|---|---|
| ADM-01 | Cadastro de Gestor | Alta | Admin cadastra um novo usuário com papel 'gestor'. |

### 3.5. Testes de Interface (E2E)
| ID | Cenário | Prioridade | Descrição |
|---|---|---|---|
| E2E-01 | Fluxo Completo Chamado | Crítica | Cliente abre ticket -> Atendente assume -> Status reflete no Painel. |
| E2E-02 | Navegação por Perfil | Alta | Validar visibilidade de itens de menu baseada no papel logado. |

## 4. Implementação TDD (Exemplo de Suíte)

### Teste de Regressão (Ticket Lifecycle)
```python
def test_atendente_assume_ticket(client, auth, db_session):
    # Setup: Criar cliente e ticket
    auth.register(email='c@t.com', role='cliente')
    ticket = Ticket(titulo='Erro', descricao='Fogo', cliente_id=1)
    db_session.add(ticket)
    db_session.commit()
    
    # Action: Login como atendente e assumir
    auth.login(email='atendente@lord.com')
    response = client.post(f'/ticket/{ticket.id}/assumir', follow_redirects=True)
    
    # Assert
    assert ticket.status == 'em_andamento'
    assert b'Voc\xc3\xaa assumiu o ticket' in response.data
```

## 5. Procedimento de Execução
1. Instalar dependências: `pip install -r requirements.txt`.
2. Rodar testes unitários: `pytest tests/unit`.
3. Rodar testes E2E: `pytest tests/e2e`.
4. Gerar cobertura: `coverage run -m pytest && coverage report`.
