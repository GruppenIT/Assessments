#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para exportar respostas de projetos liberados para CSV.

Uso: python3 scripts/exportar_respostas.py "Nome do Tipo de Assessment"

Gera um arquivo CSV no formato: nome_argumento_timestamp.csv
Contém apenas respostas de projetos com status "Liberado" (finalizado=True)
"""

import sys
import os
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models.assessment_version import AssessmentTipo, AssessmentVersao, AssessmentDominio
from models.projeto import Projeto, ProjetoAssessment
from models.cliente import Cliente
from models.respondente import Respondente
from models.resposta import Resposta
from models.pergunta import Pergunta


def sanitize_filename(name):
    """Remove caracteres inválidos do nome do arquivo"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.replace(' ', '_').lower()


def exportar_respostas(nome_tipo_assessment):
    """Exporta respostas de projetos liberados para CSV"""
    
    app = create_app()
    
    with app.app_context():
        tipo = AssessmentTipo.query.filter(
            AssessmentTipo.nome.ilike(f'%{nome_tipo_assessment}%')
        ).first()
        
        if not tipo:
            print(f"Erro: Tipo de assessment '{nome_tipo_assessment}' não encontrado.")
            print("\nTipos disponíveis:")
            tipos = AssessmentTipo.query.filter_by(ativo=True).all()
            for t in tipos:
                print(f"  - {t.nome}")
            return False
        
        print(f"Tipo de assessment encontrado: {tipo.nome} (ID: {tipo.id})")
        
        versoes_ids = [v.id for v in tipo.versoes]
        
        if not versoes_ids:
            print(f"Nenhuma versão encontrada para o tipo '{tipo.nome}'.")
            return False
        
        print(f"Versões encontradas: {len(versoes_ids)}")
        
        projetos_assessment = ProjetoAssessment.query.filter(
            ProjetoAssessment.versao_assessment_id.in_(versoes_ids),
            ProjetoAssessment.ativo == True,
            ProjetoAssessment.finalizado == True
        ).all()
        
        projeto_ids = [pa.projeto_id for pa in projetos_assessment]
        
        if not projeto_ids:
            print(f"Nenhum projeto liberado encontrado para o tipo '{tipo.nome}'.")
            return False
        
        projetos = Projeto.query.filter(
            Projeto.id.in_(projeto_ids),
            Projeto.ativo == True
        ).all()
        
        print(f"Projetos liberados encontrados: {len(projetos)}")
        
        respostas = db.session.query(
            Cliente.nome.label('cliente_nome'),
            Respondente.email.label('respondente_email'),
            AssessmentTipo.nome.label('tipo_nome'),
            AssessmentDominio.nome.label('dominio_nome'),
            Pergunta.texto.label('pergunta_texto'),
            Resposta.nota.label('valor_resposta'),
            Resposta.comentario.label('comentario')
        ).join(
            Projeto, Resposta.projeto_id == Projeto.id
        ).join(
            Cliente, Projeto.cliente_id == Cliente.id
        ).join(
            Respondente, Resposta.respondente_id == Respondente.id
        ).join(
            Pergunta, Resposta.pergunta_id == Pergunta.id
        ).join(
            AssessmentDominio, Pergunta.dominio_versao_id == AssessmentDominio.id
        ).join(
            AssessmentVersao, AssessmentDominio.versao_id == AssessmentVersao.id
        ).join(
            AssessmentTipo, AssessmentVersao.tipo_id == AssessmentTipo.id
        ).filter(
            Resposta.projeto_id.in_(projeto_ids),
            AssessmentTipo.id == tipo.id
        ).order_by(
            Cliente.nome,
            Respondente.email,
            AssessmentDominio.ordem,
            Pergunta.ordem
        ).all()
        
        if not respostas:
            print(f"Nenhuma resposta encontrada para os projetos liberados.")
            return False
        
        print(f"Total de respostas a exportar: {len(respostas)}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"{sanitize_filename(nome_tipo_assessment)}_{timestamp}.csv"
        
        with open(nome_arquivo, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            writer.writerow([
                'Nome Cliente',
                'E-mail Respondente',
                'Tipo Assessment',
                'Domínio',
                'Pergunta',
                'Pontuação',
                'Comentário'
            ])
            
            for resp in respostas:
                writer.writerow([
                    resp.cliente_nome or '',
                    resp.respondente_email or '',
                    resp.tipo_nome or '',
                    resp.dominio_nome or '',
                    resp.pergunta_texto or '',
                    resp.valor_resposta if resp.valor_resposta is not None else '',
                    resp.comentario or ''
                ])
        
        print(f"\nArquivo exportado com sucesso: {nome_arquivo}")
        print(f"Total de registros: {len(respostas)}")
        return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/exportar_respostas.py \"Nome do Tipo de Assessment\"")
        print("\nExemplo:")
        print('  python3 scripts/exportar_respostas.py "Cybersecurity"')
        print('  python3 scripts/exportar_respostas.py "NIST CSF"')
        sys.exit(1)
    
    nome_tipo = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"EXPORTADOR DE RESPOSTAS - PROJETOS LIBERADOS")
    print(f"{'='*60}")
    print(f"Tipo de Assessment: {nome_tipo}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    sucesso = exportar_respostas(nome_tipo)
    
    if sucesso:
        print(f"\n{'='*60}")
        print("Exportação concluída com sucesso!")
        print(f"{'='*60}\n")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
