#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Import verification script to check if all the required dependencies are installed correctly.
"""

import sys
import importlib.util

def check_import(module_name):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} is installed")
        return True
    except ImportError as e:
        print(f"❌ {module_name} is NOT installed: {str(e)}")
        return False

def main():
    """Check all imports needed for the application"""
    print("\nChecking critical imports...\n")
    
    # Check core modules
    required_modules = [
        "langchain",
        "langchain_core", 
        "langchain_groq",
        "groq",
        "llama_index",
        "sentence_transformers",
        "transformers",
        "fastapi",
        "streamlit"
    ]
    
    success_count = 0
    for module in required_modules:
        if check_import(module):
            success_count += 1
    
    # Try to import specific problematic modules to verify fixes
    print("\nChecking specific module implementations...\n")
    
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("✅ llama_index.embeddings.huggingface.HuggingFaceEmbedding can be imported")
        success_count += 1
    except Exception as e:
        print(f"❌ llama_index.embeddings.huggingface.HuggingFaceEmbedding import error: {str(e)}")
    
    try:
        from transformers import BertModel
        print("✅ transformers.BertModel can be imported")
        success_count += 1
    except Exception as e:
        print(f"❌ transformers.BertModel import error: {str(e)}")
    
    try:
        from langchain_groq import ChatGroq
        print("✅ langchain_groq.ChatGroq can be imported")
        success_count += 1
    except Exception as e:
        print(f"❌ langchain_groq.ChatGroq import error: {str(e)}")
    
    print(f"\nImport verification complete: {success_count}/{len(required_modules) + 3} modules successful\n")
    
    if success_count == len(required_modules) + 3:
        print("✅ All imports successful! The application should be ready to run.")
        return 0
    else:
        print("⚠️ Some imports failed. The application may not run correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 