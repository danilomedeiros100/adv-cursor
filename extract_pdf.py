#!/usr/bin/env python3
import PyPDF2
import os
import sys

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Erro ao extrair texto do PDF {pdf_path}: {str(e)}"

def main():
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        print(f"Diretório {docs_dir} não encontrado")
        return
    
    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(docs_dir, pdf_file)
        print(f"\n{'='*60}")
        print(f"ARQUIVO: {pdf_file}")
        print(f"{'='*60}")
        
        text = extract_text_from_pdf(pdf_path)
        print(text)
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
