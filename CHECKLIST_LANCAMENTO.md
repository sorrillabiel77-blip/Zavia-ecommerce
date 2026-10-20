# ZÁVIA — Checklist antes de divulgar a loja

## Base técnica (precisa de validação prática)

- [ ] Build da v1.7 finaliza em `Live` no Render, sem erro nos logs.
- [ ] Testes automatizados do GitHub Actions passam.
- [ ] Produto real, galeria de fotos, variações e estoque funcionam em desktop e celular.
- [ ] Carrinho preserva os itens válidos e soma o frete fixo corretamente.
- [ ] Cliente faz login, preenche endereço e abre checkout InfinitePay com total correto.
- [ ] Uma transação controlada confirma o pagamento tanto na InfinitePay quanto no pedido ZÁVIA, **sem depender apenas do retorno no navegador**.
- [ ] Pix pendente/expirado, notificações duplicadas, falhas na API e cancelamento foram testados.
- [ ] Reservas não pagas foram conferidas e recuperadas sem disponibilizar estoque de um pagamento válido.
- [ ] Fotos permanecem após novo deploy e backup/restauração de PostgreSQL foram verificados.

## Informação e confiança para compradores

- [ ] Informar titular da operação, dados comerciais/identificação obrigatórios aplicáveis e meios reais de contato.
- [ ] Publicar política de trocas, devoluções e direito de arrependimento conforme legislação brasileira aplicável.
- [ ] Publicar prazos/áreas atendidas pela entrega e informar como funciona o frete fixo.
- [ ] Publicar política de privacidade e orientar tratamento de dados pessoais, inclusive integração de pagamentos.
- [ ] Informar eventuais limites de estoque e condições de promoção sem promessas fictícias.
- [ ] Testar link compartilhado por WhatsApp e favicon. A prévia pode depender do cache dos apps.

Nenhum selo de proteção, avaliação de cliente, benefício de frete ou prazo de entrega foi inventado no layout.
