#!/bin/bash

echo "======================================================================"
echo "IMPLEMENTAÇÃO: BOTÃO EXPORTAR RESPOSTAS CSV"
echo "======================================================================"
echo ""
echo "O QUE FOI IMPLEMENTADO:"
echo ""
echo "✅ BOTÃO NA INTERFACE:"
echo "  • Botão 'Exportar Respostas' adicionado ao lado do 'Relatório Formal'"
echo "  • Localização: /admin/projetos/{id}/estatisticas"
echo "  • Cor verde (btn-success) com ícone de arquivo CSV"
echo ""
echo "✅ FUNCIONALIDADE:"
echo "  • Exporta TODAS as respostas de TODOS os assessments do projeto"
echo "  • Formato CSV com encoding UTF-8-BOM (compatível com Excel)"
echo "  • Colunas: respondente, dominio, pergunta, comentario, pontuacao"
echo "  • Nome do arquivo: respostas_{nome_projeto}_{timestamp}.csv"
echo ""
echo "======================================================================"
echo "APLICANDO NO SERVIDOR..."
echo "======================================================================"
echo ""

# Ir para diretório do projeto
cd /var/www/assessment || {
    echo "❌ ERRO: Diretório /var/www/assessment não encontrado"
    exit 1
}

# Fazer backup do estado atual
echo "1. Criando backup..."
git diff > /tmp/backup_csv_$(date +%Y%m%d_%H%M%S).patch
echo "   ✓ Backup salvo em /tmp/"
echo ""

# Fazer git pull
echo "2. Atualizando código do repositório..."
git pull origin main || {
    echo "❌ ERRO: Falha ao fazer git pull"
    echo "   Execute: cd /var/www/assessment && git status"
    exit 1
}
echo "   ✓ Código atualizado"
echo ""

# Reiniciar serviço
echo "3. Reiniciando serviço assessment..."
if command -v supervisorctl &> /dev/null; then
    sudo supervisorctl restart assessment
    echo "   ✓ Serviço reiniciado via Supervisor"
elif systemctl is-active --quiet assessment; then
    sudo systemctl restart assessment
    echo "   ✓ Serviço reiniciado via Systemd"
else
    echo "   ⚠ Não foi possível detectar o gerenciador de serviços"
    echo "   Execute manualmente: sudo supervisorctl restart assessment"
fi
echo ""

# Aguardar inicialização
echo "4. Aguardando inicialização (5 segundos)..."
sleep 5
echo "   ✓ Pronto para testar"
echo ""

echo "======================================================================"
echo "✅ IMPLANTAÇÃO CONCLUÍDA!"
echo "======================================================================"
echo ""
echo "COMO TESTAR:"
echo ""
echo "1. Acesse a página de estatísticas de qualquer projeto concluído:"
echo "   Exemplo: https://assessments.zerobox.com.br/admin/projetos/1/estatisticas"
echo ""
echo "2. Observe o novo botão verde 'Exportar Respostas' ao lado do"
echo "   botão amarelo 'Relatório Formal'"
echo ""
echo "3. Clique no botão 'Exportar Respostas'"
echo ""
echo "4. O arquivo CSV será baixado automaticamente com nome:"
echo "   respostas_{nome_do_projeto}_{data_hora}.csv"
echo ""
echo "5. Abra o arquivo no Excel ou qualquer editor de planilhas"
echo ""
echo "======================================================================"
echo "FORMATO DO CSV:"
echo "======================================================================"
echo ""
echo "Colunas:"
echo "  1. respondente - Nome do respondente"
echo "  2. dominio     - Nome do domínio da pergunta"
echo "  3. pergunta    - Texto completo da pergunta"
echo "  4. comentario  - Comentário do respondente (se houver)"
echo "  5. pontuacao   - Pontuação atribuída (0-5)"
echo ""
echo "Exemplo de linha no CSV:"
echo "João Silva,Segurança de Rede,Existe firewall configurado?,Sim temos...,5"
echo ""
echo "======================================================================"
echo "CASOS DE USO:"
echo "======================================================================"
echo ""
echo "✓ Análise detalhada em Excel/Google Sheets"
echo "✓ Importação para outros sistemas"
echo "✓ Backup das respostas em formato portátil"
echo "✓ Criação de relatórios personalizados"
echo "✓ Análise estatística avançada"
echo ""
echo "======================================================================"
