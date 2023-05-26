# reddit-sentiment

![Social Sleuth]([social_sleuth.png](https://i.ibb.co/bLZpf7W/Screenshot-2023-05-26-at-11-07-33.png))

## Description

### What does this do?

- This project analyses the change in sentiment towards various entities like companies or concepts over time.
- This sentiment is gauged based on comments extracted using the **Reddit API**.

### What are the goals?

- Our aim is to analyse how sentiment changes over time for various entities such as individuals, companies, technologies, and locations.
- We hope that useful visualisations of such trends can help inform our users.

### Who is this for?

- **Organisations**
  - This tool can gauge sentiment on other companies, products, and potential technologies useful for informing design and business decisions.
- **The curious**
  - As well as informing the common consumer, the information provided can provide fascinating cultural and societal insights.

---

## Features

- Provision necessary cloud resources in **one command**.
- Automatically extract data from the **Reddit API** every 30 minutes.
- Serverless scripts to perform NLP on extracted data.
- Visualisations provided through **Dash**, hosted on **Fargate**.
  - Sentiment trends for inputted keywords.
  - Leaderboard of most popular and unpopular keywords.
  - Sentiment towards specific concepts

---

## Data Collected

- Post titles
- Comments
- Keywords
- Post dates
- Sentiment
- Scores

---

## Behind the Scenes

The backend of this project consists of two python files, `app.py` and `load.py`, and a SQL script `create_tables.sql`.

`app.py` is responsible for extracting data from the Reddit API and storing it in an S3 bucket. It utilises PRAW (Python Reddit API Wrapper) and NLTK's VADER (Valence Aware Dictionary for Sentiment Reasoning) for sentiment analysis.

`load.py` is a script that loads the data into PostgreSQL tables. It downloads the data from the S3 bucket, connects to the PostgreSQL database, creates the necessary tables using the `create_tables.sql` file, and then populates these tables with the data.

The `create_tables.sql` file is located in the Load directory. It contains SQL commands to create tables for storing the extracted data.

These scripts are customisable through the use of the environment variables defined in the **Terraform** section.

---

## Setting up the API

To start with the project, follow these steps:

1. Set up your Reddit API by going to `https://www.reddit.com/prefs/apps`
2. Navigate to `http://localhost:8080`
3. Get your **ID** and **secret key**. These will correspond to the `client_id` and `client_secret` variables used by **Terraform**.

---

## Terraform

As aforementioned, this project uses [Terraform](https://www.terraform.io/) in order to set up our cloud infrastructure.
After ensuring that **Terraform** is installed, please add the following variables to a `.tfvars` file:

```
username = "Your desired database username."
password = "Your desired database password."
database_name = "Your desired database name."
access_key = "Your AWS access key."
secret_key = "Your AWS secret key."
region_name = "Your AWS region."
user_agent = "The user agent name you wish to use the Reddit API as."
client_id = "Your reddit client id."
client_secret = "Your reddit client secret."
num_posts = "The number of posts you wish to extract from every 30 minutes. Values that are too high may cause the serverless function to fail due to time limitations."
subreddit_name = "The name of the subreddit you wish to access."
bucket_name = "Your desired S3 bucket name."
```

The architecture can then be provisioned using the following command:

`terraform apply -var-file=".tfvars" -auto-approve`

---

## Future Aims

- Train a model to predict sentiment and trends based on posts.
- Analyse a potential correlation between sentiment and stock price.
