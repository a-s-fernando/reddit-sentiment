terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}


# Designating variables
variable "access_key" {
  description = "Access key for AWS."
  type = string
}

variable "secret_key" {
  description = "Secret key for AWS."
  type = string
}

variable "region_name" {
  description = "region name for AWS."
  type = string
}

variable "username" {
  description = "Username for the database"
  type = string
}

variable "database_name" {
  description = "Name of the database"
  type = string
}

variable "password" {
  description = "Password for the database"
  type = string
}

variable "user_agent" {
  description = "Agent name for using the Reddit API."
  type = string
}

variable "client_id" {
  description = "Client ID for the Reddit API."
  type = string
}

variable "client_secret" {
  description = "Client secret for the Reddit API."
  type = string
}

variable "num_posts" {
  description = "Number of posts for the Reddit API."
  type = string
}

variable "subreddit_name" {
  description = "Name of subreddit for the Reddit API."
  type = string
}

variable "bucket_name" {
  description = "Name of s3 bucket."
  type = string
}


# Configure AWS provider
provider "aws" {
  access_key = var.access_key
  secret_key = var.secret_key
  region     = var.region_name
}


# Use an existing VPC
data "aws_vpc" "c7-vpc" {
  id = "vpc-010fd888c94cf5102"
}


# Use an existing subnet
data "aws_db_subnet_group" "c7-subnets" {
  name = "c7-db-subnet-group"
}


# Use an existing security group
data "aws_security_group" "c7-remote-access" {
  name   = "c7-remote-access"
  vpc_id = data.aws_vpc.c7-vpc.id
  id     = "sg-01745c9fa38b8ed68"
}


# Create an RDS database
resource "aws_db_instance" "sentiment-db" {
  identifier        = "sentiment-db"
  engine            = "postgres"
  engine_version    = "14.1"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  username          = var.username
  password          = var.password
  # Make the database public.
  publicly_accessible    = true
  skip_final_snapshot = true
  db_subnet_group_name   = data.aws_db_subnet_group.c7-subnets.name
  vpc_security_group_ids = [data.aws_security_group.c7-remote-access.id]
}


# Create S3 bucket
resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name
}


# Create lambda IAM policy
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}


# Create lambda IAM role
resource "aws_iam_role" "lambda-role" {
  name_prefix = "iam-sentiment-for-lambda"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [{
      "Action" : "sts:AssumeRole",
      "Principal" : {
        "Service" : "lambda.amazonaws.com"
      },
      "Effect" : "Allow"
    }]
  })
}


# Create lambda extraction function
resource "aws_lambda_function" "sentiment-extract" {
  function_name = "sentiment-extract"
  role          = aws_iam_role.lambda-role.arn
  memory_size   = 3010
  timeout       = 900
  image_uri     = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/sentiment-extract:latest"
  package_type  = "Image"
  architectures = ["arm64"]
  environment {
    variables = {
      user_agent  = var.user_agent
      client_id   = var.client_id
      client_secret = var.client_secret
      subreddit_name = var.subreddit_name
      num_posts = var.num_posts
      bucket_name = var.bucket_name
      access_key = var.access_key
      secret_access_key = var.secret_key
      region_name = var.region_name
    }
  }
}


# Create lambda loading function
resource "aws_lambda_function" "sentiment-load" {
  function_name = "sentiment-load"
  role          = aws_iam_role.lambda-role.arn
  memory_size   = 3010
  timeout       = 900
  image_uri     = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/sentiment-load:latest"
  package_type  = "Image"
  architectures = ["arm64"]
  environment {
    variables = {
      DB_USER     = var.username
      DB_PASSWORD = var.password
      DB_NAME     = var.database_name
      DB_HOST     = aws_db_instance.sentiment-db.address
      DB_PORT     = aws_db_instance.sentiment-db.port
      bucket_name = var.bucket_name
      access_key = var.access_key
      secret_access_key = var.secret_key
      region_name = var.region_name
    }
  }
}


# Create an IAM role for Step Functions Event Bridge
resource "aws_iam_role" "sentiment-event-bridge-role" {
  name = "sentiment-event-bridge-role"
  assume_role_policy = <<POLICY1
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Principal" : {
        "Service" : "events.amazonaws.com"
      },
      "Action" : "sts:AssumeRole"
    }
  ]
}
POLICY1
}


# Create an IAM role for Step Functions State Machine
resource "aws_iam_role" "sentiment-state-machine-role" {
  name = "sentiment-state-machine-role"
  assume_role_policy = <<POLICY2
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Principal" : {
        "Service" : "states.amazonaws.com"
      },
      "Action" : "sts:AssumeRole"
    }
  ]
}
POLICY2
}


# Create an IAM policy for Eventbridge to be able to start a Step Function execution
resource "aws_iam_policy" "sentiment-event-bridge-policy" {
  name = "sentiment-event-bridge-policy"
  policy = <<POLICY3
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : [
        "states:StartExecution"
      ],
      "Resource" : "${aws_sfn_state_machine.sfn_state_machine.arn}"
    }
  ]
}
POLICY3
}


# Create an IAM policy to enable Step Function State Machine to push logs to CloudWatch logs
resource "aws_iam_policy" "sentiment-state-machine-log-delivery-policy" {
  name = "sentiment-state-machine-log-delivery-policy"
  policy = <<POLICY4
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : [
        "logs:CreateLogDelivery",
        "logs:GetLogDelivery",
        "logs:UpdateLogDelivery",
        "logs:DeleteLogDelivery",
        "logs:ListLogDeliveries",
        "logs:PutResourcePolicy",
        "logs:DescribeResourcePolicies",
        "logs:DescribeLogGroups"
      ],
      "Resource" : "*"
    }
  ]
}
POLICY4
}


