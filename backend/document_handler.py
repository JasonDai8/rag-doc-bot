import os
import PyPDF2
from docx import Document
from typing import List, Optional
import io
import re

class SimpleTextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if not text:
            return []
        
        # Split by paragraphs first, then by sentences if needed
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    # Start new chunk with overlap
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + " " + paragraph
                else:
                    # Single paragraph is too long, split by sentences
                    sentences = re.split(r'[.!?]+', paragraph)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                            
                        if len(temp_chunk) + len(sentence) > self.chunk_size:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                                temp_chunk = sentence
                            else:
                                # Single sentence is too long, split by words
                                words = sentence.split()
                                word_chunk = ""
                                for word in words:
                                    if len(word_chunk) + len(word) > self.chunk_size:
                                        if word_chunk:
                                            chunks.append(word_chunk.strip())
                                        word_chunk = word
                                    else:
                                        word_chunk += " " + word if word_chunk else word
                                if word_chunk:
                                    chunks.append(word_chunk.strip())
                        else:
                            temp_chunk += ". " + sentence if temp_chunk else sentence
                    
                    if temp_chunk:
                        current_chunk = temp_chunk
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]

class DocumentHandler:
    def __init__(self):
        self.text_splitter = SimpleTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
    
    def extract_text_from_pdf(self, file_content: bytes) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
    
    def extract_text_from_docx(self, file_content: bytes) -> Optional[str]:
        """Extract text from DOCX file"""
        try:
            doc = Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return None
    
    def extract_text_from_txt(self, file_content: bytes) -> Optional[str]:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return None
    
    def extract_text(self, file_content: bytes, filename: str) -> Optional[str]:
        """Extract text from file based on file extension"""
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file_content)
        elif file_extension == 'docx':
            return self.extract_text_from_docx(file_content)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(file_content)
        else:
            print(f"Unsupported file type: {file_extension}")
            return None
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        try:
            chunks = self.text_splitter.split_text(text)
            return [chunk.strip() for chunk in chunks if chunk.strip()]
        except Exception as e:
            print(f"Error chunking text: {e}")
            return []
    
    def process_document(self, file_content: bytes, filename: str) -> Optional[List[str]]:
        """Process document and return chunks"""
        text = self.extract_text(file_content, filename)
        if text is None:
            return None
        
        chunks = self.chunk_text(text)
        return chunks if chunks else None 