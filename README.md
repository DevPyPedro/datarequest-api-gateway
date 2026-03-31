# DataRequest API Gateway

Versao atual: `1.1.0`

API responsavel pelo gateway de autenticacao e acesso da plataforma DataRequest, com persistencia de usuarios em PostgreSQL e gerenciamento de sessao em Redis.

## Status atual

O projeto ja possui a base principal de autenticacao implementada e pronta para evolucao.

## Funcionalidades disponiveis

- Cadastro de usuarios
- Login com validacao de senha e codigo de verificacao
- Emissao de `access token`
- Emissao e rotacao de `refresh token`
- Sessao centralizada no Redis
- Revogacao de sessao no logout
- Validacao de usuario autenticado via endpoint protegido
- Geracao de codigo de verificacao por e-mail

## Componentes principais

- `FastAPI` como framework HTTP
- `SQLAlchemy` para acesso ao banco relacional
- `PostgreSQL` para persistencia de usuarios
- `Redis` para controle de sessao e tokens
- `JWT` para autenticacao
- `bcrypt` para hash de senha
- `SMTP` para envio do codigo de verificacao

## Estrutura funcional da autenticacao

- O usuario e armazenado na tabela `user_auth.users`
- O login valida email, senha e codigo de verificacao
- O `access token` representa o acesso de curta duracao
- O `refresh token` permite renovar a autenticacao com duracao maxima de 4 horas por emissao
- Cada sessao fica registrada no Redis com identificador proprio
- O logout remove a sessao do Redis e invalida os tokens associados

## Endpoints atualmente expostos

- `GET /`
  Retorna uma mensagem simples para indicar que a API esta ativa.

- `POST /auth/register`
  Realiza o cadastro de um novo usuario na base `user_auth.users`, aplicando hash seguro na senha antes da persistencia.

- `GET /auth/generate-code`
  Gera um codigo de verificacao temporario, salva esse codigo no Redis e envia o valor por e-mail para o usuario informado.

- `POST /auth/login`
  Executa o fluxo principal de autenticacao: valida existencia do usuario, confere senha, valida o codigo de verificacao e cria uma nova sessao no Redis com `access token` e `refresh token`.
  Recebe os dados de login no corpo da requisicao e retorna `access_token`, `refresh_token` e `token_type`.

- `POST /auth/token`
  Disponibiliza o mesmo comportamento de autenticacao do endpoint de login, retornando os tokens da sessao para integracoes que prefiram uma rota dedicada a emissao de token.
  Recebe os dados de login no corpo da requisicao e retorna `access_token`, `refresh_token` e `token_type`.

- `POST /auth/refresh`
  Recebe um `refresh token` valido, confere a sessao correspondente no Redis, gera um novo `access token`, rotaciona o `refresh token` e atualiza a sessao ativa.
  Recebe `refresh_token` no corpo da requisicao e retorna novo `access_token`, novo `refresh_token` e `token_type`.

- `POST /auth/logout`
  Revoga a sessao autenticada removendo o registro correspondente do Redis, fazendo com que os tokens associados deixem de ser aceitos.
  Recebe o `access token` no header `Authorization: Bearer <token>` e retorna uma mensagem de sucesso apos invalidar a sessao.

- `GET /auth/me`
  Valida o `access token`, confirma que a sessao ainda existe no Redis e retorna os dados basicos do usuario autenticado.

## Observacoes de evolucao

- O projeto ainda pode receber testes automatizados mais amplos para rotas e integracao
- Os arquivos `Dockerfile` e `docker-compose.yaml` ainda nao estao estruturados
- O fluxo atual esta preparado para expansao de politicas de sessao, revogacao e multi-dispositivo
