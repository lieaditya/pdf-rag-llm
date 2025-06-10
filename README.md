# 📄 PDF Q&A System with RAG  
**Ask questions, get answers—directly from your PDFs.**  
A serverless, AI-powered system that uses **Retrieval-Augmented Generation (RAG)** to deliver accurate, context-aware answers from uploaded documents. 

## 🚀 Key Features  
- **AI-Powered Q&A**: Google Gemini + LangChain for generative answers.  
- **Serverless Architecture**: FastAPI + AWS Lambda (Dockerized) for scalability.  
- **Vector Search**: ChromaDB for efficient PDF text retrieval.  
- **Infrastructure-as-Code**: AWS CDK deploys DynamoDB (storage) and SSM (secrets).  
- **Responsive UI**: Next.js + Tailwind CSS (Vercel-hosted).  
- **CI/CD Automation**: GitHub Actions for testing/Lambda deployments.  

## 🌐 Live Demo  
Web App: [pdf-rag-llm.vercel.app](https://pdf-rag-llm.vercel.app)  
API Docs: [qqolevsheofuqq56sccpvtun340abhod.lambda-url.us-east-1.on.aws/docs](https://qqolevsheofuqq56sccpvtun340abhod.lambda-url.us-east-1.on.aws/docs)

## 🔧 Tech Stack  
| Backend            | Frontend         | DevOps                  |  
|--------------------|------------------|-------------------------|  
| Python             | TypeScript       | AWS CDK                 |  
| LangChain          | Next.js          | Docker                  |  
| FastAPI            | Tailwind CSS     | GitHub Actions          |  
| Google Gemini API  | Vercel (Hosting) | AWS Lambda/DynamoDB/SSM |  

## 🛠️ Local Development Setup
### Prerequisites
- Python 3.11
- Node.js 18
- AWS CLI Configured
- Docker Engine Started

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
    --name "/myapp/google_api_key" \
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

   # After deployment, set the TABLE_NAME environment variable to your DynamoDB table name
   export TABLE_NAME="YourDeployedTableName"
   ``` 

3. **Run FastAPI server locally**
   ```bash
   pip install -r requirements-dev.txt
   nohup uvicorn image.src.api_handler --host 0.0.0.0 --port 8000 > server.log 2>&1
   # pkill -f uvicorn # later to stop background server
   ```
4. **Run tests**
   ```bash
   pytest
   ```
5. **Run frontend locally**
   ```bash
   # Configure frontend to connect to local backend during development
   export NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
   
   cd rag-frontend/
   npm install
   npm run dev
   ```
