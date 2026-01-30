import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional


class TextLoader:
    
    @staticmethod
    def load_text(file_path: str) -> str:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        extension = path.suffix.lower()
        
        try:
            if extension == '.pdf':
                return TextLoader._extract_from_pdf(str(path))
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
                
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(pdf_path: str) -> str:
        text = ""
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
            
            return text
            
        except Exception as e:
            raise IOError(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return {
            'name': path.name,
            'size_bytes': path.stat().st_size,
            'absolute_path': str(path.absolute()),
            'extension': path.suffix,
            'type': 'PDF' if path.suffix.lower() == '.pdf' else 'Text'
        }


if __name__ == "__main__":
    # Test the loader
    loader = TextLoader()
    
    # This will be tested with actual file path
    print("TextLoader module ready for testing")
