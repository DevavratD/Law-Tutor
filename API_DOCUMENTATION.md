# Indian Law Tutor API Documentation

## Overview

The Indian Law Tutor API provides programmatic access to legal document management, question answering, quiz generation, and legal concept explanations. This documentation outlines all available endpoints, their parameters, and response formats.

**Base URL**: `http://localhost:8000/api`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Endpoints

### Documents

#### Upload Document
Upload a legal document (PDF, DOCX, TXT) for processing and indexing.

- **URL**: `/documents/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (required): The document file to upload
  - `description` (optional): Description of the document

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "description=Legal case study on Article 21"
```

**Example Response**:
```json
{
  "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
  "filename": "document.pdf",
  "description": "Legal case study on Article 21",
  "content_length": 15782,
  "status": "processed"
}
```

#### List Documents
Get a list of all uploaded and processed documents.

- **URL**: `/documents/list`
- **Method**: `GET`

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/documents/list"
```

**Example Response**:
```json
{
  "documents": [
    {
      "file_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
      "extraction_date": "2023-04-15T14:32:10.123456",
      "content_length": 15782
    },
    {
      "file_id": "ce1a9802-22b1-4557-a6f8-3858a391380e",
      "extraction_date": "2023-04-16T09:45:22.987654",
      "content_length": 8943
    }
  ]
}
```

#### Get Document
Get details of a specific document by ID.

- **URL**: `/documents/{document_id}`
- **Method**: `GET`
- **Parameters**:
  - `include_content` (query, optional): Set to `true` to include the full document content in the response

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/documents/80ac9c55-3a0d-45a2-87d4-e52c8288d573?include_content=true"
```

**Example Response**:
```json
{
  "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
  "content_length": 15782,
  "content": "The full text content of the document..."
}
```

#### Delete Document
Delete a document and its associated data.

- **URL**: `/documents/{document_id}`
- **Method**: `DELETE`

**Example Request**:
```bash
curl -X DELETE "http://localhost:8000/api/documents/80ac9c55-3a0d-45a2-87d4-e52c8288d573"
```

**Example Response**:
```json
{
  "status": "success",
  "message": "Document with ID 80ac9c55-3a0d-45a2-87d4-e52c8288d573 has been deleted"
}
```

### Q&A

#### Ask Question
Ask a question about a specific document or a general legal question.

- **URL**: `/qa/ask`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "question": "What are the key aspects of Article 21?",
    "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573" // Optional, omit for general questions
  }
  ```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key aspects of Article 21?",
    "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573"
  }'
```

**Example Response**:
```json
{
  "answer": "Article 21 of the Indian Constitution guarantees the protection of life and personal liberty...",
  "sources": [
    {
      "text": "Article 21 states: 'No person shall be deprived of his life or personal liberty except according to procedure established by law.'",
      "score": 0.92
    }
  ],
  "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573"
}
```

#### Chat Interaction
Have a conversation with the legal tutor, maintaining context through chat history.

- **URL**: `/qa/chat`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "question": "How is Article 21 interpreted by the Supreme Court?",
    "chat_history": [
      {"role": "user", "content": "What is Article a21?"},
      {"role": "assistant", "content": "Article 21 of the Indian Constitution guarantees..."}
    ],
    "document_id": null // Optional, include to ground responses in a document
  }
  ```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/qa/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How is Article 21 interpreted by the Supreme Court?",
    "chat_history": [
      {"role": "user", "content": "What is Article 21?"},
      {"role": "assistant", "content": "Article 21 of the Indian Constitution guarantees..."}
    ]
  }'
```

**Example Response**:
```json
{
  "answer": "The Supreme Court has given a broad interpretation to Article 21, expanding its scope to include...",
  "sources": [],
  "document_id": null
}
```

### Quizzes

#### Generate Quiz
Generate a quiz based on a document.

- **URL**: `/quizzes/generate`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
    "num_questions": 5,
    "difficulty": "medium" // "easy", "medium", or "hard"
  }
  ```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/quizzes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
    "num_questions": 5,
    "difficulty": "medium"
  }'
```

**Example Response**:
```json
{
  "quiz_id": "2a696818-506d-417b-b015-569befd7acb6",
  "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
  "num_questions": 5,
  "difficulty": "medium",
  "status": "generated"
}
```

#### List Quizzes
Get a list of all generated quizzes, optionally filtered by document ID.

- **URL**: `/quizzes/list`
- **Method**: `GET`
- **Parameters**:
  - `document_id` (query, optional): Filter quizzes for a specific document

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/quizzes/list?document_id=80ac9c55-3a0d-45a2-87d4-e52c8288d573"
```

**Example Response**:
```json
{
  "quizzes": [
    {
      "quiz_id": "2a696818-506d-417b-b015-569befd7acb6",
      "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
      "num_questions": 5,
      "difficulty": "medium",
      "generation_date": "2023-04-15T16:45:30.123456"
    }
  ]
}
```

#### Get Quiz
Get details of a specific quiz by ID.

- **URL**: `/quizzes/{quiz_id}`
- **Method**: `GET`

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/quizzes/2a696818-506d-417b-b015-569befd7acb6"
```

