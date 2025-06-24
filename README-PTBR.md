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
├── README.md
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── security.py
│   └── modules/
│       ├── __init__.py
│       └── example/
│           ├── __init__.py
│           ├── application/
│           │   ├── __init__.py
│           │   ├── interfaces.py
│           │   └── use_cases.py
│           ├── domain/
│           │   ├── __init__.py
│           │   ├── entities.py
│           │   ├── services.py
│           │   └── value_objects.py
│           ├── infrastructure/
│           │   ├── __init__.py
│           │   ├── models.py
│           │   └── repositories.py
│           └── presentation/
│               ├── __init__.py
│               ├── dependencies.py
│               ├── routers.py
│               └── schemas.py
├── docker-compose.yaml
├── docs/
├── requirements.txt
├── pyproject.toml
├── scripts/
│   ├── __init__.py
│   └── directory_tree.py
├── test/
│   ├── __init__.py
│   ├── core/
│   │   └── __init__.py
│   └── modules/
│       ├── __init__.py
│       └── example/
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
  * Carrega configurações iniciais (por exemplo, definindo nível de log a partir de `core/logging.py`, ou lendo configurações de `core/config.py`).
  * Inclui os roteadores (routers) de cada módulo, usando `app.include_router(...)` para registrar as rotas das diferentes partes da API. No nosso caso, ele incluirá o roteador do módulo de exemplo (e futuramente, de outros módulos).
  * Define event handlers de inicialização ou finalização se necessário (por exemplo, função `startup` para conectar ao banco de dados usando `core/database.py`, ou `shutdown` para fechar conexões).

  Em resumo, o `app.py` monta a aplicação compondo as peças definidas em outros lugares. É este arquivo (mais especificamente o objeto `app` dentro dele) que será apontado ao executar o servidor.

* **`__init__.py`:** Arquivo vazio (ou quase vazio) apenas para indicar que `app` é um pacote Python. Não há necessidade de colocar lógica aqui, mas você poderia usar para configurar importações globais se desejado (não é obrigatório; manter vazio para simplicidade é ok).

#### Diretório `app/core/` (Configuração Central)

O pacote `app/core` contém módulos de configuração e utilitários fundamentais para a aplicação. São componentes de baixo nível ou transversais, que normalmente são usados por várias partes do sistema. Detalhes dos arquivos dentro de `core/`:

