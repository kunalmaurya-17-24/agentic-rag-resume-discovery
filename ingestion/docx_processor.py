import re
import pathlib
from typing import List, Dict, Any
from pathlib import Path
from langchain_community.document_loaders import Docx2txtLoader

class DocxProcessor():
    def __init__(self):
        """Build the tools needed for DOCX extraction"""
        self.link_scanner = re.compile(
            r'(https?://[^\s<>"{}|\\^`\[\]]+)|'    
            r'(www\d{0,3}\.[^\s<>"{}|\\^`\[\]]+)|' 
            r'(github\.com[^\s<>"{}|\\^`\[\]]+)|'   
            r'(linkedin\.com[^\s<>"{}|\\^`\[\]]+)|' 
            r'([a-z0-9-]+\.(com|org|net|io|ai|co|edu)[^\s<>"{}|\\^`\[\]]*)',
            re.IGNORECASE
        )

    def process_docx(self, docx_path: str | Path) -> List[Dict[str, Any]]:
        """Process single DOCX: text extraction + regex link finding"""
        docx_path = Path(docx_path)
        print(f"📄 Processing DOCX: {docx_path.name}")
        
        try:
            loader = Docx2txtLoader(str(docx_path))
            docs = loader.load()
            
            for doc in docs:
                # Find all links in the text
                text_links = self.link_scanner.findall(doc.page_content)
                # Clean up the regex matches (extract non-empty group)
                doc.metadata["all_links"] = list(set([m[0] or m[1] or m[2] or m[3] or m[4] for m in text_links]))
                doc.metadata["native_links"] = []  
                
            return docs
            
        except Exception as e:
            print(f"❌ Error in DocxProcessor: {e}")
            return []

if __name__ == "__main__":
    """Standalone test"""
    data_dir = pathlib.Path(r"E:\MY_RAG\data")
    # Find first docx file in data dir
    docx_files = list(data_dir.glob("*.docx"))
    
    if docx_files:
        test_file = docx_files[0]
        processor = DocxProcessor()
        results = processor.process_docx(test_file)
        print(f"✅ Test SUCCESS: Processed {test_file.name}")
        if results:
            print(f"   Links found: {results[0].metadata.get('all_links')}")
    else:
        print("ℹ️ No DOCX files found to test.")