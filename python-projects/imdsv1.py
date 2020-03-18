import requests

response = requests.get('http://169.254.169.254/latest/meta-data/ami-id')

print("AMI-ID using IMDSv1 - %s" % (response.text))
