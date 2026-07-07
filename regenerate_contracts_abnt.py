import os
import shutil
import datetime
from app import create_app
from extensions import db
from models import Document
from services.pdf_service import create_document_pdf

def backup_data():
    print("--- FASE 1: Backup ---")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.getcwd(), 'backups', f'backup_{timestamp}')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup instance/ (Database)
    instance_dir = os.path.join(os.getcwd(), 'instance')
    if os.path.exists(instance_dir):
        print(f"Compactando {instance_dir}...")
        shutil.make_archive(os.path.join(backup_dir, 'instance_backup'), 'zip', instance_dir)
    else:
        print("Pasta instance/ não encontrada. Pulando backup do DB.")

    # Backup uploads/ (PDFs)
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    if os.path.exists(uploads_dir):
        print(f"Compactando {uploads_dir}...")
        shutil.make_archive(os.path.join(backup_dir, 'uploads_backup'), 'zip', uploads_dir)
    else:
        print("Pasta uploads/ não encontrada. Pulando backup de PDFs.")
        
    print(f"Backup concluído em: {backup_dir}\n")

def run_migration():
    print("--- FASE 2: Consulta e Processamento ---")
    app = create_app()
    with app.app_context():
        contracts = Document.query.filter_by(type='contract').all()
        print(f"Encontrados {len(contracts)} contratos para migração ABNT.")
        
        print("\n--- FASE 3: Regeneração e Substituição ---")
        for doc in contracts:
            print(f"Regerando contrato {doc.id} - {doc.title}...")
            if not doc.content_html:
                print(f" -> Aviso: Contrato {doc.id} não possui content_html. Pulando.")
                continue
                
            try:
                # create_document_pdf will handle sanitization and passing the correct margins
                create_document_pdf(doc.type, doc.content_html, doc.file_path)
                print(f" -> Sucesso: PDF regerado em {doc.file_path}")
            except Exception as e:
                print(f" -> Erro ao regerar {doc.id}: {str(e)}")

        print("\nMigração concluída com sucesso.")

if __name__ == "__main__":
    backup_data()
    run_migration()
