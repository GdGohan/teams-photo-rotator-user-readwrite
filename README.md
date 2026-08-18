# Teams Photo Rotator — User.ReadWrite

Esta versão usa **permissão delegada `User.ReadWrite`** e altera somente
a foto do usuário que fez login, usando `PUT /me/photo/$value`.

A Microsoft documenta `User.ReadWrite` como permissão suficiente para
atualizar a foto do usuário conectado em uma conta corporativa/escolar,
e indica que essa permissão delegada não requer admin consent por padrão.

## Atenção ao GitHub Actions

`User.ReadWrite` é uma permissão DELEGADA: existe um usuário conectado.
Por isso, o primeiro login é feito pelo fluxo de Device Code.

O GitHub Actions não mantém automaticamente uma sessão interativa.
Depois do primeiro login, o MSAL usa o cache/token de atualização para
obter novos access tokens.

### Configuração

1. Crie um App Registration no Microsoft Entra ID.
2. Copie o **Application (client) ID**.
3. Em Authentication, habilite o fluxo de autenticação público/cliente
   conforme a configuração disponível no seu tenant.
4. Em API permissions, adicione Microsoft Graph > Delegated permissions:
   `User.ReadWrite`.
5. Não crie `client secret` para esta versão.

No GitHub, crie os secrets:

- `MS_CLIENT_ID`
- `MS_TENANT_ID` (opcional; use o Directory/Tenant ID. Se não usar,
  o padrão é `organizations`)
- `MS_TOKEN_CACHE` (será preenchido depois do primeiro login)

## Primeiro teste

1. Vá em Actions.
2. Execute o workflow manualmente.
3. O log exibirá uma mensagem da Microsoft com um código e uma página
   para login.
4. Faça login com sua conta institucional.
5. Se o tenant permitir o consentimento, o script obterá o token e
   atualizará a foto.
6. O log imprimirá `TOKEN_CACHE=...`.
7. Salve somente o valor depois de `TOKEN_CACHE=` no secret
   `MS_TOKEN_CACHE`.

Se aparecer uma mensagem exigindo aprovação do administrador, isso
significa que a política da sua organização bloqueia o consentimento
do usuário para esse aplicativo/permissão.

## Fotos

Coloque JPG/JPEG em `photos/`.

Exemplo:

photos/
  01.jpg
  02.jpg
  03.jpg

O script escolhe uma foto diferente conforme o dia.

## Segurança

- Nunca coloque senha da Microsoft no código.
- Nunca publique o conteúdo de `MS_TOKEN_CACHE`.
- Use um repositório privado.
- Se o token/cache for exposto, remova/revogue o aplicativo/sessão
  conforme as políticas da sua organização.

## Observação

O agendamento do GitHub Actions pode atrasar alguns minutos. O horário
configurado é 12:17 UTC (09:17 em Brasília).