* **`core/config.py`:** Módulo de **configurações da aplicação**. Aqui definimos classes e objetos que carregam variáveis de configuração a partir do ambiente (por exemplo, utilizando `pydantic_settings.BaseSettings`). Em um típico projeto FastAPI, este arquivo define uma classe `Settings` com atributos para cada configuração necessária (ex.: `APP_NAME`, `DEBUG`, `DATABASE_URL`, credenciais de APIs, etc.). A classe `Settings` carrega valores do arquivo `.env` por padrão. Exemplo simplificado do conteúdo:

  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      app_name: str = "FastAPI Clean Architecture DDD Template"
      debug: bool = False
      database_url: str  # etc., outros campos de configuração...
      class Config:
          env_file = ".env"

  settings = Settings()
  ```

  Assim, outras partes do código podem importar `settings` para acessar configurações (e.g., `settings.database_url`). Esse padrão centraliza todas as configurações da aplicação num só lugar e facilita alterar comportamentos via variável de ambiente sem mudar código. Lembre-se de manter segredos (e.g., secret keys) apenas no .env e não commitá-los.

* **`core/database.py`:** Módulo responsável por configurar a conexão com banco de dados ou outros recursos de dados persistentes. Por exemplo, se usamos SQLAlchemy, aqui poderíamos instanciar o engine de conexão usando a URL do banco das configs (`settings.database_url`), criar uma sessão (sessionmaker) e fornecer funções utilitárias para obter a sessão (a serem usadas como dependência no FastAPI). Se não usamos banco relacional, este módulo pode ajustar conexão com um banco NoSQL, ou se a aplicação é focada em IA talvez gerencie conexão com um vetor de embeddings, etc. Em suma, é o ponto central para inicializar e compartilhar conexões de dados. Por exemplo:

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from app.core.config import settings

  engine = create_engine(settings.database_url)
  SessionLocal = sessionmaker(bind=engine)

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

  Em contextos sem banco de dados, este arquivo pode permanecer mínimo ou vazio, mas está preparado para integrar persistência de forma limpa.

* **`core/logging.py`:** Define a configuração global de **logging** da aplicação. Antes de inicializar o servidor, queremos configurar como os logs serão formatados e qual nível de detalhe será exibido (info, debug, error, etc.). Neste arquivo, usamos o módulo padrão `logging` do Python para configurar handlers, formatters e levels. Por exemplo, podemos definir um formato unificado de log, ou integrar a lib `loguru` se preferir. No start da app (em `app.py`), chamamos a função de setup do logging para aplicar essas configurações. Um possível conteúdo:

  ```python
  import logging

  LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  def setup_logging():
      logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
      # ... configurações adicionais, se necessárias
  ```

  Dessa forma, ao iniciar a aplicação, chamamos `setup_logging()` e garantimos logs bem formatados e no nível correto. Manter uma boa configuração de log é crucial para depuração e monitoramento em produção.

* **`core/security.py`:** Módulo para funcionalidades de segurança **comuns** da aplicação. Por exemplo, podemos definir aqui utilitários para hash de senhas, geração e verificação de tokens JWT, configuração de políticas de CORS, contextos de autenticação, etc. A ideia é centralizar aspectos de segurança que possam ser usados em múltiplos módulos.

  * Se a aplicação requer autenticação de usuários, esse arquivo pode conter funções para criar/verificar tokens JWT (e.g., usando `python-jose` ou similar), funções para criptografar/verificar senha (e.g., usando `passlib`).
  * Também pode definir credenciais de OAuth ou escopos de autorização.

  **Observação:** A autenticação/autorização específica de cada rota ou módulo pode ser configurada nos *routers* (camada de Presentation), mas as funções genéricas de suporte (como verificar assinatura de token, obter usuário atual a partir do token, etc.) podem residir aqui no core. Assim, evitamos repetição e usamos as mesmas funções de segurança em todo o projeto.

Em resumo, o `app/core/` abriga código que é transversal e agnóstico de domínio específico, servindo de alicerce para a aplicação como um todo.

#### Diretório `app/modules/` (Módulos de Funcionalidade)

Este diretório é onde organizamos o código por **funcionalidade ou contexto de domínio**. Cada subpasta dentro de `modules` representa um **módulo** ou **bounded context** da aplicação, encapsulando lógica de domínio, casos de uso, interfaces e detalhes de infraestrutura relacionados a aquela funcionalidade.

Por exemplo, poderíamos ter módulos como `users`, `orders`, `payments`, `recommendation`, etc., cada um contendo suas entidades, use cases, repositórios, rotas, etc. No nosso template, temos um módulo de exemplo chamado **`example/`** que demonstra a estrutura. Novos módulos a serem criados no futuro devem seguir o mesmo padrão de organização interna.

Estrutura de um módulo típico (usando o módulo `example` como modelo):

##### Módulo de Exemplo: `app/modules/example/`

O módulo **example** foi gerado para servir de referência e ponto de partida. Ele implementa a arquitetura sugerida dentro de um domínio fictício "example". Dentro dele, há subpastas para cada camada lógica do módulo:

* **application/** – Camada de aplicação (casos de uso e interfaces).
* **domain/** – Camada de domínio (entidades e lógica de negócio).
* **infrastructure/** – Camada de infraestrutura (detalhes de persistência, APIs externas, etc).
* **presentation/** – Camada de apresentação (endpoints FastAPI, schemas de request/response, injeção de dependências).

Cada subpasta contém arquivos específicos conforme descrito abaixo:

###### Domain (Domínio)

Esta subpasta define o núcleo de regras de negócio do módulo. Os arquivos aqui descrevem **o que** são os conceitos principais do domínio e como eles se comportam, sem nenhuma dependência de detalhes externos (banco de dados, FastAPI, etc).

* **`entities.py`:** Define as **Entidades de Domínio** do módulo. Entidades são classes ou estruturas que representam os objetos fundamentais do negócio com os quais o módulo lida, incluindo seus atributos e possivelmente lógica básica interna. Por exemplo, num módulo de usuários poderíamos ter uma entidade `User` com atributos como id, nome, email, e métodos para verificar senha ou alterar perfil. As entidades devem encapsular invariantes e regras simples relacionadas a si mesmas.

  Em Python, entidades podem ser implementadas como classes normais ou até dataclasses, dependendo da necessidade. O importante é que elas não dependem de como são armazenadas ou exibidas – são apenas modelos de negócio. No contexto de IA, se este módulo envolvesse por exemplo um "Modelo de IA" ou "Dataset", poderiam ser entidades também (representando configurações ou estado desses objetos).

* **`value_objects.py`:** (Objetos de Valor) Contém definição de tipos ou classes que representam valores do domínio que possuem lógica ou invariantes próprias, mas não têm identidade única como as entidades. Em Domain-Driven Design, **Value Objects** são imutáveis e comparados por valor, não por identidade.

  Exemplos comuns: um CPF, um Email, uma moeda/quantia monetária, coordenadas, etc., que você queira representar com sua própria classe para garantir formatação ou validação. Neste arquivo você pode definir classes para esses valores específicos, encapsulando verificações (por exemplo, classe `Email` que valida formato no construtor). No módulo example, poderíamos ter algo como um `Score` ou outro VO demonstrativo.

  Manter objetos de valor separados ajuda a tornar o código mais expressivo e garantir integridade dos dados do domínio. Se o seu domínio não tem objetos de valor complexos, este arquivo pode ficar vazio ou ser omitido, mas a estrutura está pronta caso precise.

* **`services.py`:** (Serviços de Domínio) Este arquivo reúne **lógicas de domínio complexas** que não cabem dentro de uma única entidade ou dizem respeito à interação entre múltiplas entidades. Domain Services são funções ou classes que implementam regras de negócio usando entidades e value objects, mas que não pertencem exclusivamente a nenhuma entidade específica.

  Por exemplo, no domínio financeiro, poderíamos ter um serviço de domínio para calcular juros ou validar uma transação entre duas contas (envolvendo duas entidades `Conta`). No contexto de IA, poderia haver um serviço de domínio para executar um pipeline de inferência ou combinar resultados de múltiplos modelos, se isso for considerado parte do domínio e não apenas infra.

  Esses serviços de domínio *ainda assim não devem ter acesso a infraestrutura*. Ou seja, eles operam em objetos do domínio que foram carregados em memória (provavelmente pelos repositórios) e aplicam lógica pura sobre eles. Se precisam obter dados de fora ou salvar resultados, eles devem receber esses dados via parâmetros ou retornar resultados para que camadas superiores (aplicação) persistam.

  Resumindo, coloque em `services.py` regras de negócio que envolvam lógica mais elaborada ou múltiplos objetos, mantendo o código das entidades enxuto.

###### Application (Aplicação)

A subpasta `application` implementa os **casos de uso (use cases)** do módulo e define **interfaces (portas)** que conectam a camada de aplicação com outras camadas. Esta camada orquestra as ações necessárias para realizar operações solicitadas pelo mundo exterior (ex: um endpoint da API), coordenando entidades, chamando serviços de domínio e utilizando repositórios (interfaces).

* **`interfaces.py`:** Define as **interfaces abstratas** ou contratos que a camada de aplicação espera para realizar certas tarefas de infraestrutura. Normalmente, as principais interfaces aqui são os **Repositórios** de dados do domínio.

  Por exemplo, se o domínio `example` precisa ler e gravar objetos de uma base de dados, aqui definimos uma interface abstrata para o repositório (e.g., `class ExampleRepositoryInterface(ABC): ...`) com métodos como `listar_objetos()`, `obter_por_id(id)`, `salvar(objeto)` etc. Essas interfaces podem ser classes abstratas usando `abc.ABC` e `@abstractmethod` ou **protocolos** do Python 3.8+ (`typing.Protocol`) descrevendo os métodos esperados. O domínio/aplicação então dependerá dessa interface, sem saber qual implementação concreta será usada.

  Além de repositórios, aqui podem ser definidas interfaces para outros serviços externos que a aplicação use, por exemplo: interface para um serviço de envio de e-mail, interface para um provider de IA (se quiserem abstrair chamadas a modelos externos), etc. Qualquer coisa que a lógica de aplicação precise chamar, mas que é um detalhe de infra, pode ser formalizada como interface nesta camada.

  Ao isolar as interfaces aqui, aplicamos o princípio da **Dependency Inversion**: a camada de aplicação define o contrato, e a implementação concreta virá da infraestrutura (invertendo a dependência). Isso permite facilmente trocar a implementação (por exemplo, usar um repositório em memória para testes e um repositório real SQL em produção, ambos cumprindo a mesma interface).

* **`use_cases.py`:** Contém a implementação dos **Use Cases** (casos de uso) do módulo. Cada caso de uso representa uma ação ou funcionalidade específica que o sistema fornece, agregando a lógica necessária para realizá-la.

  Use cases podem ser implementados de diferentes formas:

  * Como **funções** simples (quando a lógica é pequena).
  * Como **classes** (por exemplo, uma classe por caso de uso, com um método `execute()` ou tornando a classe chamável via `__call__`). Essa abordagem de classe é útil se o caso de uso precisa injetar um repositório via construtor e depois executá-lo.

  Por exemplo, suponha que o módulo example seja responsável por gerenciar "foo". Poderíamos ter um caso de uso `CriarFoo` e outro `ListarFoo`. Em código, poderíamos ter:

  ```python
  from app.modules.example.domain.entities import Foo
  from app.modules.example.application.interfaces import FooRepositoryInterface

  class FooUseCase:
      def __init__(self, repo: FooRepositoryInterface):
          self.repo = repo
      
      def CriarFooUseCase(self, dados: dict) -> Foo:
          # Valida e cria entidade
          foo = Foo(**dados)
          # Regras de negócio (chamar serviços de domínio se necessário)
          # ...
          # Persistir usando o repositório
          foo_salvo = self.repo.salvar(foo)
          return foo_salvo
  
      def ListarFooUseCase(self) -> list[Foo]:
            # Obtém todos os Foo do repositório
            return self.repo.listar()
  ```

  Nesse exemplo, o use case `FooUseCase` recebe uma implementação de repositório via injeção (no construtor) e a utiliza para armazenar a entidade criada. Ele próprio coordena a criação da entidade e aplicação de regras. O mesmo estilo se aplica a casos de uso de leitura: obter dados do repo, possivelmente aplicar alguma regra (ex: filtrar, ordenar, calcular algo) e retornar o resultado.

  O importante é que **Use Cases não sabem nada de HTTP, JSON ou detalhes de API** – isso é tratado na camada de apresentação. Eles recebem e retornam objetos de domínio (ou estruturas Python puras) e podem levantar exceções de negócio se algo impede a execução (ex: "Foo já existe", "Dados inválidos" etc.), que a camada de apresentação transformará em respostas HTTP adequadas.

  Em `use_cases.py` podemos ter múltiplos use cases implementados. Se o arquivo ficar muito grande, uma boa prática é subdividir por funcionalidade (ex: um arquivo por caso de uso complexo, ou agrupar alguns relacionados). Mas inicialmente, o template deixa um arquivo único para simplificar.

###### Infrastructure (Infraestrutura)

A subpasta `infrastructure` do módulo contém as implementações concretas dos detalhes de tecnologia necessários para o módulo, seguindo as interfaces definidas na camada de aplicação. Aqui lidamos com persistência, chamadas externas e qualquer coisa que envolva recursos externos ou detalhes de framework.

* **`models.py`:** Define os **modelos de dados de infraestrutura**, tipicamente modelos de banco de dados ou mapeamentos ORM. Por exemplo, se utilizamos **SQLAlchemy**, este arquivo pode declarar classes de modelo do SQLAlchemy correspondentes às entidades de domínio, com suas tabelas, colunas e relacionamentos. Às vezes, as entidades de domínio podem coincidir em estrutura com os modelos de banco, mas não é obrigatório – podemos ter diferenças (por exemplo, campos técnicos no modelo de banco que não existem na entidade, ou vice-versa).

  Exemplo (usando SQLAlchemy ORM):

  ```python
  from sqlalchemy import Column, Integer, String
  from app.core.database import Base

  class FooModel(Base):
      __tablename__ = "foo"
      id = Column(Integer, primary_key=True, index=True)
      nome = Column(String, index=True)
      descricao = Column(String)
      # etc...
  ```

  Onde `Base` seria a classe base declarativa do SQLAlchemy importada de `core/database.py`. Esses modelos são utilizados por repositórios para realizar operações CRUD. Se você usar outro tipo de persistência (por exemplo, ODM para Mongo, ou mesmo acesso direto via bibliotecas de client), pode não ter um "models.py" formal, mas ainda assim terá representações de dados específicas da infra aqui (por exemplo, esquemas do Mongo, ou mapeamento para documentos JSON, etc).

  Em cenários de IA, `models.py` poderia conter classes para interagir com um modelo de ML pré-treinado ou endpoint, mas geralmente isso seria mais um serviço do que um modelo de dado. Nesse caso, você poderia criar classes de infraestrutura para encapsular chamadas a modelos de IA externos (ex: OpenAI API) – essas classes poderiam residir aqui ou em `repositories.py` dependendo de como você categoriza (são repositórios de conhecimento? ou serviços externos? Pode tratá-los similarmente).

* **`repositories.py`:** Contém as **implementações concretas dos repositórios** definidos em `application/interfaces.py`. Aqui escrevemos classes (ou funções) que acessam a fonte de dados real para recuperar ou salvar informações.

  Continuando o exemplo do Foo, se em `interfaces.py` definimos `FooRepositoryInterface` com certos métodos, em `repositories.py` teremos a classe `FooRepository` (implementando `FooRepositoryInterface`) que realiza as operações reais usando o banco de dados ou outro meio.

  Exemplo:

  ```python
  from app.modules.example.application.interfaces import FooRepositoryInterface
  from app.modules.example.infrastructure.models import FooModel
  from app.core.database import SessionLocal

  class FooRepository(FooRepositoryInterface):
      def __init__(self, db_session=None):
          self.db = db_session or SessionLocal()

      def listar(self) -> list[Foo]:
          results = self.db.query(FooModel).all()
          # Mapear FooModel (ORM) para entidade Foo (de domain.entities)
          return [Foo.from_model(m) for m in results]

      def obter_por_id(self, id: int) -> Foo | None:
          model = self.db.query(FooModel).get(id)
          return Foo.from_model(model) if model else None

      def salvar(self, foo: Foo) -> Foo:
          model = FooModel.from_entity(foo)
          self.db.add(model)
          self.db.commit()
          self.db.refresh(model)
          return Foo.from_model(model)
  ```

  *(Nota: métodos `from_model` e `from_entity` seriam métodos utilitários para converter entre entidade de domínio e modelo ORM, que você pode implementar para manter o domínio separado da camada ORM.)*

  Nesse exemplo, o repositório recebe uma sessão de banco de dados (que podemos obter via `app.core.database.SessionLocal`). No FastAPI, usaremos a injeção de dependência para fornecer uma sessão por requisição (veja `dependencies.py` na camada de apresentação). O repositório realiza a consulta ou persiste os dados e retorna objetos do domínio.

  Se a aplicação for usar um banco de dados diferente ou uma API externa, este repositório poderia chamar os endpoints apropriados, parsear a resposta e transformar em entidades de domínio. Por exemplo, se `example` fosse um módulo que busca dados de um serviço externo, o repositório pode usar `httpx` (já incluso via `fastapi[standard]`) para fazer requests e depois montar entidades.

  **Importante:** O repositório faz parte da infraestrutura, então ele pode e deve conhecer tanto os modelos de infra (`FooModel`, ou detalhes de API externa) quanto as entidades de domínio (`Foo`). Ele atua como um adaptador que converte entre os dois mundos. A lógica aqui deve ser limitada a operações de dados (consultas, conversões), não regras de negócio (estas ficam no domínio/aplicação).

###### Presentation (Apresentação)

A subpasta `presentation` define como o módulo expõe as suas funcionalidades para o "mundo exterior", no caso via uma API web (FastAPI). Aqui moram os **routers** (controladores) com os endpoints HTTP, os **schemas** Pydantic para validação/serialização e as **dependências** específicas do módulo (por exemplo, provedores de repositório ou de autenticação para uso nos endpoints).

* **`routers.py`:** Define as rotas (endpoints) da API referentes a este módulo. Geralmente, criamos um objeto `router = APIRouter()` e decoramos funções Python com verbos HTTP (@router.get, @router.post, etc.) para cada endpoint necessário.

  Cada função de endpoint deve lidar com:

  * Receber entradas (path params, query params, body) já validadas (usando os schemas, ver abaixo).
  * Obter instâncias necessárias via dependências (por exemplo, obter um repositório ou o usuário atual autenticado).
  * Chamar o caso de uso apropriado na camada de aplicação, passando os dados necessários.
  * Tratar exceções de negócio lançadas pelos use cases (por ex., converter uma exceção de "não encontrado" em um HTTP 404, ou erro de validação em 400).
  * Retornar o resultado (convertendo para schema de saída se for objeto complexo, ou simplesmente retornando tipos básicos que FastAPI converterá automaticamente).

  Por exemplo, suponha um endpoint GET para listar Foos:

  ```python
  from fastapi import APIRouter, Depends, HTTPException
  from app.modules.example.presentation.schemas import FooOut
  from app.modules.example.application.use_cases import ListarFoosUseCase
  from app.modules.example.presentation.dependencies import get_foo_repository

  router = APIRouter(prefix="/foo", tags=["Foo"])

  @router.get("/", response_model=list[FooOut])
  def listar_foos(repo = Depends(get_foo_repository)):
      use_case = ListarFoosUseCase(repo)
      foos = use_case.execute()
      return foos  # FastAPI converterá cada Foo via FooOut schema
  ```

  Nesse pseudo-código:

  * Usamos `Depends(get_foo_repository)` para injetar uma instância do repositório concreto (definido em `infrastructure`) conforme a interface esperada.
  * Instanciamos o caso de uso `ListarFoosUseCase` fornecendo o repositório.
  * Executamos e obtemos o resultado (lista de entidades `Foo`).
  * Retornamos essa lista; FastAPI vai usar o `response_model` `list[FooOut]` para filtrar e serializar a resposta conforme definido no schema.
  * Tratamento de erros: se `execute()` lançasse alguma exceção, poderíamos capturá-la e lançar `HTTPException` correspondente.

  O arquivo `routers.py` pode conter múltiplas rotas (GET, POST, PUT, DELETE) de acordo com as operações suportadas pelo módulo. Se as rotas forem muitas, podemos subdividir em múltiplos arquivos (ex: `routers_public.py`, `routers_admin.py`) e incluir todos em um APIRouter principal, mas no template mantemos um único arquivo para simplicidade.

  Finalmente, no `app.py`, o roteador do módulo example seria incluído na app principal:

  ```python
  from app.modules.example.presentation.routers import router as example_router
  app.include_router(example_router)
  ```

  possivelmente com um prefixo (por ex., `/api/v1` global, ou prefixos específicos se desejado).

* **`schemas.py`:** Define os **Schemas Pydantic** usados para validar e serializar os dados nas entradas e saídas dos endpoints da API desse módulo. Pydantic (v2, integrada via FastAPI) permite criar classes modelo que representam a estrutura dos dados esperados/retornados em JSON, com validação de tipos automática.

  Tipicamente teremos:

  * **Schemas de Entrada** (Input): representam o corpo de requisições POST/PUT, ou parâmetros mais complexos. Ex.: `FooCreate` com os campos necessários para criar um Foo.
  * **Schemas de Saída** (Output): representam como a entidade será exposta na API. Ex.: `FooOut` contendo campos a serem retornados ao cliente (geralmente equivalentes aos da entidade, exceto segredos ou campos desnecessários).

  Em FastAPI, usamos esses schemas nas funções de rota: parâmetros de função para body (e.g., `foo: FooCreate` será automaticamente populado e validado) e `response_model=FooOut` para conversão de resposta.

  No módulo example, poderíamos ter no `schemas.py` algo como:

  ```python
  from pydantic import BaseModel

  class FooBase(BaseModel):
      nome: str
      descricao: str

  class FooCreate(FooBase):
      pass  # Mesmo campos por enquanto, mas separado caso futuramente haja diferença

  class FooOut(FooBase):
      id: int

      class Config:
          from_attributes = True  # Permite criar FooOut a partir de objeto ORM ou dataclass com atributos correspondentes
  ```

  Aqui definimos um schema base com campos compartilhados, um de criação (igual ao base neste caso) e um de saída incluindo o id. O `from_attributes = True` é uma configuração do Pydantic v2 que permite converter automaticamente a partir de objetos que tenham atributos com os mesmos nomes (útil quando retornamos entidades do domínio ou modelos ORM; o FastAPI/Pydantic consegue extrair os dados).

  Os schemas servem como contrato da API – eles documentam e validam o formato esperado. Mantenha-os atualizados conforme o domínio evolui, mas não inclua aqui campos que não deveriam ser expostos (por exemplo, senhas, segredos, etc.).

* **`dependencies.py`:** Define **funções de dependência** do FastAPI específicas do módulo. Essas funções usam o sistema de **Dependency Injection** do FastAPI (`fastapi.Depends`) para fornecer objetos prontos para os endpoints, mantendo o código das rotas mais limpo e desacoplado da criação desses objetos.

  As dependências comuns definidas aqui incluem:

  * **Obtenção de repositórios ou serviços**: por exemplo, `def get_foo_repository():` que instancia e retorna um `FooRepository` (da infraestrutura). Poderia também gerenciar a sessão de DB (ex: criando uma instância de repositório já amarrada a uma sessão do SQLAlchemy obtida de `core/database.get_db()`).
  * **Autenticação/autorização**: por exemplo, `def get_current_user()` que verifica o token JWT presente no header Authorization (usando funções de `core/security.py`) e retorna o usuário atual ou lança exceção 401. Embora isso possa ser reutilizado globalmente, se for específico do módulo, pode residir aqui.
  * Qualquer outra lógica de preparação de argumentos para endpoints: por exemplo, verificar se uma entidade existe antes de entrar no endpoint (carregando do repo e injetando, ou lançando 404 se não).

  Em nosso exemplo, um `get_example_repository` simples:

  ```python
  from app.modules.example.infrastructure.repositories import FooRepository
  from app.core.database import get_db

  def get_foo_repository(db=Depends(get_db)):
      return FooRepository(db_session=db)
  ```

  Assim, o FastAPI primeiro resolverá `get_db` (que provavelmente fornece uma sessão de banco por requisição), depois passa essa sessão para `FooRepository` e retorna a instância. A função de rota então recebe já um `FooRepository` pronto, sem saber de detalhes de criação.

  O uso de `dependencies.py` promove reuso e centralização: se quisermos mudar como obtemos o repositório (por exemplo, trocar por implementação fake em testes, ou adicionar caching), fazemos em um só lugar. Além disso, facilita testes das rotas, pois podemos sobrepor Dependencias no TestClient do FastAPI se necessário.

Resumindo a estrutura de um **módulo**: a camada **Presentation** (routers) recebe a requisição e utiliza **Dependencies** para obter instâncias de **Repositories** (Infra), então cria um **Use Case** (Application) para executar a lógica usando **Entidades/Serviços** (Domain) e possivelmente salvando/consultando via repositório, retornando o resultado que o router envia de volta ao cliente. Cada parte faz sua responsabilidade e fica relativamente isolada.

### Diretório `docs/` (Documentos)

A pasta `docs/` é destinada a armazenar **documentações externas** do projeto. Aqui podem ser colocados arquivos como PDF, documentos de especificação, requisitos, diagramas, notas de design, ou qualquer outro artefato de documentação que seja útil manter junto ao repositório de código, mas que não faz parte do código em si.

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

Este template já vem com algumas dependências Python instaladas e pré-configuradas, conforme definidas no `pyproject.toml` e `uv.lock`. Aqui um resumo das principais:

* **FastAPI (v0.115.13)** – Framework web ASGI moderno e de alta performance, ideal para construir APIs RESTful e integrar componentes de IA facilmente. Utilizamos a instalação `fastapi[standard]`, que inclui extras úteis:

  * **Starlette (v0.46.2):** framework ASGI subjacente ao FastAPI, lida com roteamento, middleware, WebSocket, etc.
  * **Uvicorn (v0.34.3):** servidor ASGI de alta performance incluído via extra "standard", usado para executar a aplicação.
  * **Email-validator, python-multipart, itsdangerous, PyYAML, httptools, websockets, etc.:** várias libs que vêm no `[standard]` para dar suporte a recursos de formulario, uploads, WebSockets e outras funcionalidades do FastAPI.
  * **FastAPI-CLI (v0.0.7):** ferramenta de linha de comando para gerenciar apps FastAPI (já inclusa), permitindo por exemplo rodar `python -m fastapi serve` para subir a API. (Opcional, uvicorn direto também funciona.)
  * **HTTPX (v0.28.1):** cliente HTTP async poderoso, usado se precisarmos chamar APIs externas (por exemplo, consumir um serviço de IA). Já está incluso via dependência do fastapi\[standard].
  * **Jinja2 (v3.1.6):** mecanismo de templates, incluso pelo Starlette (pode ser útil para gerar emails HTML, por exemplo).
* **Pydantic (v2.11.7):** Biblioteca para validação de dados e criação de modelos, base para os schemas do FastAPI. A versão 2 traz desempenho otimizado via pydantic-core. Usamos também **pydantic-settings (v2.10.0)** para lidar com configurações (carregar .env).
* **UV (Astral)** – Gerenciador de pacotes e ambientes. Permite criar o virtualenv `.venv`, resolver dependências (uv.lock) e executar comandos isolados. É uma alternativa moderna a pip/pipenv/poetry, trazendo velocidade e facilidade. (Ver próxima seção para detalhes de uso.)
* **Ruff (v0.12.0)** – Linter para manter qualidade de código. Está incluído no grupo de dependências de desenvolvimento (`[tool.ruff]` no pyproject se configurado). Ele checa PEP8, erros comuns e até faz algumas auto-correções. Use-o regularmente para manter o código limpo.
* *(Outras possíveis dependências não listadas aqui podem ser adicionadas conforme necessidade do projeto. Ex: bibliotecas de IA como TensorFlow/PyTorch, ou ORMs como SQLAlchemy, ou outros utilitários.*)

A **estrutura de dependências pré-instalada** pode ser visualizada de forma hierárquica conforme o `uv lock` gerou, mas o importante é saber que as principais ferramentas (FastAPI, Pydantic, etc.) já estão disponíveis. Se precisar adicionar novas libs, use o comando `uv add nome_da_lib` que ele cuidará de atualizar pyproject e uv.lock.

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

Para quem prefere ou precisa rodar em contêiner (ou preparar para produção), este projeto fornece suporte a Docker:

* **Construção da imagem Docker:** Certifique-se de ter Docker instalado. No diretório do projeto, rode:

  ```bash
  docker build -t fastapi-clean-architecture-ddd-template:latest .
  ```

  Isso vai usar o **Dockerfile** fornecido. Ele provavelmente executa passos como:

  * Usar uma imagem base (por exemplo, `python:3.13-slim`).
  * Copiar `pyproject.toml` e `uv.lock`, instalar dependências (isso aproveita o cache do Docker se não alteramos deps).
  * Copiar o restante do código.
  * Definir a variável de env `PYTHONPATH=/app` (se o código for copiado para /app).
  * Executar `uvicorn app.app:app` como entrypoint (às vezes via `CMD`).

  Ao terminar, você terá uma imagem local chamada `fastapi-clean-architecture-ddd-template:latest`.

* **Execução via Docker isolado:** Rode um container da imagem:

  ```bash
  docker run -d --env-file .env -p 8000:8000 fastapi-clean-architecture-ddd-template:latest
  ```

  Isso vai rodar em segundo plano (`-d`), carregando as variáveis do seu `.env` local para dentro do container, e mapeando a porta 8000 do container para 8000 local. Novamente, acesse [http://localhost:8000/docs](http://localhost:8000/docs) para ver se está de pé.

  *Nota:* Use `docker logs <container_id>` para ver os logs, e `docker stop` para parar quando quiser.

* **Docker Compose (desenvolvimento multi-serviço):** O arquivo `docker-compose.yaml` facilita subir a aplicação junto com outros serviços (caso necessários). Por exemplo, se o projeto exigir um banco de dados PostgreSQL e talvez um Redis, poderíamos definir no compose. Você pode editar o compose para adicionar:

  ```yaml
  services:
    api:
      build: .
      env_file: .env
      ports:
        - "8000:8000"
    db:
      image: postgres:15
      environment:
        POSTGRES_USER: myuser
        POSTGRES_PASSWORD: mypass
        POSTGRES_DB: mydb
      ports:
        - "5432:5432"
  ```

  (Isso é um exemplo; no template real pode não estar preenchido.)

  Então executar:

  ```bash
  docker-compose up --build
  ```

  Isso compilaria a imagem e iniciaria tanto `api` quanto `db`. A aplicação poderia ler as variáveis de ambiente definidas (como `DATABASE_URL=postgresql://myuser:mypass@db:5432/mydb` apontando para o container `db`).

  O Compose é muito útil para desenvolvimento, pois você pode espelhar o ambiente de produção localmente. Lembre de desligar com `docker-compose down` quando não usar.

