# ZÁVIA — checklist de lançamento (v1.8)

## Infraestrutura
- [ ] Backup PostgreSQL restaurável feito antes da atualização.
- [ ] Testes GitHub Actions aprovados; Render em `Live` sem erros.
- [ ] Banco com retenção e backups adequados para dados reais (evitar depender do PostgreSQL Free de avaliação).
- [ ] Fotos reais e variações testadas após deploy.

## Dados comerciais editáveis no Admin
- [ ] Nome/razão social, CNPJ quando aplicável e endereço comercial verdadeiro.
- [ ] WhatsApp ou e-mail de atendimento ativo e testado.
- [ ] Horário de atendimento e canal de privacidade.
- [ ] Origem, preparação e prazo/condições reais de entrega por região atendida.
- [ ] Procedimento de trocas e devoluções compatível com a operação e a legislação brasileira.
- [ ] Conferir links de Entregas, Trocas, Privacidade, Atendimento em celular e computador.

## Vendas reais
- [ ] Valor de produtos, variações, estoque e frete revisados.
- [ ] Confirmado pagamento real e notificação por webhook: valores iguais, pedido atualizado uma única vez.
- [ ] Confirmados pagamento pendente, expiração, cancelamento e estorno.
- [ ] Confirmada política de reserva de estoque e rotina de conferência de abandonos.
- [ ] Política fiscal/nota fiscal, proteção de dados e direitos do consumidor revisados.

**Observação:** não publicar dados falsos nem anunciar a loja como pronta só porque o redirecionamento para o provedor funcionou.
