# Template de Relatório de Auditoria

Use este template na **Fase 2** para gerar o relatório de auditoria.
Preencha cada campo com os dados reais encontrados no projeto analisado.

---

## Regras de preenchimento

- **Ordenação:** findings sempre ordenados CRITICAL → HIGH → MEDIUM → LOW
- **Arquivo e linhas:** sempre com caminho relativo ao raiz do projeto e intervalo de linhas exato
- **Descrição:** objetiva, sem jargão — descrever o que foi encontrado, não o que deveria ser
- **Impact:** consequência concreta e realista (não hipotética)
- **Recommendation:** ação específica e acionável
- **Confirmação obrigatória:** ao final do relatório, pausar e aguardar resposta `[y/n]` do usuário antes de qualquer modificação de arquivo

---

## Template

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <lista das principais dependências>
Domain:        <domínio inferido> (<entidades principais>)
Architecture:  <Monolítica / Layered / MVC> — <descrição em 1 linha>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas ou entidades>
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-diretório-do-projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<total de linhas> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [CRITICAL] <Nome do Anti-Pattern>
File: <caminho/arquivo.py>:<linha-início>-<linha-fim>
Description: <o que foi encontrado, objetivo e direto>
Impact: <consequência concreta se não corrigido>
Recommendation: <ação específica de correção>

### [CRITICAL] <Nome do Anti-Pattern>
File: <caminho/arquivo.py>:<linha>
Description: <...>
Impact: <...>
Recommendation: <...>

### [HIGH] <Nome do Anti-Pattern>
File: <caminho/arquivo.py>:<linha-início>-<linha-fim>
Description: <...>
Impact: <...>
Recommendation: <...>

### [MEDIUM] <Nome do Anti-Pattern>
File: <caminho/arquivo.py>:<linha-início>-<linha-fim>
Description: <...>
Impact: <...>
Recommendation: <...>

### [LOW] <Nome do Anti-Pattern>
File: <caminho/arquivo.py>:<linha-início>-<linha-fim>
Description: <...>
Impact: <...>
Recommendation: <...>

================================
Total: <N> findings
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Exemplo preenchido

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação clara de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~600 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] SQL Injection via Concatenação de String
File: models.py:28
Description: Query construída por concatenação direta: "SELECT * FROM produtos WHERE id = " + str(id)
Impact: Qualquer parâmetro da rota pode ser usado para extrair ou destruir dados do banco.
Recommendation: Substituir por query parametrizada: cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

### [CRITICAL] Credenciais Hardcoded
File: app.py:7
Description: SECRET_KEY definido como literal "minha-chave-super-secreta-123" no código-fonte.
Impact: Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão.
Recommendation: Mover para variável de ambiente: os.getenv("SECRET_KEY")

### [CRITICAL] Senha Armazenada em Texto Puro
File: models.py:127-128
Description: INSERT de usuário armazena senha sem hash: VALUES ('" + nome + "', '" + senha + "')
Impact: Banco comprometido expõe senhas reais de todos os usuários.
Recommendation: Aplicar hashlib.sha256 com salt antes de persistir.

### [HIGH] Debug Mode em Produção
File: app.py:8 e app.py:88
Description: app.config["DEBUG"] = True e app.run(host="0.0.0.0", debug=True)
Impact: Debugger interativo exposto na rede — permite execução arbitrária de código remoto.
Recommendation: Ler de os.getenv("DEBUG", "false") e nunca usar host="0.0.0.0" em produção.

### [HIGH] God Module — models.py
File: models.py:1-350
Description: Arquivo único contém queries SQL, lógica de negócio e validação para 4 domínios diferentes.
Impact: Impossível testar qualquer domínio em isolamento. Qualquer mudança afeta todos.
Recommendation: Separar em models/produto_model.py, models/usuario_model.py, etc.

### [MEDIUM] N+1 Query em get_todos_pedidos
File: models.py:203-233
Description: Para cada pedido retornado, executa query separada para buscar itens do pedido.
Impact: Com 500 pedidos, são 501 queries ao banco onde poderia ser 1 JOIN.
Recommendation: Substituir por JOIN: SELECT pedidos.*, itens_pedido.* FROM pedidos JOIN itens_pedido ON ...

### [MEDIUM] Dados Sensíveis na Resposta da API
File: controllers.py:289-290
Description: Endpoint /health retorna SECRET_KEY e caminho do banco no JSON de resposta.
Impact: Qualquer cliente (ou log de proxy) tem acesso à chave secreta da aplicação.
Recommendation: Remover campos sensíveis da resposta. Health check deve retornar apenas status.

### [LOW] Bare Except sem Log
File: controllers.py:60
Description: except Exception as e: sem log estruturado — apenas print(e).
Impact: Erros reais são engolidos e impossíveis de rastrear em produção.
Recommendation: Usar logging.error(e, exc_info=True) e retornar erro HTTP estruturado.

================================
Total: 8 findings
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 1
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Instruções para salvar o relatório

Após gerar o relatório, salvar o conteúdo em:
- Projeto 1: `reports/audit-project-1.md` (raiz do repositório)
- Projeto 2: `reports/audit-project-2.md`
- Projeto 3: `reports/audit-project-3.md`

Só avançar para a Fase 3 após confirmação explícita `y` do usuário.
