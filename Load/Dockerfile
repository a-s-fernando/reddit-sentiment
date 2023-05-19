FROM public.ecr.aws/lambda/python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY load.py ${LAMBDA_TASK_ROOT}
COPY create_tables.sql ${LAMBDA_TASK_ROOT}
CMD ["load.lambda_handler"]
