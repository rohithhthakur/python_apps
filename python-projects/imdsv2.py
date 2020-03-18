import requests

headers = {
    'X-aws-ec2-metadata-token-ttl-seconds': '21600',
}

response = requests.put('http://169.254.169.254/latest/api/token', headers=headers)
token = response.text




headers = {
    'X-aws-ec2-metadata-token':  token,
}

response = requests.get('http://169.254.169.254/latest/meta-data/ami-id', headers=headers)


print("AMI-ID using IMDSv2 - %s" % (response.text))


