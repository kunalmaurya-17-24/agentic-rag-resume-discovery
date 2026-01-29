import os
import re
import pathlib
from typing import List, Dict, Any
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
import fitz  # PyMuPDF for native links

class ResumeIngestor():
    def __init__(self, data_dir):
        links = []

        self.data_dir = data_dir
        self.link_scanner = re.compile( #This function is responsible for finding and extracting all the links present in the pdf using regular expressions
        r'(https?://[^\s<>"{}|\\^`\[\]]+)|'    
        r'(www\d{0,3}\.[^\s<>"{}|\\^`\[\]]+)|' 
        r'(github\.com[^\s<>"{}|\\^`\[\]]+)|'   
        r'(linkedin\.com[^\s<>"{}|\\^`\[\]]+)|' 
        r'([a-z0-9-]+\.(com|org|net|io|ai|co|edu)[^\s<>"{}|\\^`\[\]]*)',
        re.IGNORECASE
    )
        
        

    def extract_native_links(self, pdf_path: str | Path) -> List[str]:
        """Extract clickable PDF hyperlinks (PyMuPDF native)"""
        doc = fitz.open(pdf_path)
        links = []
        for page in doc:
            for link in page.get_links():
                uri = link.get("uri")  
                if uri is not None:    
                    links.append(uri)
        doc.close()
        return list(set(links))  # Dedupe


    def process_pdf(self, pdf_path: str | Path) -> List[Dict[str, Any]]:
        """Process single PDF: text links + native links"""
        print(f"🔗 Processing: {pdf_path}")
        
        # Native hyperlinks
        native_links = self.extract_native_links(pdf_path)
        
        # Text extraction + regex
        loader = PyMuPDFLoader(str(pdf_path))
        docs = loader.load()
        
        all_text_links = []
        for doc in docs:
            text_links = self.link_scanner.findall(doc.page_content)
            doc.metadata["text_links"] = list(set([m[0] or m[1] or m[2] or m[3] or m[4] for m in text_links]))  # ✅ 5 groups
            all_text_links.extend(doc.metadata["text_links"])
        
        # Added native links to first doc (or all)
        if docs:
            docs[0].metadata["native_links"] = native_links
            docs[0].metadata["all_links"] = list(set(native_links + all_text_links))
        
        return docs








if __name__ == "__main__":
    """Standalone test for a single file"""
    import pathlib
    
    # Configuration
    data_dir = pathlib.Path(r"E:\MY_RAG\data")
    test_pdf = data_dir / "Kunal_Maurya_LangGraph_Python_Dev.pdf"
    
    # Instantiate the class
    ingestor = ResumeIngestor(data_dir=data_dir)
    
    #Run Test
    if test_pdf.exists():
        docs = ingestor.process_pdf(test_pdf)
        print(f"✅ Test SUCCESS: {len(docs)} pages processed")
        if docs:
            print(f"   Sample Metadata (All Links): {len(docs[0].metadata.get('all_links', []))} found")
    else:
        print(f"❌ Test file not found at: {test_pdf}")