* **Hot-reload no Docker dev:** Em desenvolvimento, você pode querer que o container reflita mudanças de código sem reconstruir a imagem toda hora. Para isso, pode mapear volumes no compose (montar o código host dentro do container) e executar uvicorn em modo reload dentro do container. Ajustes extras seriam necessários no Dockerfile (como instalar uvicorn\[standard] no container se não estiver, já está via fastapi\[standard]) e no compose (montar `./app` para `/app/app`). Isso não está configurado out-of-the-box, mas pode ser feito se desejado.

Usar Docker no desenvolvimento é opcional – você pode perfeitamente usar apenas uv + venv local. Porém, para padronizar ambientes ou se alguém roda Windows e prefere container Linux para alinhamento, está disponível.

Em produção, usar a imagem Docker resultante facilita deploys (k8s, ECS, etc.), lembrando de configurar adequadamente variáveis de env de produção e ajustes de segurança/performance (como rodar uvicorn sem `--reload`, possivelmente com mais workers, etc.).

## Considerações Finais

Este README buscou cobrir **todos os aspectos da arquitetura** do projeto **fastapi-clean-architecture-ddd-template**, incluindo a finalidade de cada pasta/arquivo e as práticas recomendadas para implementação e manutenção. Recapitulando alguns pontos principais:

