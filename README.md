# IronStats Brasil 🏊🚴🏃

Análise completa de resultados de Ironman 70.3 no Brasil.

**Site ao vivo:** https://SEU-USUARIO.github.io/ironstats

## Como adicionar uma nova prova

### 1. Baixar o CSV do Coach Cox
- Acesse [coachcox.co.uk/imstats/him/](https://www.coachcox.co.uk/imstats/him/)
- Clique na aba "S. America" e encontre a prova
- Na página de resultados, espere a tabela carregar e clique no botão de download CSV

### 2. Nomear o arquivo
O nome DEVE seguir o padrão: `ironman703{cidade}{ano}-results.csv`

Exemplos:
- `ironman703florianopolis2024-results.csv`
- `ironman703brasilia2025-results.csv`
- `ironman703buenosaires2025-results.csv`

### 3. Configurar a prova (só na primeira vez de cada cidade)
Edite o arquivo `races.json` e adicione a nova cidade seguindo o modelo existente (percurso, clima, etc.)

### 4. Upload no GitHub
- Vá na pasta `data/` do repositório no GitHub
- Clique em "Add file" → "Upload files"
- Arraste o CSV
- Clique em "Commit changes"

O site atualiza automaticamente em ~2 minutos.

## Estrutura do projeto

```
ironstats/
├── data/                  ← CSVs do Coach Cox aqui
├── races.json             ← Configuração de provas (clima, percurso)
├── template.html          ← Template do site
├── build.py               ← Script que gera o site
├── docs/index.html        ← Site gerado (não editar)
└── .github/workflows/     ← Deploy automático
```

## Cidades configuradas

| Chave no nome do arquivo | Cidade |
|---|---|
| `sopaulo` | São Paulo |
| `riodejaneiro` | Rio de Janeiro |

Para adicionar uma nova cidade, edite `races.json`.

## Rodar localmente

```bash
python3 build.py
# Abra docs/index.html no navegador
```
