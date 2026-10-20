# ZÁVIA — auditoria técnica de pré-lançamento v1.9

**Base auditada:** arquivos completos do ZIP v1.8 consolidado, fornecido anteriormente. **Não inclui:** acesso autenticado ao Render, ao banco de produção, ao GitHub Actions ou à conta InfinitePay. O usuário comprovou visualmente que o link InfinitePay abre, mas não a conciliação de uma cobrança paga.

| Área | Achado | Alteração/conduta | Status de validação |
|---|---|---|---|
| Conta da cliente | Sair estava pouco visível no perfil | Botão sair no cabeçalho, POST CSRF; perfil reorganizado | Código e casos de teste preparados |
| Pedidos da cliente | Não havia detalhamento nem solicitação | Detalhes com histórico e POST de cancelamento, sem alterar cobrança | Código e casos de teste preparados |
| Administração | Pedidos tinham status somente leitura, sem fluxo | Ações controladas pago→preparo→enviado→entregue; tracking na edição | Código e casos de teste preparados |
| Cancelar teste | Cancelamento exigia link expirado + carência e conferência externa | Mantida proteção; solicitação visível, status de cancelamento manual e auditado | Necessita teste no provedor e DB |
| Reembolso | Sem ação para registrar estorno | Confirmação administrativa somente após estorno integral no app InfinitePay; nenhum estorno é disparado pelo site | Integração de reembolso **não automática** |
| Pagamento aprovado | Validação payment_check existente | Evento auditado e notificação pendente idempotente em primeira confirmação autenticada | PIX real e webhook ainda não homologados |
| Notificações | Sem emissor configurado | Fila auditável e Gmail Apps Script opcional; desativado | Depende do usuário e testes de envio |
| Estoque | Reserva potencialmente presa após abandono | Procedimento manual anterior preservado, sem baixa indevida | Permanece pendência operacional |
| Fraudes/login | Sem rate limiting e confirmação de e-mail | Identificado, sem solução nesta atualização | Bloqueio para escala pública |
| Persistência | PostgreSQL Render Free e fotos binárias na base | Exigir backup testado e DB persistente para clientes reais | Bloqueio de lançamento confiável |
| Comercial | Política, identificação, frete | v1.8 manteve páginas editáveis; operador deve completar dados reais | Requer validação comercial/legal |

### Como cancelar pedidos de teste antigos

**Pedido não pago:** no Admin, use ação "Cancelar e repor estoque SOMENTE após conferir não pagamento na InfinitePay". A ação exige prazo de expiração do link + 24 horas e confirmação manual de ausência de pagamento; não libera estoque antes dessa checagem.

**Pedido pago:** abra InfinitePay, acesse a venda e faça cancelamento/estorno de acordo com a modalidade e regras do provedor. Só depois use no Admin a ação "REGISTRAR ESTORNO INTEGRAL já confirmado na InfinitePay". O site **não executa** estornos pela API. Para Pix, use a opção oficial de devolução na InfinitePay; reembolso parcial não é abrangido pelo registro integral desta versão.

### Regra de aprovação comercial

Só considerar lançamento após **CI verde**, backup recuperável, teste de compra real com confirmação autenticada e valor correto, nenhuma duplicidade de estoque, teste de cancelamento/reembolso, políticas comerciais preenchidas e canal de atendimento. O código sozinho não comprova nenhuma dessas verificações em produção.
