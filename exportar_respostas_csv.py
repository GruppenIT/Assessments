#!/usr/bin/env python3
"""
Script para exportar respostas de assessments para CSV
Uso: python3 exportar_respostas_csv.py
"""

import sys
import os
import csv
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
try:
    from env_loader import load_env
    load_env()
except ImportError:
    pass

# Importar app e modelos
from app import app, db
from models.projeto import Projeto
from models.cliente_assessment import ClienteAssessment
from models.resposta import Resposta
from models.pergunta import Pergunta
from models.dominio import Dominio


def listar_projetos():
    """Lista todos os projetos disponíveis"""
    projetos = Projeto.query.order_by(Projeto.nome).all()
    
    if not projetos:
        print("\n❌ Nenhum projeto encontrado no sistema.")
        return None
    
    print("\n" + "="*70)
    print("PROJETOS DISPONÍVEIS")
    print("="*70)
    print(f"{'ID':<5} {'Nome do Projeto':<40} {'Cliente':<20}")
    print("-"*70)
    
    for projeto in projetos:
        cliente_nome = projeto.cliente.nome if projeto.cliente else "N/A"
        print(f"{projeto.id:<5} {projeto.nome[:40]:<40} {cliente_nome[:20]:<20}")
    
    print("="*70)
    return projetos


def listar_assessments(projeto_id):
    """Lista todos os assessments de um projeto"""
    assessments = ClienteAssessment.query.filter_by(
        projeto_id=projeto_id
    ).order_by(ClienteAssessment.id).all()
    
    if not assessments:
        print("\n⚠️  Nenhum assessment encontrado neste projeto.")
        return None
    
    print("\n" + "="*70)
    print("ASSESSMENTS DO PROJETO")
    print("="*70)
    print(f"{'ID':<5} {'Respondente':<30} {'Status':<15} {'Progresso':<10}")
    print("-"*70)
    
    for assessment in assessments:
        respondente_nome = assessment.respondente.nome if assessment.respondente else "N/A"
        status = "Concluído" if assessment.concluido else "Em Andamento"
        progresso = f"{assessment.progresso or 0}%"
        print(f"{assessment.id:<5} {respondente_nome[:30]:<30} {status:<15} {progresso:<10}")
    
    print("="*70)
    return assessments


def exportar_respostas_csv(assessment_id):
    """Exporta as respostas de um assessment para CSV"""
    assessment = ClienteAssessment.query.get(assessment_id)
    
    if not assessment:
        print(f"\n❌ Assessment ID {assessment_id} não encontrado.")
        return False
    
    # Buscar todas as respostas do assessment
    respostas = Resposta.query.filter_by(
        cliente_assessment_id=assessment_id
    ).order_by(Resposta.id).all()
    
    if not respostas:
        print("\n⚠️  Nenhuma resposta encontrada neste assessment.")
        return False
    
    # Criar nome do arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    projeto_nome = assessment.projeto.nome if assessment.projeto else "projeto"
    respondente_nome = assessment.respondente.nome if assessment.respondente else "respondente"
    
    # Limpar caracteres especiais dos nomes
    projeto_nome = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in projeto_nome)
    respondente_nome = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in respondente_nome)
    
    filename = f"respostas_{projeto_nome}_{respondente_nome}_{timestamp}.csv"
    
    # Criar CSV
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['dominio', 'pergunta', 'comentario', 'pontuacao']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for resposta in respostas:
                pergunta = resposta.pergunta
                dominio = pergunta.dominio if pergunta else None
                
                row = {
                    'dominio': dominio.nome if dominio else 'N/A',
                    'pergunta': pergunta.texto if pergunta else 'N/A',
                    'comentario': resposta.comentario or '',
                    'pontuacao': resposta.valor if resposta.valor is not None else ''
                }
                
                writer.writerow(row)
        
        print(f"\n✅ Arquivo CSV criado com sucesso!")
        print(f"📁 Arquivo: {filename}")
        print(f"📊 Total de respostas: {len(respostas)}")
        return True
    
    except Exception as e:
        print(f"\n❌ Erro ao criar arquivo CSV: {e}")
        return False


def main():
    """Função principal do script"""
    print("\n" + "="*70)
    print("EXPORTADOR DE RESPOSTAS PARA CSV")
    print("="*70)
    
    with app.app_context():
        # Passo 1: Listar projetos
        projetos = listar_projetos()
        if not projetos:
            return
        
        # Passo 2: Escolher projeto
        while True:
            try:
                projeto_id = input("\n🔹 Digite o ID do projeto (ou 'q' para sair): ").strip()
                
                if projeto_id.lower() == 'q':
                    print("\n👋 Saindo...")
                    return
                
                projeto_id = int(projeto_id)
                projeto = Projeto.query.get(projeto_id)
                
                if not projeto:
                    print(f"❌ Projeto ID {projeto_id} não encontrado. Tente novamente.")
                    continue
                
                print(f"\n✓ Projeto selecionado: {projeto.nome}")
                break
            
            except ValueError:
                print("❌ Por favor, digite um número válido.")
        
        # Passo 3: Listar assessments do projeto
        assessments = listar_assessments(projeto_id)
        if not assessments:
            return
        
        # Passo 4: Escolher assessment
        while True:
            try:
                assessment_id = input("\n🔹 Digite o ID do assessment (ou 'q' para voltar): ").strip()
                
                if assessment_id.lower() == 'q':
                    print("\n👋 Voltando ao menu de projetos...")
                    main()  # Recursão para voltar ao início
                    return
                
                assessment_id = int(assessment_id)
                assessment = ClienteAssessment.query.get(assessment_id)
                
                if not assessment:
                    print(f"❌ Assessment ID {assessment_id} não encontrado. Tente novamente.")
                    continue
                
                if assessment.projeto_id != projeto_id:
                    print(f"❌ Este assessment não pertence ao projeto selecionado. Tente novamente.")
                    continue
                
                respondente_nome = assessment.respondente.nome if assessment.respondente else "N/A"
                print(f"\n✓ Assessment selecionado: {respondente_nome}")
                break
            
            except ValueError:
                print("❌ Por favor, digite um número válido.")
        
        # Passo 5: Exportar para CSV
        print("\n📝 Exportando respostas para CSV...")
        sucesso = exportar_respostas_csv(assessment_id)
        
        if sucesso:
            # Perguntar se quer exportar outro
            continuar = input("\n🔹 Deseja exportar outro assessment? (s/n): ").strip().lower()
            if continuar == 's':
                main()  # Recursão para começar de novo
            else:
                print("\n✅ Exportação concluída! Até logo! 👋")
        else:
            print("\n⚠️  Exportação falhou.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
