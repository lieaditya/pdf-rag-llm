FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --use-deprecated=legacy-resolver

# For local testing
EXPOSE 8000

# Environment variables
ENV IS_USING_IMAGE_RUNTIME=True

# Copy necessary files
COPY src/* ${LAMBDA_TASK_ROOT}
COPY src/pdf_qa ${LAMBDA_TASK_ROOT}/pdf_qa
COPY src/utils ${LAMBDA_TASK_ROOT}/utils
COPY src/data/chroma ${LAMBDA_TASK_ROOT}/data/chroma
