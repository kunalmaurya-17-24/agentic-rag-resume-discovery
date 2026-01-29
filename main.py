import pathlib
from ingestion.pdf_processor import ResumeIngestor
from ingestion.docx_processor import DocxProcessor
import docx2txt # Used by Docx2txtLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def run_ingestion_pipeline():
    # 1. Configuration
    data_dir = pathlib.Path(r"E:\MY_RAG\data")
    all_docs = []
    
    # 2. Initialize the Ingestion Engines
    pdf_ingestor = ResumeIngestor(data_dir=data_dir)
    docx_processor = DocxProcessor()
    
    print(f"🚀 Starting Ingestion Pipeline from: {data_dir}")

    # 3. Process PDF Files
    print("\n--- Processing PDFs ---")
    for pdf_path in data_dir.glob("**/*.pdf"):
        try:
            pdf_docs = pdf_ingestor.process_pdf(pdf_path)
            all_docs.extend(pdf_docs)
        except Exception as e:
            print(f"❌ Error processing PDF {pdf_path.name}: {e}")

    # 4. Process DOCX Files
    print("\n--- Processing DOCX ---")
    for docx_path in data_dir.glob("**/*.docx"):
        try:
            docx_docs = docx_processor.process_docx(docx_path)
            all_docs.extend(docx_docs)
        except Exception as e:
            print(f"❌ Error processing DOCX {docx_path.name}: {e}")

    print(f"\n✅ Total Documents Loaded: {len(all_docs)}")

    # 5. Splitting Strategy
    print("\n--- Splitting Documents ---")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(all_docs)
    print(f"✂️ Total Splits Created: {len(splits)}")

    # 6. Verification Trace (The "Blog Hero" Output)
    kunal_docs = [d for d in all_docs if "Kunal_Maurya" in d.metadata.get('source', '')]
    if kunal_docs:
        print(f"\n🔍 Verification Trace: {kunal_docs[0].metadata['source']}")
        print(f"   Extracted Links: {kunal_docs[0].metadata.get('all_links', [])}")

    return splits

if __name__ == "__main__":
    run_ingestion_pipeline()
