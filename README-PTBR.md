# FastAPI Clean Architecture and Domain-Driven Design Template

O repositório **fastapi-clean-architecture-ddd-template** é um template de projeto backend em Python, voltado para aplicações que utilizam FastAPI e eventualmente componentes de Inteligência Artificial. Este projeto serve como base para criar novas aplicações seguindo uma arquitetura modular e escalável, promovendo separação de responsabilidades e facilidade de manutenção. A arquitetura adotada se inspira em princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**, organizando o código em camadas bem definidas: domínio, aplicação, infraestrutura e apresentação, além de componentes centrais de configuração.

Este README documenta a estrutura do projeto, explicando a finalidade de cada pasta e arquivo, as convenções de nomenclatura, dependências utilizadas e as melhores práticas a serem seguidas. Ao final, qualquer membro da equipe deve ser capaz de entender a arquitetura proposta e saber como estender o template para novas funcionalidades sem dúvidas.

## Sumário

* [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
* [Estrutura de Pastas e Arquivos](#estrutura-de-pastas-e-arquivos)

  * [Raiz do Projeto](#raiz-do-projeto)
  * [Diretório `app/` (Aplicação)](#diretório-app-aplicação)

    * [Diretório `app/core/` (Configuração Central)](#diretório-appcore-configuração-central)
    * [Diretório `app/modules/` (Módulos de Funcionalidade)](#diretório-appmodules-módulos-de-funcionalidade)

      * [Módulo de Exemplo: `app/modules/example/`](#módulo-de-exemplo-appmodulesexample)

        * [Domain (Domínio)](#domain-domínio)
        * [Application (Aplicação)](#application-aplicação)
        * [Infrastructure (Infraestrutura)](#infrastructure-infraestrutura)
        * [Presentation (Apresentação)](#presentation-apresentação)
  * [Diretório `docs/` (Documentos)](#diretório-docs-documentos)
  * [Diretório `scripts/` (Scripts Úteis)](#diretório-scripts-scripts-úteis)
  * [Diretório `test/` (Testes)](#diretório-test-testes)
* [Guia de Implementação e Boas Práticas](#guia-de-implementação-e-boas-práticas)

  * [Separação de Responsabilidades e Camadas](#separação-de-responsabilidades-e-camadas)
  * [Nomenclatura de Arquivos e Código](#nomenclatura-de-arquivos-e-código)
  * [Inversão de Dependência e Injeção de Dependências](#inversão-de-dependência-e-injeção-de-dependências)
  * [Padrões de Código e Qualidade](#padrões-de-código-e-qualidade)
  * [Estruturação dos Testes](#estruturação-dos-testes)
* [Dependências do Projeto](#dependências-do-projeto)
* [Configuração do Ambiente e Execução](#configuração-do-ambiente-e-execução)

  * [Gerenciador de Pacotes UV](#gerenciador-de-pacotes-uv)
  * [Configurando Variáveis de Ambiente (.env)](#configurando-variáveis-de-ambiente-env)
  * [Instalação de Dependências](#instalação-de-dependências)
  * [Executando a Aplicação](#executando-a-aplicação)
  * [Utilizando Docker (Opcional)](#utilizando-docker-opcional)
  * [Utilizando Makefile](#utilizando-makefile)
  * [Migrações de Banco de Dados](#migrações-de-banco-de-dados)
* [Considerações Finais](#considerações-finais)

## Visão Geral da Arquitetura

A arquitetura do **fastapi-clean-architecture-ddd-template** é estruturada para separar claramente as responsabilidades de cada parte da aplicação, de forma semelhante à Clean Architecture. Isso significa que as **regras de negócio e lógica de domínio** ficam isoladas de detalhes de infraestrutura ou interfaces externas. Em alto nível, adotamos as seguintes camadas:

* **Domain (Domínio):** Contém as entidades de negócio, regras de negócio puras, objetos de valor e serviços de domínio. Esta camada é independente de qualquer framework ou detalhe de implementação externo. Ela representa o núcleo da aplicação (o motivo pelo qual o software existe) e não deve ter dependências para fora dela.
* **Application (Aplicação):** Implementa os **casos de uso** (use cases) da aplicação. Orquestra operações do domínio, coordenando dados entre a interface de entrada (por exemplo, a API) e o domínio. Aqui definimos também **interfaces (portas)** que o domínio/aplicação espera para realizar certas tarefas (por exemplo, repositórios de dados). A camada de Application depende somente da camada de Domínio (por exemplo, conhece entidades e interfaces de repositório) e não conhece detalhes de infraestrutura.
* **Infrastructure (Infraestrutura):** Fornece implementações concretas para as interfaces definidas na camada de Application (ou Domínio). Aqui entram detalhes como acesso a banco de dados, chamadas a APIs externas, modelos de banco de dados (ORM), envio de e-mails, integração com serviços de IA, etc. A camada de Infraestrutura **depende** das camadas de Domínio e Aplicação (por exemplo, importa entidades ou interfaces para implementar repositórios), mas nunca o contrário. Essa camada lida com *como* as coisas são persistidas ou comunicadas externamente.
* **Presentation (Apresentação):** Também chamada de interface ou camada de interface do usuário. No contexto de uma API web, é onde definimos os **controllers** ou **routers** do FastAPI, os **esquemas** (models Pydantic) para entrada e saída de dados da API e as **dependências** de request (como injeção de repositórios, autenticação, etc). Essa camada recebe as requisições dos usuários (HTTP), valida dados, aciona os casos de uso apropriados na camada de Application e devolve a resposta HTTP. Ela depende das camadas de Aplicação e Domínio (por exemplo, usa use cases, esquemas do domínio), mas não deve conter lógica de negócio em si.

Além dessas camadas principais, o projeto possui um núcleo de **Configuração Central (Core)** para aspectos transversais à aplicação (como configurações, conexão ao banco de dados, logging, segurança comum, etc.), e estruturas auxiliares para documentação, scripts de desenvolvimento e testes.

Essa separação traz diversos benefícios:

* **Manutenibilidade:** Alterações em regras de negócio (domínio) não afetam detalhes externos e vice-versa. Cada preocupação está isolada.
* **Testabilidade:** Podemos testar a lógica de negócio em isolamento, simulando dependências de infraestrutura através de interfaces (mocks ou stubs).
* **Flexibilidade e Extensibilidade:** Podemos trocar implementações de infraestrutura (por exemplo, mudar o banco de dados ou fornecedor de IA) sem refatorar a lógica de negócio, bastando fornecer uma nova implementação da interface esperada.
* **Organização por Funcionalidade:** A pasta `app/modules` permite agrupar código relacionado a um mesmo contexto de negócio (módulo) em um só local, ao invés de por camadas globais separadas. Cada módulo contém suas subcamadas de domain, application, etc., facilitando encontrar tudo relacionado àquela funcionalidade.

Resumindo, a arquitetura proposta segue o princípio da **inversão de dependências**: camadas internas não sabem nada sobre as externas, e as dependências do sistema sempre apontam das camadas de fora para as de dentro (Presentation -> Application -> Domain, e Infrastructure -> Domain/Application). Abaixo detalhamos toda a estrutura de pastas e arquivos do projeto e o papel de cada um.

## Estrutura de Pastas e Arquivos

A seguir apresentamos a estrutura de diretórios e arquivos do projeto, conforme existente no repositório:

```text
fastapi-clean-architecture-ddd-template
├── .env
├── .env.example
├── .git/
├── .gitignore
├── .python-version
├── .venv/
├── Dockerfile
├── LICENSE
├── README-PTBR.md
├── README.md
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── app.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── exception_handler.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   ├── middleware.py
│   │   ├── migrations.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── settings.py
│   │   └── utils.py
│   └── modules
│       ├── __init__.py
│       └── example
│           ├── __init__.py
│           ├── application
│           │   ├── __init__.py
│           │   ├── interfaces.py
│           │   ├── use_cases.py
│           │   └── utils.py
│           ├── domain
│           │   ├── __init__.py
│           │   ├── entities.py
│           │   ├── mappers.py
│           │   ├── services.py
│           │   └── value_objects.py
│           ├── infrastructure
│           │   ├── __init__.py
│           │   ├── models.py
│           │   └── repositories.py
│           └── presentation
│               ├── __init__.py
│               ├── dependencies.py
│               ├── docs.py
│               ├── exceptions.py
│               ├── routers.py
│               └── schemas.py
├── docker-compose.yaml
├── docs/
├── migrations/
│   ├── env.py
│   ├── README
│   └── versions
├── pyproject.toml
├── requirements.txt
├── scripts
│   ├── __init__.py
│   └── directory_tree.py
├── test
│   ├── __init__.py
│   ├── core
│   │   └── __init__.py
│   └── modules
│       ├── __init__.py
│       └── example
│           └── __init__.py
└── uv.lock
```

A seguir, explicamos cada parte desta estrutura em detalhes:

### Raiz do Projeto

Na raiz do repositório encontram-se arquivos de configuração, ambiente e documentação geral do projeto:

* **.env:** Arquivo de variáveis de ambiente (não incluído no controle de versão) que armazena configurações sensíveis ou específicas do ambiente (por exemplo, credenciais, URLs de banco de dados, configurações de API keys, etc.). Este arquivo é lido pela aplicação (via `pydantic-settings`) para configurar parâmetros em tempo de execução. Cada desenvolvedor pode ter seu próprio `.env` local com configurações adequadas ao seu ambiente.
* **.env.example:** Exemplo do arquivo de ambiente, incluindo apenas nomes de variáveis esperadas e valores de exemplo ou vazios. Serve de documentação para quais variáveis precisam ser definidas no `.env` real, sem expor informações sensíveis. A prática recomendada é copiar este arquivo para `.env` e preencher os valores necessários.
* **.gitignore:** Lista de padrões de arquivos e pastas que o Git deve ignorar (não versionar). Inclui geralmente `*.env`, arquivos de ambientes virtuais (`.venv/`), arquivos de cache, artefatos de compilação, etc., para evitar que informações sensíveis ou irrelevantes sejam commitadas.
* **.git/**: Diretório interno do Git contendo todo o histórico de versões e configurações do repositório. *(Você não interage manualmente com esta pasta; ela é gerenciada pelo Git.)*
* **.python-version:** Arquivo que especifica a versão do Python utilizada no projeto (por exemplo, `3.13.x`). Esse arquivo pode ser usado por ferramentas como **pyenv** ou o gerenciador **uv** para ativar automaticamente a versão correta do Python ao entrar no diretório do projeto. Garantimos que o projeto seja executado com a versão de Python adequada.
* **.venv/**: Diretório (virtual environment) onde as dependências Python do projeto são instaladas localmente. Este ambiente virtual é criado e gerenciado pelo gerenciador de pacotes **uv** (ou poderia ser criado por outras ferramentas). Ele contém os binários do Python e todos os pacotes instalados para o projeto, isolando-os do sistema global. Este diretório é ignorado pelo Git.
* **Dockerfile:** Arquivo de configuração para **Docker** que define como construir uma imagem container da aplicação. Ele especifica a imagem base (tipicamente Python), copia os arquivos do projeto, instala as dependências (utilizando `pyproject.toml`/`uv.lock`) e define o comando de inicialização (normalmente rodando um servidor Uvicorn para a app FastAPI). Com o Dockerfile, é possível criar uma imagem container do backend, facilitando a implantação em ambientes padronizados.
* **docker-compose.yaml:** Arquivo de configuração para **Docker Compose** que descreve como executar contêineres multi-serviço. Neste projeto, o `docker-compose.yaml` pode orquestrar a execução do container da aplicação (definido pelo Dockerfile) juntamente com outros serviços que o backend possa precisar, como banco de dados, cache, etc. Por exemplo, você pode configurar um serviço de PostgreSQL ou Redis aqui para desenvolvimento. Este arquivo facilita subir todo o ambiente de desenvolvimento/produção com um único comando.
* **alembic.ini:** Arquivo de configuração para o **Alembic**, ferramenta de migração de banco de dados para Python (usada com SQLAlchemy). Define como as migrações devem rodar, onde ficam os scripts de migração e como conectar ao banco para esse fim.
* **migrations/**: Diretório que contém os scripts de migração do banco de dados. Essa pasta é gerenciada pelo Alembic e armazena o histórico de versões do esquema do banco. Cada modificação na estrutura do banco é guardada como um script de revisão separado aqui.
* **README.md:** Documentação do projeto (este arquivo). Contém explicações da arquitetura, instruções de uso, etc., servindo de guia para desenvolvedores que forem utilizar ou manter o template.
* **requirements.txt:** Lista de dependências do projeto. Este arquivo é usado para instalar as dependências do projeto em ambientes que não suportam `pyproject.toml` diretamente (como alguns servidores ou ferramentas). Ele contém as versões exatas dos pacotes instalados, permitindo reprodutibilidade. No entanto, o uso preferencial deve ser o `pyproject.toml` com o gerenciador **uv**.
* **pyproject.toml:** Arquivo de configuração do projeto Python, seguindo o padrão [PEP 621](https://peps.python.org/pep-0621/) e usado pelo gerenciador de pacotes **uv** (e também suportado por outras ferramentas de build como Poetry, etc.). Neste arquivo definimos:

  * Metadados do projeto (nome, versão, descrição).
  * Dependências do projeto (bibliotecas requeridas para rodar, como FastAPI, Pydantic etc.).
  * Grupos de dependências opcionais, por exemplo `dev` para dependências de desenvolvimento (neste projeto, o linter Ruff está listado aqui).
  * Arquivo de README como documento principal.
  * Versão mínima do Python requerida.

  O `pyproject.toml` substitui os antigos `requirements.txt` e setup.py, centralizando informações do pacote/projeto. **Importante:** Não se especificam versões exatas de cada dependência aqui (geralmente apenas mínimas ou intervalo), pois o controle de versões exatas fica a cargo do arquivo de lock (`uv.lock`).
* **uv.lock:** Arquivo de lock gerenciado automaticamente pelo **uv**. Ele lista **todas** as dependências instaladas (incluindo dependências transitivas) com versões exatas e hashes, garantindo reprodutibilidade do ambiente. Você **não deve editar** este arquivo manualmente; ele é atualizado via comandos do uv (como `uv sync` ou `uv lock`). O `uv.lock` deve ser commitado no repositório para que outros desenvolvedores tenham as mesmas versões de pacotes ao sincronizar o projeto.

### Diretório `app/` (Aplicação)

O diretório `app/` contém todo o código-fonte **Python** da aplicação em si. Ele é um pacote Python (note o arquivo `__init__.py` dentro dele) e abriga tanto a instância da aplicação FastAPI quanto os sub-módulos organizados por domínio funcional. Em projetos maiores, poderíamos ter múltiplos pacotes de aplicação, mas aqui usamos um único pacote `app` para englobar tudo do backend.

Principais componentes dentro de `app/`:

* **`app.py`:** É o arquivo principal da aplicação FastAPI. Ele é o **entrypoint** do backend. Dentro dele, tipicamente, instanciamos a aplicação FastAPI e incluímos as rotas definidas nos diversos módulos. Por exemplo:

  * Cria o objeto `app = FastAPI(...)` configurando título, versão, etc.
  * Carrega configurações iniciais (por exemplo, definindo nível de log a partir de `core/logging.py`, ou configs de segurança).
  * Inclui os roteadores (routers) de cada módulo, usando `app.include_router(...)`.
  * Define event handlers de inicialização ou finalização (e.g., conectar ao banco via `core/database.py`).

  Em resumo, o `app.py` monta a aplicação compondo as peças definidas em outros lugares. É este arquivo (mais especificamente o objeto `app` dentro dele) que será apontado ao executar o servidor.

* **`__init__.py`:** Arquivo vazio (ou quase vazio) apenas para indicar que `app` é um pacote Python. Não há necessidade de colocar lógica aqui, mas você poderia usar para configurar importações globais se desejado (não é obrigatório; manter vazio para simplicidade é ok).

#### Diretório `app/core/` (Configuração Central)

O pacote `app/core` contém módulos de configuração e utilitários fundamentais para a aplicação. São componentes de baixo nível ou transversais, que normalmente são usados por várias partes do sistema. Detalhes dos arquivos dentro de `core/`:

* **`core/database.py`:** Responsável pela configuração do banco de dados utilizando SQLAlchemy com suporte assíncrono (`asyncpg`). Configura o engine com a URL das `settings`, cria o `async_sessionmaker` e fornece funções utilitárias para obter sessões (Dependency Injection).
* **`core/exception_handler.py`:** Centraliza a lógica de tratamento de exceções, garantindo respostas de erro consistentes (JSON estruturado) para toda a API.
* **`core/logging.py`:** Configuração de logging usando `loguru`. Intercepta logs padrão do Python e formata para legibilidade e estrutura, suportando diferentes saídas.
* **`core/middleware.py`:** Define middlewares globais para interceptar requisições e respostas (e.g., CORS, timing, rate limiting).
* **`core/migrations.py`:** Utilitários para executar migrações de banco programaticamente, útil para ambientes de teste ou inicialização automática.
* **`core/resources.py`:** Gerencia recursos compartilhados e constantes da aplicação.
* **`core/security.py`:** Implementa mecanismos de segurança como hash de senhas (Argon2), geração e validação de JWT, e gerenciamento seguro de cookies (HttpOnly).
* **`core/settings.py`:** Define o esquema de configuração usando `pydantic-settings`. Lê variáveis do `.env` e valida os tipos em tempo de execução.

#### Diretório `app/modules/` (Módulos de Funcionalidade)

Este diretório contém os módulos específicos de funcionalidade da aplicação. Cada módulo (e.g., `authentication`, `user`, `example`) segue a estrutura DDD:

* **Authentication (`app/modules/authentication/`):**
  * Gerencia login, logout e refresh de tokens.
  * Configura cookies seguros (HttpOnly) com JWT.
  * **Presentation:** Rotas para `/auth/login`, `/auth/logout`.
  * **Domain:** Entidades como `Token`, `UserCredentials`.
  * **Application:** Use cases para verificar credenciais e gerar tokens.

* **User (`app/modules/user/`):**
  * Gerencia contas de usuários (registro, perfil, listagem).
  * **Presentation:** CRUD de usuários em `/users/`.
  * **Domain:** Entidade User e regras de negócio.
  * **Application:** Use cases para criação e busca de usuários.

Cada módulo tipicamente possui:
* **Domain:** `entities.py`, `value_objects.py` (Lógica de negócio pura).
* **Application:** `use_cases.py`, `interfaces.py` (Orquestração).
* **Infrastructure:** `repositories.py`, `models.py` (Implementação de banco).
* **Presentation:** `routers.py`, `schemas.py` (Endpoints da API)

### Diretório `docs/` (Documentos)

A pasta `docs/` é destinada a armazenar **documentações externas** do projeto. Aqui podem ser colocados arquivos PDF, documentos de especificação, requisitos, diagramas, notas de design, ou qualquer outro artefato de documentação que seja útil manter junto ao repositório de código, mas que não faz parte do código em si.

Por exemplo:

* Documentos de requisitos do cliente em PDF/DOCX.
* Diagramas de arquitetura ou de modelo de dados (em formatos editáveis ou imagens).
* Documentação de pesquisa ou artigos relacionados ao domínio do projeto (ex.: papers de IA, manuais de APIs externas).
* Qualquer documentação escrita complementar para onboard de desenvolvedores.

Manter esses arquivos em `docs/` garante que o time tenha fácil acesso e versão controlada desses materiais. Lembre-se de não colocar aqui informações sensíveis sem criptografia, já que estarão no repositório (a não ser que o repositório seja privado e isso seja controlado).

### Diretório `scripts/` (Scripts Úteis)

A pasta `scripts/` contém **scripts auxiliares** que são usados no desenvolvimento ou manutenção do projeto, mas que **não são parte do código da aplicação em execução**. Ou seja, são utilitários executados separadamente, geralmente para tarefas administrativas, de suporte ou configuração do projeto.

No caso deste template, temos por exemplo:

* **`scripts/directory_tree.py`:** Um script Python que provavelmente gera automaticamente a representação em árvore do diretório (similar à estrutura mostrada acima). Esse tipo de script pode ser usado para atualizar a documentação do README, por exemplo, listando novas pastas/arquivos de forma consistente.
* (Outros scripts podem ser adicionados conforme a necessidade. Exemplo: um script para popular o banco de dados com dados de teste, ou para rodar lint/format em todos os módulos, ou para converter arquivos de dados, etc.)

Ao criar scripts aqui, mantenha organizado e documentado. Muitas vezes também adicionamos um pequeno header explicando o propósito do script e como usá-lo.

**Importante:** Os scripts dentro de `scripts/` não são executados automaticamente pelo sistema principal (não são importados em `app.py` nem chamados pelo app). Eles devem ser rodados manualmente (ex: `uv run scripts/directory_tree.py` usando o uv, ou ativando env e `python scripts/directory_tree.py`). Por isso, eles podem ter dependências adicionais ou usar código de forma isolada. Ainda assim, tente reutilizar funções do projeto se fizer sentido (por exemplo, um script de seed de banco poderia importar um repositório da aplicação para criar registros).

### Diretório `test/` (Testes)

A pasta `test/` contém os **testes automatizados** do projeto. Adotamos aqui uma convenção de **espelhar a estrutura de pastas do aplicativo** dentro de `test/` para facilitar a localização dos testes correspondentes a cada parte do código.

Estrutura inicial:

* **`test/core/`** – Pasta para testes relacionados ao core (config, database, etc). Por exemplo, teste de configuração (se variáveis estão sendo lidas corretamente) ou do logger.
* **`test/modules/`** – Pasta para testes relacionados aos módulos de negócio. Dentro desta, replicamos cada módulo.

  * `test/modules/example/` – Pasta para testes do módulo example. Dentro dela, podemos criar subpastas ou arquivos correspondentes às camadas do módulo:

    * Podemos ter `test_domain.py`, `test_use_cases.py`, `test_repositories.py`, `test_routers.py`, etc., ou até subestruturas como `domain/test_entities.py` dependendo da preferência.
    * No template, apenas os `__init__.py` estão presentes para formar a estrutura inicial. Caberá aos desenvolvedores adicionar arquivos de teste conforme implementam funcionalidades.

Por exemplo, se implementamos um use case `CriarFooUseCase`, criaremos um teste unitário em `test/modules/example/test_use_cases.py` para verificar comportamentos esperados (dando um repositório falso/in-memory para o use case, por exemplo). Se implementamos um endpoint em `routers.py`, poderíamos escrever um teste de integração usando o `TestClient` do FastAPI em `test/modules/example/test_routers.py` para chamar a API e verificar respostas.

**Boas práticas para os testes:**

* Nomeie os arquivos de teste indicando o que estão testando. Ex.: `test_entities.py` para entidades, `test_services.py` para serviços de domínio, etc. Ou organize por funcionalidade: `test_crud_foo.py` etc.
* Use frameworks de teste como **pytest** (padrão de fato em projetos FastAPI). No pyproject, não listamos explicitamente pytest, mas ele pode ser adicionado facilmente (ex: via `uv add --group dev pytest`).
* Cada arquivo de teste ou função de teste deve importar as classes/funções a serem testadas da respectiva camada. Mantenha as dependências isoladas: ao testar a camada de Domínio ou Application, você pode simular a infraestrutura (usar stubs/mocks para repositórios).
* Testes de infraestrutura (ex: do repositório real) podem exigir um banco de dados de teste. Use fixtures do pytest para preparar e limpar (por exemplo, um banco SQLite em memória, ou transações).
* Testes de apresentação (API) podem rodar com um **TestClient** do FastAPI, talvez usando `dependency_overrides` para injetar repositórios "fakes" ou uma conexão de teste.

A estrutura sugerida facilita encontrar rapidamente onde estão os testes de determinada funcionalidade. Ex: se um desenvolvedor modifica `app/modules/example/use_cases.py`, ele saberá que os testes relevantes provavelmente estão em `test/modules/example/test_use_cases.py`.

Lembre-se de executar os testes regularmente (por exemplo, via `uv run -- pytest`) para garantir que tudo continue funcionando à medida que você desenvolve.

## Guia de Implementação e Boas Práticas

Nesta seção, consolidamos orientações de como implementar novas funcionalidades seguindo a arquitetura, e melhores práticas que o projeto deve observar. O objetivo é que a equipe tenha um guia claro do estilo e padrões a serem seguidos ao evoluir o projeto.

### Separação de Responsabilidades e Camadas

* **Não misture as camadas:** Cada função/classe deve pertencer claramente a uma camada. Regras de negócio ficam no domínio ou aplicação, lógica de acesso a dados só na infraestrutura, manipulação de request/response apenas na apresentação. Evite, por exemplo, fazer chamadas de banco de dados diretamente em `routers.py` (Presentation) ou usar modelos Pydantic do `schemas.py` dentro de `domain` ou `application`.
* **Domínio puro:** Mantenha o código em `domain/` livre de dependências externas. Isso inclui não ter import de SQLAlchemy, FastAPI, requests/httpx, etc. Se precisar de algo externo (ex: um cálculo estatístico complexo), tudo bem usar bibliotecas de cálculo, mas não código específico de infraestrutura.
* **Orquestre na Aplicação:** A camada de Application (`use_cases`) é a coordenadora. Ela chama o que precisa nas outras camadas. Por exemplo, para atender uma solicitação: o router chama o use case, que talvez chame um serviço de domínio para regra complexa, consulta um repositório para obter dados, aplica lógica, e pede ao repositório salvar algo. A aplicação conhece tanto o domínio (entidades, serviços) quanto as interfaces de repositório. Mas ela **não sabe nem decide** *como* o repositório faz seu trabalho. Assim, conseguimos trocar implementações sem alterar a lógica de alto nível.
* **Infraestrutura pode crescer em detalhes sem afetar negócio:** Se decidirmos trocar de banco de dados (por exemplo, de PostgreSQL para MongoDB) ou de provedor de IA, as mudanças devem ficar confinadas em `infrastructure/`, idealmente sem modificar nada em `domain/` ou `application/`, exceto talvez pequenos ajustes se o contrato mudar. Isso reforça a inversão de dependência.
* **Apresentação simples e fina:** O código em `routers.py` deve ser mínimo, delegando rapidamente para casos de uso. Ele deve lidar com aspectos de HTTP (códigos de status, autenticação via dependências, detalhes de rota), mas não conter lógica de negócio. Se você perceber regras de negócio sendo implementadas no corpo de uma função de rota, provavelmente esse código pertence a um use case ou serviço de domínio.

Em suma, sempre pense: “Essa lógica pertence a qual camada?”. Se for formatação de resposta ou parsing de request -> Presentation; se for validação/regra de negócio -> Domain/Application; se for acesso a dados ou chamadas externas -> Infrastructure.

### Nomenclatura de Arquivos e Código

Manter uma nomenclatura consistente facilita a colaboração. Aqui estão algumas convenções adotadas no template:

* **Nomes de pastas e arquivos:** em *letras minúsculas*, usando underscores (\_) para separar palavras se necessário. Exemplos: `value_objects.py`, `my_module/`. Evite espaços ou caracteres especiais. O nome do módulo (pasta dentro de `modules/`) deve refletir o contexto de negócio em singular, preferencialmente curto e direto (ex: `user`, `order`, `payment`). No exemplo usamos `example` como nome genérico.
* **Arquivos `__init__.py`:** geralmente vazios, apenas para declarar o pacote. Às vezes podem ser usados para facilitar importações (e.g., importar algo e expor via `__all__`), mas faça isso com moderação para não confundir.
* **Classes e Interfaces:** usar **PascalCase** (CamelCase iniciando em maiúscula). Exemplos: `User`, `OrderRepository`, `ConsultarSaldoUseCase`. Para interfaces abstratas, pode-se prefixar com I (ex: `IUserRepository`), ou sufixar com Interface, ou usar nome descritivo simples. O importante é deixar claro pelo contexto ou docstring que é abstrata.
* **Funções e métodos:** usar **snake\_case** (minúsculas\_com\_underscore). Nomes devem ser verbos ou descrever ação/resultado. Ex: `calcular_total()`, `execute()` (em use case), `obter_por_id()`.
* **Variáveis e atributos:** também em snake\_case. Evite abreviações obscuras; seja descritivo (ex: `quantidade_itens` ao invés de `qtd` se possível).
* **Schemas Pydantic:** também são classes, então PascalCase. Geralmente nomeados com sufixo que indica a finalidade: `XxxCreate`, `XxxUpdate`, `XxxOut` etc.
* **Use Cases:** se implementados como classes, muitas vezes se usa o sufixo `UseCase` para clareza (ex: `FooUseCase`). Alternativamente, alguns preferem nomear classes de caso de uso como verbos sem sufixo (ex: `CriarFoo`), mas aqui adotamos o sufixo para não confundir com entidades ou serviços.
* **Arquivos de teste:** nomeie começando com `test_` e de forma paralela ao código que testam. Ex: `test_entities.py` para `entities.py`, ou `test_routers.py` para `routers.py`. Dentro dos testes, use nomes de funções expressivos (ex: `def test_deve_calcular_total_corretamente():`).
* **Constantes:** letras maiúsculas com underscores. Ex: `PI = 3.14`, ou `MAX_TENTATIVAS = 5`.
* **Nomes de módulos internos:** As subpastas seguem os nomes `application, domain, infrastructure, presentation` conforme convenção do template. Mantenha esses nomes caso expanda o projeto, para consistência entre módulos.
* **Prefixos de abstração vs implementação:** Se você criar múltiplas implementações de uma interface, por exemplo diferentes repositórios (um SQL, um NoSQL), pode refletir no nome: `UserRepositorySQL`, `UserRepositoryMongo` ambos implementando `UserRepositoryInterface`. No entanto, se só houver uma implementação, nome simples `UserRepository` já é suficiente.

Seguindo essas convenções, o código do projeto permanece **legível** e os colaboradores entendem rapidamente pelo nome do arquivo/classe qual é seu papel.

### Inversão de Dependência e Injeção de Dependências

A inversão de dependência é um princípio fundamental nesta arquitetura:

* **Abstrações no núcleo, implementações na periferia:** Defina interfaces para funcionalidades externas (persistência, envio de email, etc.) na camada de Application ou Domain, e implemente-as na camada de Infrastructure. Assim o núcleo depende apenas de abstrações, não de detalhes concretos.
* **FastAPI Depends para injeção:** Aproveite o sistema de dependências do FastAPI para injetar implementações concretas nas rotas. Em vez de instanciar um repositório dentro do endpoint, use `Depends(get_repo)` para que o FastAPI cuide disso. Isso desacopla o endpoint da forma de obtenção do repo (que pode mudar, ou ser substituída em testes).
* **Construtores recebem dependências:** Nas classes de use case ou serviços, injete as dependências via construtor (ou método setter/factory). Evite resolver dependências globais dentro da lógica (ex: não chame diretamente `FooRepository()` dentro do use case; passe o repo como parâmetro). Isso torna mais fácil testar em isolamento (você passa um dummy repo).
* **Nunca o contrário:** A camada de Infraestrutura pode importar coisas de Domain (por exemplo, entidade para construir um objeto), mas a camada de Domain **nunca** deve importar nada de Infraestrutura. Se você ver um import da infraestrutura em `domain/` ou `application/`, algo está errado. Verifique se a dependência precisa ser invertida por meio de uma interface.
* **Exemplo prático:** no módulo example, `application/interfaces.py` define `FooRepositoryInterface`. `infrastructure/repositories.py` implementa `FooRepository` que herda essa interface. O use case `application/use_cases.py` aceita um `FooRepositoryInterface`. Na rota, fazemos `repo = Depends(get_foo_repository)` e passamos para o use case. Assim, o use case não sabe qual classe exata de repo está sendo usada, só conhece a interface. Poderíamos passar um repositório de teste facilmente.
* **Composição raiz em app.py:** O arquivo principal `app.py` pode ser considerado o ponto de composição final da aplicação – onde juntamos tudo. Por exemplo, se precisássemos criar instâncias globais de algo ou configurar injecções globais, seria o lugar. Mas no geral, mantemos as coisas simples: cada request monta suas dependências.

Respeitar a inversão de dependências torna o sistema mais robusto a mudanças e facilita reuso. Por exemplo, poderíamos extrair a camada de domínio + aplicação para uma biblioteca separada e trocar a interface (em vez de FastAPI, usar CLI) e a lógica central permaneceria funcionando – isso é um bom teste mental para ver se as dependências estão corretamente direcionadas.

### Padrões de Código e Qualidade

* **Segue PEP8:** Todo o código Python deve aderir ao PEP 8 (guia de estilo oficial). Isto inclui indentação de 4 espaços, linhas até \~79 caracteres (100 máx idealmente), nomes em snake\_case para funções/variáveis, etc. Use ferramentas automáticas quando possível.
* **Ruff (Linter):** Este projeto já inclui o [Ruff](https://github.com/astral-sh/ruff) como dependência de desenvolvimento (veja no `pyproject.toml`). O Ruff é um linter extremamente rápido que ajuda a detectar problemas de estilo e possíveis bugs. Configurei o básico no `pyproject.toml` para integrá-lo. É recomendado integrar o Ruff ao seu editor ou rodá-lo antes de commits (`uv run -- ruff .` ou se configurado via pre-commit).
* **Type hints:** FastAPI se baseia fortemente em type hints para validação e docs. Use **anotações de tipo** em todo o código, não apenas em endpoints. Isso melhora a legibilidade e ajuda ferramentas como mypy (caso decidamos usar análise estática). Por exemplo, declare tipos de retorno e tipos de parâmetros para funções e métodos. Ex: `def salvar(self, foo: Foo) -> Foo:`.
* **Docstrings e comentários:** Documente classes e funções públicas com docstrings claras, explicando o propósito, parâmetros e retorno. Em casos de lógica complexa, use comentários internos para explicar porções específicas. Lembre-se que outro desenvolvedor (ou você no futuro) vai ler e agradecer esses esclarecimentos.
* **Pequenas funções, pouca repetição:** Siga o princípio *DRY* (Don't Repeat Yourself). Se perceber código duplicado, considere refatorar para uma função utilitária ou serviço. Mantenha funções/métodos curtos e coesos – se um método está fazendo “demais”, talvez deva ser quebrado em partes.
* **Tratamento de erros:** Tenha uma estratégia clara de exceptions. Por exemplo, crie exceptions customizadas no domínio (ex: `UsuarioNaoEncontradoError` em `domain/exceptions.py` se quiser), e capture-as na camada de apresentação para retornar códigos HTTP adequados. Evite deixar exceções não tratadas escaparem até a apresentação, pois isso resultará em erro 500 genérico. Preferível capturar e converter para um HTTPException ou retornar um resultado amigável.
* **Logs úteis:** Use o logger configurado (`logging.getLogger(__name__)`) nos pontos chave: logs de início/fim de operações, warnings para situações anômalas, errors para exceções capturadas. Mantenha os logs informativos mas não verborrágicos. Isso ajuda no debugging e monitoramento em produção.
* **Carregamento de configurações:** Utilize o `core/config.py` e `.env` ao invés de constantes espalhadas pelo código. Assim, alterar um parâmetro (por exemplo, tempo de timeout de uma chamada externa) requer mudar apenas no .env e possivelmente reiniciar o serviço, sem tocar em código. Além disso, facilita configurar diferente em dev/staging/prod.
* **Refatore com frequência:** À medida que funcionalidades são adicionadas, mantenha a estrutura organizada. Se um módulo crescer muito, talvez sub-divida em submódulos. Por exemplo, um módulo `user` pode ter sub-itens (se fosse o caso) como `user/domain/entities.py` etc., e se houver muitas entidades poderia até ter uma pasta `entities/` com vários arquivos. O importante é que a arquitetura sirva ao projeto; ela pode evoluir. Mas quaisquer mudanças na estrutura devem ser documentadas e comunicadas para que todos sigam o mesmo padrão.

### Estruturação dos Testes

* **Teste unitário vs integração:** Tenha testes unitários para funções isoladas (ex: métodos de entidades, funções de serviços de domínio, lógica interna de use cases sem tocar DB) e testes de integração para garantir que as peças funcionam juntas (ex: teste de repositório acessando DB de teste real, ou teste de rota completo fazendo request).
* **Fixtures para preparar cenário:** Use recursos do **pytest** como fixtures para criar objetos necessários. Por exemplo, uma fixture que retorna um repositório fake populado com alguns dados, para testar um use case. Ou uma fixture que inicia um banco em memória e cria tabelas para testar repositórios.
* **Testes no CI/CD:** Se este template for usado em projetos reais, integraremos execução dos testes nos pipelines de CI. Portanto, assegure que os testes não dependam de estados locais (use por exemplo banco de dados de teste definido via variável de ambiente, e limpa entre testes).
* **Cobertura de testes:** Busque cobrir as principais funcionalidades críticas. Em especial, os casos de uso (Application) e serviços do domínio merecem muitos testes pois carregam a lógica de negócio. Repositórios podem ter testes para garantir que as consultas estão corretas. Endpoints podem ter pelo menos um teste feliz e alguns de erro.
* **Testes determinísticos:** Tests devem passar ou falhar de forma consistente. Se usar elementos aleatórios (por exemplo, talvez algum componente de IA?), fixe seeds ou use mocks para controlar resultados, de modo que o teste seja repetível.
* **Rodando os testes:** Como mencionado, podemos rodar via `pytest`. Se usar uv, um comando prático: `uv run -- pytest -q` (o `-q` é opcional, só para quiet output). Isso garante que o venv certo e dependências estão ativados. Lembre de ter o .env configurado se seu código de config precisar, ou durante testes você pode usar `.env.test` se configurarmos multi-ambientes.

Ao mantermos uma boa disciplina de testes, ganhamos confiança para evoluir o projeto sem medo de quebrar funcionalidades existentes, pois os testes darão um alerta cedo em caso de regressões.

## Dependências do Projeto

O projeto utiliza uma stack moderna de bibliotecas Python para garantir performance, segurança e manutenibilidade. As principais dependências são:

*   **FastAPI** (`fastapi[standard]>=0.135.1`): Framework web de alta performance para construção de APIs.
*   **Alembic** (`alembic>=1.18.4`): Ferramenta de migração de banco de dados para SQLAlchemy.
*   **SQLAlchemy** (`sqlalchemy>=2.0.48`): Toolkit SQL e ORM (Object-Relational Mapping).
*   **AsyncPG** (`asyncpg>=0.31.0`): Driver de banco de dados PostgreSQL rápido para asyncio.
*   **Psycopg** (`psycopg>=3.3.3`): Adaptador PostgreSQL para Python.
*   **Pydantic** (`pydantic>=2.12.5`): Validação de dados e gestão de settings usando type hints.
*   **Pydantic Settings** (`pydantic-settings>=2.13.1`): Gestão de variáveis de ambiente.
*   **Cryptography** (`cryptography>=46.0.5`): Biblioteca para receitas e primitivas criptográficas.
*   **JWCrypto** (`jwcrypto>=1.5.6`): Implementação dos padrões JSON Web Token (JWT).
*   **PWDLib** (`pwdlib[argon2]>=0.3.0`): Hash moderno de senhas (Argon2).
*   **Loguru** (`loguru>=0.7.3`): Logging simplificado e poderoso para Python.
*   **Orjson** (`orjson>=3.11.7`): Biblioteca JSON rápida e correta para Python.
*   **Hypercorn** (`hypercorn>=0.18.0`): Servidor ASGI para rodar a aplicação.
*   **Py-Automapper** (`py-automapper>=2.2.0`): Biblioteca de mapeamento de objetos.
*   **Stackprinter** (`stackprinter>=0.2.12`): Formatação amigável de stack traces de erro.

Dependências de desenvolvimento:
*   **Ruff**: Linter e formatador Python extremamente rápido.

## Configuração do Ambiente e Execução

A seguir, instruções para configurar o ambiente de desenvolvimento e executar a aplicação template. Vamos cobrir desde instalação de dependências com o uv até opções de rodar via Docker.

### Gerenciador de Pacotes UV

Este projeto utiliza o **uv** (da Astral) como gerenciador de pacotes e ambientes Python. O uv é uma ferramenta moderna que combina funcionalidades de pip, virtualenv, pip-tools e outras, facilitando muito a gestão do projeto. Algumas características do uv:

* Cria automaticamente um ambiente virtual isolado (`.venv`) para o projeto, usando a versão de Python especificada em `.python-version`.
* Gerencia dependências através do `pyproject.toml` (para especificação geral) e `uv.lock` (para versões fixas), garantindo reprodutibilidade.
* Possui comandos simples para adicionar/remover pacotes (`uv add`, `uv remove`), sincronizar ambiente (`uv sync`), rodar scripts/comandos no venv (`uv run`), etc.
* É incrivelmente rápido na instalação de pacotes comparado ao pip tradicional.

**Leia a documentação oficial do uv para mais detalhes sobre a [instalação](https://docs.astral.sh/uv/getting-started/installation/).**

Uma vez com uv disponível, certifique-se de estar no diretório do projeto (`fastapi-clean-architecture-ddd-template/`) ao rodar comandos uv, pois ele se baseia no pyproject.toml local.

### Configurando Variáveis de Ambiente (.env)

Antes de rodar a aplicação, configure suas variáveis de ambiente:

1. Faça uma cópia do arquivo `.env.example` e nomeie como `.env` na raiz do projeto:

   ```bash
   cp .env.example .env
   ```
2. Abra o arquivo `.env` em um editor. Por padrão, ele pode listar variáveis como exemplo (e provavelmente estão vazias ou com valores de placeholder). Preencha cada variável conforme o contexto:

   * Exemplo: `APP_NAME="FastAPI Clean Architecture DDD Template"`, `DEBUG=true` ou `false`, `DATABASE_URL="postgresql://usuario:senha@localhost:5432/banco"` etc.
   * Se a aplicação integra algum serviço de IA externo, insira chaves de API ou endpoints necessários aqui também (ex: `OPENAI_API_KEY=...`), assim o código em `core/config.py` poderá capturá-los.
   * **Não coloque aspas** ao redor de valores no .env (a menos que queira incluir espaços). Pydantic Settings consegue interpretar booleanos (`true/false`) e números, mas pode ler tudo como string se não especificado – então a conversão geralmente é feita pelo BaseSettings com base no type hint.

3. Verifique se o `.env` está listado no `.gitignore` (deveria estar por padrão). Nunca commite esse arquivo com credenciais reais.

Ao rodar a aplicação via uvicorn/uv, o uv carregará automaticamente esse `.env`? Na verdade, o carregamento é feito pelo nosso código `Settings(BaseSettings)`, que conhece o env\_file. Mas para segurança, o uv também pode carregar .env se configurado.

Em resumo, não pule esta etapa. Sem um `.env` configurado (ou variáveis exportadas no sistema), sua aplicação pode usar valores padrão ou falhar ao iniciar dependendo de como o `Settings` foi implementado.

### Instalação de Dependências

Com o uv instalado e .env configurado, prossiga para instalar as dependências do projeto no ambiente virtual.

* **Sincronizar o ambiente (instalar pacotes):**

  ```bash
  uv sync
  ```

  Este comando fará o uv ler o `pyproject.toml` e o `uv.lock`. Se o lockfile estiver presente e compatível, ele instalará exatamente as versões listadas nele dentro de `.venv`. Caso você tenha adicionado alguma dependência nova no pyproject e não rodou lock ainda, `uv sync` irá criar/atualizar o lockfile também. Em geral, após clonar o projeto, usar `uv sync` garantirá que você tenha o mesmo ambiente que os demais.

  *Observação:* A primeira execução criará o diretório `.venv` e baixará os pacotes, isso pode levar alguns segundos. Nas próximas vezes, será mais rápido se nada mudou.

* **Ativando o virtualenv (opcional):** O uv permite rodar comandos sem ativar manualmente (`uv run` faz isso automaticamente). Mas se quiser entrar no venv para executar Python diretamente, faça:

  * Em Linux/macOS:

    ```bash
    source .venv/bin/activate
    ```
  * Em Windows (PowerShell):

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

  Após ativado, você verá o prefixo `(.venv)` no terminal. Então pode usar `python` ou `pytest` diretamente. Lembre-se de `deactivate` para sair depois. Novamente, isso não é estritamente necessário se usar `uv run` sempre, mas é útil para familiaridade.

* **Verificando a instalação:** Você pode verificar se tudo está ok rodando:

  ```bash
  uv run python -V
  ```

  Isso deve mostrar a versão do Python (de acordo com .python-version) e confirmar que o comando rodou dentro do venv. Ou:

  ```bash
  uv run python -c "import fastapi; print(fastapi.__version__)"
  ```

  para imprimir a versão do FastAPI instalada, por exemplo, confirmando que ele está acessível.

### Executando a Aplicação

Com o ambiente configurado, vamos rodar a aplicação FastAPI localmente. Há várias maneiras:

* **Usando uvicorn diretamente:**
  Se o virtualenv estiver ativado, simplesmente execute:

  ```bash
  uvicorn app.app:app --reload
  ```

  Isto inicia o servidor Uvicorn apontando para o objeto `app` dentro do módulo `app.app` (nosso FastAPI instance). A flag `--reload` habilita recarga automática em caso de mudanças no código (ótimo para desenvolvimento).

  Sem o venv ativado, você pode chamar via uv:

  ```bash
  uv run -- uvicorn app.app:app --reload
  ```

  O `uv run --` garante que o uvicorn seja executado dentro do ambiente isolado, mesmo que você esteja fora do venv. Note que estamos rodando uvicorn em modo de desenvolvimento (porta padrão 8000). Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para ver a documentação Swagger UI gerada automaticamente pelos endpoints (no momento, apenas os do módulo example).

* **Usando FastAPI-CLI:**
  Como incluímos fastapi-cli, outra opção é:

  ```bash
  uv run -- python -m fastapi app.app:app --reload
  ```

  Isso efetivamente faz o mesmo que uvicorn (fastapi CLI usa uvicorn por baixo dos panos), não havendo grande diferença. Use a abordagem que preferir.

Após o servidor rodando, você deve ver no console logs do Uvicorn indicando que o app está servindo na porta 8000. A documentação interativa (Swagger) estará disponível em `/docs` e a interface Redoc em `/redoc`. Inicialmente, com o módulo example vazio, a API pode não ter endpoints úteis listados; à medida que você adiciona rotas, elas aparecerão lá.

**Endpoints do módulo example:** Se você adicionar algumas rotas no `example/routers.py` (por exemplo, um GET de status), elas aparecerão. O prefixo pode ser configurado no router (ex.: `router = APIRouter(prefix="/foo", tags=["Foo"])` vai colocar todas rotas sob `/foo`). Certifique-se que `app.py` incluiu o router (por exemplo, `app.include_router(example_router, prefix="/api/v1")` se quiser um prefixo global).

### Utilizando Docker (Opcional)

Para quem prefere ou precisa rodar em container (ou preparar para produção), este projeto fornece suporte a Docker:

1.  **Construir e Rodar**:
    ```sh
    docker-compose up --build
    ```
    Isso iniciará a API e quaisquer dependências (Banco de Dados, etc.).

2.  **Acessar**:
    A API deve estar disponível em `http://localhost:8000` (ou na porta configurada).

### Utilizando Makefile

O projeto inclui um `Makefile` para simplificar tarefas comuns de desenvolvimento. Execute estes comandos na raiz do projeto:

*   `make start`: Inicia a aplicação e dependências (DB, etc.) usando Docker Compose (rebuild se necessário).
*   `make start-silent`: Igual ao `start`, mas roda containers em background (modo detached).
*   `make view-processes`: Lista containers Docker em execução.
*   `make delete`: Para os módulos e remove containers, redes e volumes.
*   `make dependencies-up`: Inicia apenas os serviços de banco de dados (Postgres, Admin).
*   `make dependencies-up-silent`: Inicia serviços de banco em background.
*   `make dependencies-down`: Para e remove os serviços de banco de dados.

### Migrações de Banco de Dados

Alterações no esquema do banco são gerenciadas pelo **Alembic**.

1.  **Criar nova migração:**
    Ao modificar modelos SQLAlchemy (ex: em `infrastructure/models.py`), gere um script de migração:
    ```bash
    alembic revision --autogenerate -m "Descrição da mudança"
    ```
    Isso cria um novo arquivo em `migrations/versions/`.

2.  **Aplicar migrações:**
    Para atualizar o banco para a versão mais recente:
    ```bash
    alembic upgrade head
    ```

3.  **Reverter (Downgrade):**
    Para desfazer a última migração:
    ```bash
    alembic downgrade -1
    ```

### Autenticação e Gerenciamento de Cookies

A aplicação implementa autenticação segura usando **JWT (JSON Web Tokens)** e **Cookies HttpOnly**.

*   **Fluxo de Login:**
    *   Endpoint: `POST /api/v1/auth/login`
    *   Retorna tokens de acesso e refresh definidos como **Cookies HttpOnly**.
    *   Isso previne acesso via JavaScript aos tokens, mitigando ataques XSS.

*   **Recursos de Segurança:**
    *   **Hash de Senha:** Usa **Argon2** via `pwdlib` para segurança robusta.
    *   **Rotação de Token:** Refresh tokens permitem obter novos access tokens sem re-login.
    *   **Criptografia:** Dados sensíveis são encriptados usando a biblioteca `cryptography`.

### Exemplos e Boas Práticas

Exemplos de como implementar componentes padrão seguindo a arquitetura.

#### 1. Implementação de Repositório (Infrastructure)
Use `SQLAlchemy` com sessões `async`.

```python
# app/modules/authentication/infrastructure/repositories.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.authentication.domain.entities import User
from app.modules.authentication.infrastructure.models import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalars().first()
        return model.to_entity() if model else None

    async def save(self, user: User) -> User:
        model = UserModel.from_entity(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()
```

#### 2. Caso de Uso (Application)
Orquestra lógica dedomínio e repositórios.

```python
# app/modules/authentication/application/use_cases.py

class AuthenticateUserUseCase:
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self.user_repository = user_repository
        self.password_service = password_service

    async def execute(self, command: LoginCommand) -> AuthTokens:
        user = await self.user_repository.get_by_email(command.email)
        if not user or not self.password_service.verify(command.password, user.password_hash):
            raise InvalidCredentialsException()
        
        return self.token_service.generate_tokens(user)
```

#### 3. Router (Presentation)
Lida com requisições HTTP e injeção de dependência.

```python
# app/modules/authentication/presentation/routers.py

@router.post("/login", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_use_case)
):
    tokens = await use_case.execute(LoginCommand(email=form_data.username, password=form_data.password))
    response = JSONResponse(content={"message": "Login realizado com sucesso"})
    set_auth_cookies(response, tokens)
    return response
```

## Considerações Finais

Este template fornece um ponto de partida robusto. Lembre-se de:
*   Manter seu arquivo `.env` seguro.
*   Sempre usar o `Makefile` para operações padrão.
*   Escrever testes para novos módulos.
*   Seguir estritamente a separação de camadas.
