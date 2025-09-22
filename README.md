# PDF Q&A System with RAG  
**Ask questions, get answers-directly from your PDFs.**  
A serverless, AI-powered system that uses **Retrieval-Augmented Generation (RAG)** to deliver accurate, context-aware answers from your uploaded documents. 

## Live Demo  
Web App: [pdf-rag-llm.vercel.app](https://pdf-rag-llm.vercel.app)  
API Docs: [https://cq4kcnt6ph2cpum4xtpzbxycpq0ighgw.lambda-url.us-east-1.on.aws/docs](https://cq4kcnt6ph2cpum4xtpzbxycpq0ighgw.lambda-url.us-east-1.on.aws/docs)

## Tech Stack  
| Backend            | Frontend         | DevOps                  |  
|--------------------|------------------|-------------------------|  
| Python             | TypeScript       | AWS CDK                 |  
| LangChain          | Next.js          | Docker                  |  
| FastAPI            | Tailwind CSS     | GitHub Actions          |  
| Google Gemini API  | Vercel (Hosting) | AWS Lambda/DynamoDB/SSM |  

## Local Development Setup
### Prerequisites
- Python 3.11
- Node.js 18
- AWS CLI Configured
- Docker Engine Started
- Google API Key
- Chroma API Key

### Steps
1. **Clone the repo**:
   ```bash
   git clone https://github.com/yourusername/pdf-rag-llm.git
   cd pdf-rag-llm/
   ```
2. **Deploy AWS Infrastructure**
   ```bash
   # Add GOOGLE_API_KEY to AWS SSM
   aws ssm put-parameter \
    --name "/rag-app/google_api_key" \
    --value "your_actual_key_here" \
    --type "SecureString" \
    --overwrite

   # Add CHROMA_API_KEY to AWS SSM
   aws ssm put-parameter \
    --name "/rag-app/chroma_api_key" \
    --value "your_actual_key_here" \
    --type "SecureString" \
    --overwrite
   
   # Deploy CDK
   cd rag-cdk-infra/
   npm install -g aws-cdk typescript
   npm install
   cdk bootstrap  # first time
   cdk deploy
   cd ..
   ```
   You will see output like:
   ```bash
   Outputs:
   RagCdkInfraStack.FunctionUrl = https://xyz.lambda-url.us-east-1.on.aws/ 
   RagCdkInfraStack.RagQueryTableName = RagCdkInfraStack-RagQueryTablexyz 
   ```
3. **Configure environment variables**
   At the root of the project, create a `.env` file and add the values from the CDK outputs:
   ```bash
   TABLE_NAME=RagCdkInfraStack-RagQueryTablexyz 
   BUCKET_NAME=your_bucket_url
   ```
   In the frontend directory `./rag-frontend`, create a `.env.local` file and add the values from the CDK outputs:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=https://xyz.lambda-url.us-east-1.on.aws/ # or use your local server
   NEXT_PUBLIC_S3_BUCKET_URL=your_bucket_url
   ```
4. **Run FastAPI server locally**
   ```bash
   pip install -r requirements-dev.txt
   uvicorn image.src.api_handler --host 0.0.0.0 --port 8000 > server.log 2>&1
   ```
6. **Run tests**
   ```bash
   # Print the content of log file in case of failure
   pytest -s || (cat server.log && false)
   ```
7. **Run frontend locally**
   ```bash   
   cd rag-frontend/
   npm install
   npm run dev
   ```
