Boa pedida — isso é **sinal clássico de projeto maduro**.
Um README bom **orienta o leitor espacialmente** antes de entrar na teoria. Vamos encaixar isso de forma limpa e profissional.

Abaixo está o **README da camada de dados**, já **com a árvore do projeto integrada**, mantendo o tom de engenharia real (e sem virar manual chato).

---

# 📊 Data Platform — RentSight

Este repositório contém a **camada de dados** do projeto **RentSight**, responsável por ingestão, processamento, modelagem e disponibilização de dados analíticos para consumo por APIs e aplicações.

A arquitetura segue o padrão **Medallion (Bronze → Silver → Gold)** e foi construída com foco em **engenharia de dados, clareza arquitetural e reprodutibilidade**.

---

## 🗂️ Estrutura do Projeto

```
data_plataform/
├── databricks/
│   │
│   ├── bronze/
│   │       └── raw_inspect_data.ipynb
│   │
│   ├── silver/
│   │       └── silver_select_columns_cleaned.ipynb
│   │
│   └── gold/
│
├── ingest/
│   ├── parquet_to_sqlite.py
│   └── parquet_to_mysql.py
│
├── seed/
│   ├── schema.sql
│   └── seed.sql
│
└── README.md
```

Cada diretório representa uma responsabilidade bem definida dentro da plataforma de dados.

---

## 🔶 Databricks — Processamento Analítico

O diretório `databricks/` concentra os notebooks responsáveis pelo processamento e transformação dos dados, seguindo a arquitetura Medallion.

### 🥉 Bronze Layer — Raw Data

* Armazena os dados exatamente como foram recebidos da fonte
* Nenhuma transformação ou regra de negócio é aplicada
* Serve como fonte de verdade para todo o pipeline

Usada para inspeção inicial, validação de schema e rastreabilidade.

---

### 🥈 Silver Layer — Clean & Structured Data

* Seleção de colunas relevantes para o domínio do problema
* Padronização e correção de tipos de dados
* Normalização de identificadores
* Tratamento técnico de valores inválidos
* Preservação consciente de valores nulos

Essa camada entrega dados **confiáveis, consistentes e prontos para análise**, sem ainda aplicar regras de negócio.

---

### 🥇 Gold Layer — Analytics & Insights

* Aplicação de regras de negócio
* Criação de métricas e indicadores analíticos
* Agregações por bairro, tipo de imóvel e período
* Views otimizadas para consumo por APIs e dashboards

Essa camada é orientada a **uso real**, servindo diretamente o backend da aplicação.

---

## 🔄 Ingest — Exportação para Bancos Relacionais

O diretório `ingest/` contém scripts responsáveis por **converter os dados processados (Parquet)** para bancos relacionais.

Esses scripts permitem:

* Persistência local rápida (SQLite)
* Evolução futura para bancos como MySQL ou PostgreSQL
* Separação clara entre processamento analítico e camada de serving

Essa abordagem evita o acoplamento direto da API ao Databricks.

---

## 🗄️ Seed — Banco de Dados Reproduzível

O diretório `seed/` contém scripts SQL que garantem uma **experiência de execução simples e previsível** para quem clona o projeto.

### `schema.sql`

* Define a estrutura do banco de dados
* Cria tabelas, tipos e relações necessárias
* Serve como contrato entre dados e aplicação

### `seed.sql`

* Insere um recorte pequeno e coerente de dados analíticos
* Permite que a API funcione imediatamente após o setup
* Representa dados já processados, não o pipeline completo

Esses arquivos **não substituem o ETL real**, mas tornam o projeto executável localmente.

---

## 🧠 Decisões Arquiteturais

* O Databricks é utilizado exclusivamente para processamento e analytics
* A API consome apenas dados já tratados e persistidos
* O banco SQLite é usado para desenvolvimento e demonstração
* A arquitetura é preparada para escalar para MySQL/PostgreSQL sem mudanças estruturais

---

## 🎯 Objetivo do Repositório

Este repositório existe para demonstrar, na prática:

* Engenharia de dados
* Databricks e Apache Spark
* Arquiteturas analíticas modernas
* Boas práticas de separação de responsabilidades
* Construção de pipelines reprodutíveis e escaláveis