# Create an IAM policy to enable Step Function State Machine to invoke lambda functions
resource "aws_iam_policy" "sentiment-state-machine-lambda-policy" {
  name = "sentiment-state-machine-lambda-policy"
  policy = <<POLICY5
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : [
        "lambda:InvokeFunction"
      ],
      "Resource" : [
        "${aws_lambda_function.sentiment-extract.arn}",
        "${aws_lambda_function.sentiment-load.arn}"
      ]
    }
  ]
}
POLICY5
}


# Attach the IAM policies to the equivalent rule
resource "aws_iam_role_policy_attachment" "sentiment-event-bridge-policy-attachment" {
  role       = aws_iam_role.sentiment-event-bridge-role.name
  policy_arn = aws_iam_policy.sentiment-event-bridge-policy.arn
}

resource "aws_iam_role_policy_attachment" "sentiment-state-machine-policy-attachment" {
  role       = aws_iam_role.sentiment-state-machine-role.name
  policy_arn = aws_iam_policy.sentiment-state-machine-log-delivery-policy.arn
}

resource "aws_iam_role_policy_attachment" "sentiment-state-machine-lambda-policy-attachment" {
  role       = aws_iam_role.sentiment-state-machine-role.name
  policy_arn = aws_iam_policy.sentiment-state-machine-lambda-policy.arn
}


# Create an Log group for the Step Function
resource "aws_cloudwatch_log_group" "MyLogGroup" {
  name = "sentiment-log-group"
}


# Create Step Function State Machine
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "sentiment-step-function"
  role_arn = aws_iam_role.sentiment-state-machine-role.arn

  definition = <<EOF
  {
    "Comment": "Invoke AWS Lambda from AWS Step Functions with Terraform",
    "StartAt": "Extract",
    "States": {
      "Extract": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.sentiment-extract.arn}",
        "Next": "Load"
      },
      "Load" : {
        "Type": "Task",
        "Resource": "${aws_lambda_function.sentiment-load.arn}",
        "End": true
      }
    }
  }
  EOF

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.MyLogGroup.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }
}


# Create schedule event rule to use for our step function 
resource "aws_cloudwatch_event_rule" "sentiment-schedule-step-function" {
  name                = "sentiment-schedule-step-function"
  schedule_expression = "rate(30 minutes)"
  description = "Rule that triggers every 30 minutes, created for the reddit-sentiment project."
  role_arn = aws_iam_role.sentiment-event-bridge-role.arn
}


# Create a schedule target for our schedule rule
resource "aws_cloudwatch_event_target" "schedule-target-sentiment" {
  rule = aws_cloudwatch_event_rule.sentiment-schedule-step-function.name
  arn  = aws_sfn_state_machine.sfn_state_machine.arn
  role_arn = aws_iam_role.sentiment-event-bridge-role.arn
}


# Create Elastic Container Service Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.name}-cluster-${var.environment}"
}


# Create Elastic Container Service task
resource "aws_ecs_task_definition" "main" {
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  container_definitions = jsonencode([{
   name        = "${var.name}-container-${var.environment}"
   image       = "${var.container_image}:latest"
   essential   = true
   environment = var.container_environment
   portMappings = [{
     protocol      = "tcp"
     containerPort = var.container_port
     hostPort      = var.container_port
   }]
  }])
}

# Create ecs task role 
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.name}-ecsTaskRole"
 
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "ecs-tasks.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}


# Create ecs task execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.name}-ecsTaskExecutionRole"
 
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "ecs-tasks.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}
 
resource "aws_iam_role_policy_attachment" "ecs-task-execution-role-policy-attachment" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_ecs_service" "main" {
 name                               = "${var.name}-service-${var.environment}"
 cluster                            = aws_ecs_cluster.main.id
 task_definition                    = aws_ecs_task_definition.main.arn
 desired_count                      = 2
 deployment_minimum_healthy_percent = 50
 deployment_maximum_percent         = 200
 launch_type                        = "FARGATE"
 scheduling_strategy                = "REPLICA"
 
 network_configuration {
   security_groups  = var.ecs_service_security_groups
   subnets          = var.subnets.*.id
   assign_public_ip = false
 }
 
 load_balancer {
   target_group_arn = var.aws_alb_target_group_arn
   container_name   = "${var.name}-container-${var.environment}"
   container_port   = var.container_port
 }
 
 lifecycle {
   ignore_changes = [task_definition, desired_count]
 }
}

resource "aws_lb" "main" {
  name               = "${var.name}-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.alb_security_groups
  subnets            = var.subnets.*.id
 
  enable_deletion_protection = false
}
 
resource "aws_alb_target_group" "main" {
  name        = "${var.name}-tg-${var.environment}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
 
  health_check {
   healthy_threshold   = "3"
   interval            = "30"
   protocol            = "HTTP"
   matcher             = "200"
   timeout             = "3"
   path                = var.health_check_path
   unhealthy_threshold = "2"
  }
}

resource "aws_alb_listener" "http" {
  load_balancer_arn = aws_lb.main.id
  port              = 80
  protocol          = "HTTP"
 
  default_action {
   type = "redirect"
 
   redirect {
     port        = 443
     protocol    = "HTTPS"
     status_code = "HTTP_301"
   }
  }
}
 
resource "aws_alb_listener" "https" {
  load_balancer_arn = aws_lb.main.id
  port              = 443
  protocol          = "HTTPS"
 
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.alb_tls_cert_arn
 
  default_action {
    target_group_arn = aws_alb_target_group.main.id
    type             = "forward"
  }
}

resource "aws_ecr_repository" "sentiment-dash" {
  name                 = "sentiment-dash"
  image_tag_mutability = "MUTABLE"
}
