FROM public.ecr.aws/lambda/python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY app.py ${LAMBDA_TASK_ROOT}
CMD ["app.lambda_handler"]
