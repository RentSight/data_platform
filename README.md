
---

# 📊 Data Platform — RentSight

Este repositório contém a **camada de dados** do projeto **RentSight**, responsável por **ingestão, processamento, validação, modelagem analítica e disponibilização de dados prontos para consumo** por APIs e aplicações externas.

A solução segue a arquitetura **Medallion (Bronze → Silver → Gold)** e foi construída com foco em:

* engenharia de dados
* clareza arquitetural
* reprodutibilidade
* separação de responsabilidades
* prontidão para consumo em produção

---

## 🧠 Visão Geral da Arquitetura

O pipeline é **lake-first** e orientado a produtos analíticos:

* **Spark / Databricks** → processamento e analytics
* **Parquet** → formato intermediário e analítico
* **Banco relacional (Docker)** → camada de serving
* **API** → consumo read-only dos dados Gold

Os notebooks existem para **explicação e validação**, enquanto a execução oficial do pipeline ocorre via **scripts Python**.

---

## 🗂️ Estrutura do Projeto

```
data_platform/
├── data/
│   ├── raw/            # dados brutos (download real ou sample copiado)
│   ├── sample/         # dataset reduzido e versionado (fallback)
│   ├── bronze/         # dados organizados (Parquet)
│   ├── silver/         # dados validados e limpos (Parquet)
│   └── gold/           # produtos analíticos (Parquet)
│
├── scripts/
│   ├── download_data.py     # ingestão com fallback automático para sample
│   ├── run_pipeline.py      # execução Bronze → Silver → Gold
│   ├── quality_checks.py    # métricas de qualidade dos dados
│   └── publish_to_db.py     # carga das tabelas Gold no banco relacional
│
├── databricks/              # notebooks explicativos (READ-ONLY)
│   ├── raw/
│   ├── silver/
│   └── gold/
│
├── sql/                     # contratos SQL (schema, índices, views)
├── docker/                  # infraestrutura do banco (Docker)
├── requirements.txt
└── README.md
```

---

## 📦 Camadas de Dados (Medallion)

### 🥉 Bronze — Dados Brutos Organizados

* Dados ingeridos a partir da fonte original (ou sample fallback)
* Estrutura preservada, sem regras de negócio
* Padronização mínima para permitir processamento
* Persistidos em formato **Parquet**

Esta camada garante **rastreabilidade** e serve como base para todo o pipeline.

---

### 🥈 Silver — Dados Limpos e Confiáveis

* Seleção de colunas relevantes
* Normalização de tipos e formatos
* Tratamento técnico de valores inválidos
* Neutralização consciente de outliers (ex: valores extremos → `NULL`)
* Preservação semântica de valores ausentes

Entrega dados **consistentes, auditáveis e prontos para análise**, sem ainda aplicar métricas finais.

---

### 🥇 Gold — Produtos Analíticos

* Aplicação de regras de negócio
* Criação de métricas, rankings e indicadores
* Agregações por bairro, tipo de imóvel e disponibilidade
* Tabelas orientadas a consumo por APIs e dashboards

A camada Gold representa a **verdade analítica do projeto**.

---

## 📓 Databricks — Notebooks (Read-Only)

O diretório `databricks/` contém notebooks versionados com finalidade **exploratória e documental**:

* Análise exploratória de dados (EDA)
* Justificativa de decisões de limpeza
* Validação dos resultados da camada Gold

> ⚠️ Os notebooks **não são utilizados para executar o pipeline oficial**.
> A execução determinística ocorre exclusivamente via scripts Python.

---

## 🔄 Scripts — Pipeline Executável

### `download_data.py`

* Realiza o download do dataset original
* Em caso de falha (rede, indisponibilidade), utiliza automaticamente o **dataset sample**
* Garante que o pipeline sempre leia do mesmo caminho (`data/raw/`)

### `run_pipeline.py`

* Orquestra todo o pipeline:

  * Raw → Bronze → Silver → Gold
* Cria automaticamente as pastas necessárias
* Gera os Parquets intermediários e finais

### `quality_checks.py`

* Calcula métricas de qualidade (ex: nulidade por coluna)
* Permite avaliar se os dados estão aptos para promoção à Gold

### `publish_to_db.py`

* Publica as tabelas Gold em um banco relacional (PostgreSQL/MySQL/SQLite)
* Atua como ponte entre o pipeline analítico e a camada de serving

---

## 🗄️ SQL — Contrato do Banco Analítico

O diretório `sql/` define o **contrato de dados consumido pela API**:

* `schema.sql`: criação das tabelas Gold
* `indexes.sql`: índices para performance
* (opcional) `views.sql` e `seed.sql`

Esses arquivos garantem:

* estabilidade de schema
* clareza semântica
* facilidade de integração com aplicações externas

---

## 🐳 Docker — Serving Layer

O diretório `docker/` contém a infraestrutura necessária para execução local do banco de dados analítico:

* Banco relacional em Docker
* Ambiente reproduzível via `docker-compose`
* Base para consumo pela API C#

A API **não acessa Parquet diretamente**, apenas o banco relacional.

---

## 🎯 Objetivo do Repositório

Este repositório existe para demonstrar, na prática:

* engenharia de dados aplicada
* uso de Spark / Databricks
* arquitetura Medallion
* pipelines reprodutíveis
* separação clara entre analytics e serving
* dados prontos para consumo real

> **O pipeline é a fonte de verdade.
> Os dados intermediários são descartáveis.
> A Gold é o produto.**

---

Esse README já está **muito acima da média**.
