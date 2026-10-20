# ZÁVIA v1.9 — Auditoria técnica e validação pré-vendas

## Correções implementadas no código
- Sair da conta no cabeçalho + botão visível em Minha Conta, sempre via POST com CSRF.
- Página de detalhes de cada pedido e solicitação de cancelamento pelo cliente (não é cancelamento automático da cobrança).
- Admin: status em preparação, enviado, entregue (respeitam transições), registro de reembolso SOMENTE após a InfinitePay confirmar; código de rastreio/formato de entrega.
- Admin: cancelamento de pedidos não pagos por ação já existente após 24h do vencimento e checagem manual na InfinitePay; repõe estoque uma única vez.
- Eventos de auditoria para compra, pagamento confirmado, expedição, entrega e cancelamento conferido.
- Notificações transacionais com fila e tentativas opcionais por Apps Script (sem custo de plataforma, dependente da conta Google). Desligadas até a configuração. Sem envio automático de reembolso não confirmado.
- Sem mudanças na identidade, produtos reais, fotos, frete fixo, cadastro, estrutura do checkout ou banco existente. Migração 0007 ADITIVA.

## O que a auditoria encontrou e NÃO pode afirmar como validado
- **Pagamentos**: apenas redirecionamento foi demonstrado pelo usuário. Ainda é necessário executar PIX real controlado e verificar a atualização do pedido por webhook e `payment_check`, inclusive após retorno da cliente.
- **Cancelamento de cobrança**: a API de checkout não garante que apagar um pedido local cancele um link/estorne pagamento. A v1.9 registra a solicitação do cliente e oferece fluxo manual auditável; cancelar/estornar ainda deve ser feito/verificado na InfinitePay.
- **Webhook de reembolso**: o código continua sem conciliação automática de eventos `refunded`/`canceled`. A situação pode ser registrada manualmente depois da conferência externa. Não afirmar que esses status estejam automatizados.
- **Reservas abandonadas**: permanecem em revisão/soltura manual com carência, pois expiração não prova ausência de pagamento.
- **Banco gratuito Render**: serviço free pode expirar e não fornece backups automáticos; migrar para banco com backups comprovados ANTES de operações reais de clientes. Fotografias no PostgreSQL consomem armazenamento.
- **Login / abuso**: faltam rate limiting distribuído, verificação de e-mail e reset por e-mail configurado. Não declarar segurança de produção totalmente homologada.
- **E-mail**: o módulo é opcional. Exige Apps Script autorizado e configurações privadas. Sem integração não dispara. Falhas podem precisar de reenvio manual.
- **Regulatório**: conferir endereço/identificação comercial, política de trocas e devoluções, LGPD, impostos, prazo real de entrega e canal de atendimento.
- **Testes**: Django não pôde ser instalado neste ambiente isolado sem internet. Rodar GitHub Actions, `manage.py check`, migrações PostgreSQL e fluxo real no Render; não declarar 100% antes disso.

## Passos de deploy seguro
1. Guarde tag/commit estável e backup recuperável PostgreSQL; desabilite temporariamente Auto Deploy.
2. Atualize GitHub com todo o ZIP extraído (arquivos na raiz, sem apagar arquivos do projeto).
3. Confira GitHub Actions verde, principalmente novas regressões.
4. No Render, faça deploy manual, verifique migração `0007` e status Live.
5. Com `ZAVIA_CHECKOUT_ENABLED=0` na homologação, teste cadastro, login, sair, carrinho, painel, pedido antigo e solicitar cancelamento.
6. Use Admin > Pedidos para testar transições em registros controlados. Pagamentos: teste real controlado com usuário autorizado e confirme valor exato pela InfinitePay.
7. Configure Gmail Apps Script **se desejar**; mantenha `ZAVIA_EMAIL_ENABLED=0` até a primeira mensagem de teste.
8. Só reabilite checkout e divulgue após backup, condições comerciais, testes de segurança e conciliação.
