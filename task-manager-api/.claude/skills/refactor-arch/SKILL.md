---
name: refactor-arch
description: Analyzes a codebase, audits architectural anti-patterns, and refactors the project to MVC. Use when the user invokes /refactor-arch or wants to audit and refactor a legacy project (Python/Flask or Node.js/Express) to MVC architecture.
---

# refactor-arch

Executa 3 fases sequenciais: análise da stack, auditoria de anti-patterns e refatoração para MVC.
Agnóstica de tecnologia — funciona com Python/Flask e Node.js/Express.
Pode ser copiada para qualquer projeto e executada com `/refactor-arch`.

---

## Fase 1 — Análise do Projeto

> Leia agora: [01-project-analysis.md](01-project-analysis.md)

1. Detecte o nome do projeto atual pelo nome do diretório de trabalho (`basename $PWD`)
2. Explore todos os arquivos do diretório atual:
   ```bash
   find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) \
     -not -path "*/node_modules/*" \
     -not -path "*/__pycache__/*" \
     -not -path "*/.git/*"
   ```
3. Aplique as heurísticas de [01-project-analysis.md](01-project-analysis.md) para detectar:
   - Linguagem e framework (com versão)
   - Banco de dados e ORM
   - Domínio da aplicação (via nomes de tabelas e rotas)
   - Arquitetura atual (Monolítica / Layered / MVC)
   - Número de arquivos fonte e entry point
4. Imprima o resumo no formato exato definido em [01-project-analysis.md](01-project-analysis.md#7-output-esperado-fase-1)

---

## Fase 2 — Auditoria de Anti-Patterns

> Leia agora: [02-antipatterns-catalog.md](02-antipatterns-catalog.md) e [03-audit-report-template.md](03-audit-report-template.md)

1. Leia o conteúdo de cada arquivo fonte do projeto
2. Cruze o código contra **cada anti-pattern** do catálogo em [02-antipatterns-catalog.md](02-antipatterns-catalog.md)
3. Para cada ocorrência encontrada, registre:
   - Severidade (CRITICAL / HIGH / MEDIUM / LOW)
   - Arquivo e linhas exatas
   - Descrição objetiva do que foi encontrado
   - Impacto concreto
   - Recomendação específica
4. Gere o relatório completo seguindo o template de [03-audit-report-template.md](03-audit-report-template.md):
   - Ordene os findings: CRITICAL → HIGH → MEDIUM → LOW
   - Mínimo de 5 findings obrigatórios
5. Salve o relatório em `reports/audit-report.md` dentro do projeto atual (crie o diretório se não existir)
6. **PARE. Exiba o relatório completo e aguarde confirmação do usuário:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Só avance para a Fase 3 se o usuário responder `y`. Se responder `n`, encerre e informe o caminho do relatório salvo.

---

## Fase 3 — Refatoração para MVC

> Leia agora: [04-mvc-guidelines.md](04-mvc-guidelines.md) e [05-refactoring-playbook.md](05-refactoring-playbook.md)

1. Aplique as transformações do [05-refactoring-playbook.md](05-refactoring-playbook.md) para cada finding da Fase 2
2. Siga a estrutura de diretórios e responsabilidades de [04-mvc-guidelines.md](04-mvc-guidelines.md)
3. Ordem de execução:
   - Criar `config/settings.py` (ou `config/settings.js`) com variáveis de ambiente
   - Criar `models/` com um arquivo por entidade de domínio
   - Criar `controllers/` com um arquivo por domínio
   - Criar `routes/` com mapeamento limpo URL → controller
   - Criar `middlewares/error_handler.py` (ou `.js`) com handler centralizado
   - Atualizar entry point (`app.py` / `app.js`) como composition root limpo
4. Após refatorar, valide:
   - **Boot:** execute o entry point e confirme que a aplicação inicia sem erros
     - Python: `python app.py`
     - Node.js: `node src/app.js`
   - **Endpoints:** teste os endpoints principais com os mesmos parâmetros de antes e confirme que respondem corretamente
5. Imprima o resumo final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework>

## New Project Structure
[árvore de diretórios do projeto refatorado]

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining

## Report saved at
  reports/audit-report.md
================================
```
