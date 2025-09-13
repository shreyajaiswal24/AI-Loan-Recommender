import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.embeddings = SentenceTransformerEmbeddings(model_name=settings.embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        self.vector_store = None
        
    def load_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            return ""
    
    def process_bank_documents(self, documents_dir: str) -> List[Document]:
        """Process all bank documents in directory"""
        documents = []
        
        for file_path in Path(documents_dir).glob("*.pdf"):
            logger.info(f"Processing {file_path}")
            
            # Extract bank name from filename
            bank_name = file_path.stem.split("_")[0].upper()
            
            # Extract text
            text = self.load_pdf(str(file_path))
            if not text.strip():
                continue
                
            # Create document with metadata
            doc = Document(
                page_content=text,
                metadata={
                    "source": str(file_path),
                    "bank_name": bank_name,
                    "document_type": "loan_product_guide",
                    "file_name": file_path.name
                }
            )
            documents.append(doc)
        
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks for better retrieval"""
        chunked_docs = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc.page_content)
            
            for i, chunk in enumerate(chunks):
                chunked_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                )
                chunked_docs.append(chunked_doc)
        
        return chunked_docs
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create and populate vector database"""
        try:
            # Ensure directory exists
            os.makedirs(settings.chroma_db_path, exist_ok=True)
            
            # Create vector store
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=settings.chroma_collection_name,
                persist_directory=settings.chroma_db_path
            )
            
            # Persist the database
            vector_store.persist()
            logger.info(f"Created vector store with {len(documents)} documents")
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def load_existing_vector_store(self) -> Chroma:
        """Load existing vector database"""
        try:
            vector_store = Chroma(
                collection_name=settings.chroma_collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.chroma_db_path
            )
            logger.info("Loaded existing vector store")
            return vector_store
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return None
    
    def initialize_vector_store(self, force_rebuild: bool = False):
        """Initialize or load vector store"""
        if force_rebuild or not os.path.exists(settings.chroma_db_path):
            logger.info("Building new vector store...")
            
            # Process documents
            documents = self.process_bank_documents(settings.raw_data_dir)
            if not documents:
                raise ValueError("No documents found to process")
            
            # Chunk documents
            chunked_docs = self.chunk_documents(documents)
            
            # Create vector store
            self.vector_store = self.create_vector_store(chunked_docs)
        else:
            # Load existing
            self.vector_store = self.load_existing_vector_store()
            if self.vector_store is None:
                raise ValueError("Could not load existing vector store")
    
    def search_relevant_documents(self, query: str, k: int = None) -> List[Document]:
        """Search for relevant documents"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        k = k or settings.max_retrieved_docs
        
        # Perform similarity search
        docs = self.vector_store.similarity_search(
            query=query,
            k=k
        )
        
        return docs