* A arquitetura segue princípios de **Clean Architecture**, separando domínio, aplicação, infraestrutura e apresentação, o que torna o código mais modular, testável e resiliente a mudanças.
* Cada módulo de funcionalidade dentro de `app/modules` é estruturado internamente de forma consistente, facilitando que novos módulos sejam adicionados seguindo o mesmo modelo do módulo de exemplo.
* Arquivos de configuração central (`core`) permitem gerenciar aspectos transversais (config, db, logging, security) de modo único.
* O gerenciamento de dependências via **uv** assegura reprodutibilidade e facilidade em atualizar pacotes, enquanto ferramentas de qualidade como **Ruff** mantêm o código padronizado.
* O template já provê integração com Docker, .env para configurações, e estrutura de testes – aproveitando isso, deve-se sempre escrever testes ao adicionar funcionalidades, e garantir que rodam todos verdes antes de integrar mudanças.
* **Boas práticas** de código (PEP8, documentação, type hints, divisão de responsabilidades) são encorajadas para que o projeto se mantenha limpo e compreensível conforme cresce.
* Para qualquer dúvida, volte a este documento 😉. Ele deve servir como referência contínua. Se algo não estiver claro aqui, é um indicativo de que devemos aprimorar ainda mais a documentação.

Com esse template em mãos, a equipe pode iniciar novos projetos de forma mais rápida e uniforme, focando na lógica específica da aplicação, pois os alicerces (estrutura e configurações básicas) já estão preparados. Sinta-se à vontade para ajustar detalhes conforme as necessidades específicas do projeto, mas **mantenha a consistência** – isso facilitará onboarding de novos devs e troca de código entre projetos irmãos que usem o mesmo template.

Bom desenvolvimento! 🚀 E lembre-se: uma arquitetura bem definida é um guia, mas deve sempre servir ao propósito do software. Utilize-a com flexibilidade e bom senso. Qualquer contribuição ou melhoria ao template em si pode ser discutida com o time para evoluirmos nossa base padrão continuamente. Boa codificação!