**Example Response**:
```json
{
  "quiz_id": "2a696818-506d-417b-b015-569befd7acb6",
  "document_id": "80ac9c55-3a0d-45a2-87d4-e52c8288d573",
  "num_questions": 5,
  "difficulty": "medium",
  "questions": [
    {
      "question": "What is the primary focus of Article 21 of the Indian Constitution?",
      "options": [
        "A. Right to equality",
        "B. Right to life and personal liberty",
        "C. Right to freedom of speech",
        "D. Right to constitutional remedies"
      ],
      "correct_answer": "B",
      "explanation": "Article 21 focuses on the protection of life and personal liberty..."
    },
    // More questions...
  ]
}
```

#### Submit Quiz Answers
Submit answers to a quiz and get evaluation results.

- **URL**: `/quizzes/{quiz_id}/submit`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "answers": ["B", "A", "C", "D", "A"]
  }
  ```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/quizzes/2a696818-506d-417b-b015-569befd7acb6/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": ["B", "A", "C", "D", "A"]
  }'
```

**Example Response**:
```json
{
  "quiz_id": "2a696818-506d-417b-b015-569befd7acb6",
  "score": 80.0,
  "correct_count": 4,
  "total_questions": 5,
  "feedback": [
    {
      "question_number": 1,
      "is_correct": true,
      "user_answer": "B",
      "correct_answer": "B",
      "explanation": "Correct! Article 21 focuses on the protection of life and personal liberty..."
    },
    // More feedback for each question...
  ]
}
```

### Legal Concept Explanations

#### Explain Concept
Get an explanation for a legal concept.

- **URL**: `/explanations/concept`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "concept": "Habeas Corpus"
  }
  ```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/explanations/concept" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Habeas Corpus"
  }'
```

**Example Response**:
```json
{
  "concept": "Habeas Corpus",
  "explanation": "Habeas Corpus is a fundamental legal principle that safeguards individual freedom against arbitrary state action. In Indian law, it is one of the writs enshrined under Article 32 and Article 226 of the Constitution..."
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Unsupported file format. Supported formats: .pdf, .docx, .txt"
}
```

### 404 Not Found
```json
{
  "detail": "Document with ID 80ac9c55-3a0d-45a2-87d4-e52c8288d573 not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to process document: File extraction error"
}
```

## Integration Examples

### Python Client Example

```python
import requests
import json

# Base API URL
API_URL = "http://localhost:8000/api"

# Upload a document
def upload_document(file_path, description=None):
    files = {'file': open(file_path, 'rb')}
    data = {}
    if description:
        data['description'] = description
        
    response = requests.post(f"{API_URL}/documents/upload", files=files, data=data)
    return response.json()

# Get document list
def get_documents():
    response = requests.get(f"{API_URL}/documents/list")
    return response.json()['documents']

# Ask a question about a document
def ask_question(question, document_id=None):
    data = {'question': question}
    if document_id:
        data['document_id'] = document_id
        
    response = requests.post(f"{API_URL}/qa/ask", json=data)
    return response.json()

# Generate a quiz
def generate_quiz(document_id, num_questions=5, difficulty="medium"):
    data = {
        'document_id': document_id,
        'num_questions': num_questions,
        'difficulty': difficulty
    }
    
    response = requests.post(f"{API_URL}/quizzes/generate", json=data)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Upload a document
    doc_response = upload_document("legal_document.pdf", "Constitution analysis")
    document_id = doc_response['document_id']
    print(f"Uploaded document with ID: {document_id}")
    
    # Ask a question
    answer = ask_question("What is the scope of Article 21?", document_id)
    print(f"Answer: {answer['answer']}")
    
    # Generate a quiz
    quiz = generate_quiz(document_id)
    print(f"Generated quiz with ID: {quiz['quiz_id']}")
```

### JavaScript Client Example

```javascript
const API_URL = "http://localhost:8000/api";

// Upload a document
async function uploadDocument(file, description = null) {
  const formData = new FormData();
  formData.append('file', file);
  
  if (description) {
    formData.append('description', description);
  }
  
  const response = await fetch(`${API_URL}/documents/upload`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Get document list
async function getDocuments() {
  const response = await fetch(`${API_URL}/documents/list`);
  const data = await response.json();
  return data.documents;
}

// Ask a question about a document
async function askQuestion(question, documentId = null) {
  const data = { question };
  
  if (documentId) {
    data.document_id = documentId;
  }
  
  const response = await fetch(`${API_URL}/qa/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return await response.json();
}

// Generate a quiz
async function generateQuiz(documentId, numQuestions = 5, difficulty = "medium") {
  const data = {
    document_id: documentId,
    num_questions: numQuestions,
    difficulty: difficulty
  };
  
  const response = await fetch(`${API_URL}/quizzes/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return await response.json();
}

// Example usage:
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById('fileInput');
  const description = document.getElementById('description').value;
  
  if (fileInput.files.length > 0) {
    const result = await uploadDocument(fileInput.files[0], description);
    console.log(`Uploaded document with ID: ${result.document_id}`);
    
    // Ask a question about the document
    const answer = await askQuestion("What is habeas corpus?", result.document_id);
    console.log(`Answer: ${answer.answer}`);
    
    // Generate a quiz
    const quiz = await generateQuiz(result.document_id);
    console.log(`Generated quiz with ID: ${quiz.quiz_id}`);
  }
});
```

## Rate Limits

Currently, there are no rate limits implemented.

