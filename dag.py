# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from airflow.operators.email import EmailOperator
# from datetime import datetime
# from github import Github

# # Function to send email
# def send_email(**context):
#     # Get the task instance
#     ti = context['task_instance']
    
#     # Retrieve the GitHub event information from the task instance
#     github_event = ti.xcom_pull(task_ids='github_event')

#     # Compose the email content
#     email_subject = "New GitHub Push Event"
#     email_body = f"Repository: {github_event.repository}\n" \
#                  f"Pusher: {github_event.pusher}\n" \
#                  f"Timestamp: {github_event.timestamp}\n" \
#                  f"Commits: {github_event.commits}"
    
#     # Send the email
#     email_operator = EmailOperator(
#         task_id='send_email_task',
#         to='i190441@nu.edu.pk',
#         subject=email_subject,
#         html_content=email_body,
#     )
#     email_operator.execute(context)

# # Function to retrieve GitHub push event
# def get_github_push_event(**context):
#     # Your GitHub access token
#     access_token = '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'
    
#     # Create a GitHub instance using the access token
#     g = Github(access_token)
    
#     # Get the repository
#     repository = g.get_repo('https://github.com/Abdullah476/FYP-F22-101-D-GoogleTalk.git')
    
#     # Get the latest push event
#     push_event = repository.get_events().get_page(0)[0]
    
#     # Extract relevant information from the push event
#     pusher = push_event.actor.login
#     timestamp = push_event.created_at.strftime("%Y-%m-%d %H:%M:%S")
#     commits = [commit.commit.message for commit in push_event.payload['commits']]
    
#     # Define a class to store the GitHub event information
#     class GitHubEvent:
#         def __init__(self, repository, pusher, timestamp, commits):
#             self.repository = repository
#             self.pusher = pusher
#             self.timestamp = timestamp
#             self.commits = commits
    
#     # Create an instance of the GitHubEvent class
#     github_event = GitHubEvent(repository.full_name, pusher, timestamp, commits)
    
#     # Push the GitHub event information to XCom
#     context['task_instance'].xcom_push(key='github_event', value=github_event)

# # Define the DAG
# with DAG(
#     'github_push_email_workflow',
#     start_date=datetime(2023, 6, 11),
#     schedule_interval='*/1 * * * *',  # Run every 5 minutes
# ) as dag:

#     # Task to retrieve GitHub push event
#     get_github_push_event_task = PythonOperator(
#         task_id='get_github_push_event_task',
#         python_callable=get_github_push_event,
#         provide_context=True,
#     )

#     # Task to send email
#     send_email_task = PythonOperator(
#         task_id='send_email_task',
#         python_callable=send_email,
#         provide_context=True,
#     )

#     # Define task dependencies
#     get_github_push_event_task >> send_email_task


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime
import requests

# Function to send email
def send_email(**context):
    # Get the task instance
    ti = context['task_instance']
    
    # Retrieve the GitHub event information from the task instance
    github_event = ti.xcom_pull(task_ids='github_event')

    # Compose the email content
    email_subject = "New GitHub Push Event"
    email_body = f"Repository: {github_event['repository']}\n" \
                 f"Pusher: {github_event['pusher']}\n" \
                 f"Timestamp: {github_event['timestamp']}\n" \
                 f"Commits: {github_event['commits']}"
    
    # Send the email
    email_operator = EmailOperator(
        task_id='send_email_task',
        to='i190441@nu.edu.pk',
        subject=email_subject,
        html_content=email_body,
    )
    email_operator.execute(context)

# Function to retrieve GitHub push event
def get_github_push_event(**context):
    # Your GitHub access token
    access_token = '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'
    
    # GitHub API URL
    api_url = 'https://api.github.com/repos/Abdullah476/FYP-F22-101-D-GoogleTalk/events'
    
    # Set the request headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Send a GET request to the GitHub API
    response = requests.get(api_url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Get the latest push event
        push_event = response.json()[0]
        
        # Extract relevant information from the push event
        pusher = push_event['actor']['login']
        timestamp = push_event['created_at']
        commits = [commit['message'] for commit in push_event['payload']['commits']]
        
        # Create a dictionary to store the GitHub event information
        github_event = {
            'repository': 'Abdullah476/FYP-F22-101-D-GoogleTalk',
            'pusher': pusher,
            'timestamp': timestamp,
            'commits': commits
        }
        
        # Push the GitHub event information to XCom
        context['task_instance'].xcom_push(key='github_event', value=github_event)
    else:
        raise Exception(f"Failed to retrieve GitHub events. Status code: {response.status_code}")

# Define the DAG
with DAG(
    'github_push_email_workflow',
    start_date=datetime(2023, 6, 11),
    schedule ='*/1 * * * *',  # Run every 5 minutes
) as dag:

    # Task to retrieve GitHub push event
    get_github_push_event_task = PythonOperator(
        task_id='get_github_push_event_task',
        python_callable=get_github_push_event,
    )

    # Task to send email
    send_email_task = PythonOperator(
        task_id='send_email_task',
        python_callable=send_email,
    )

    # Define task dependencies
    get_github_push_event_task >> send_email_task
