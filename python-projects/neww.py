import os.path, argparse, sys, csv, datetime
from jira import JIRA

env_var_list = ['JIRA_USERNAME', 'JIRA_PASSWORD']
for i in env_var_list:
    if i not in os.environ:
       print("\nERROR: Environment variables %s are not set" % (', '.join(env_var_list)))
       print("\nHELP: Use export command to set environment variables\n\nEXAMPLES:\n\texport JIRA_USERNAME='MY_USER'\n\texport JIRA_PASSWORD='MY_PASSWORD'\n")
       sys.exit(1)
jira_username, jira_password = os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD']

def jira_login(jira_url, jira_username, jira_password):
    jira = JIRA(jira_url, auth=(jira_username, jira_password))
    return jira


def create_jira(jira, jira_project, jira_epic_id, jira_data):
    project = jira.project(jira_project)
    issue = jira.create_issue( fields = jira_data )
    print("%s is Created" % (issue.key))
    jira.add_issues_to_epic(jira_epic_id, [ issue.key ])

def find_all_issues_of_epic(jira, jira_project, jira_epic_id):
    all = jira.search_issues("'Epic Link' = "+jira_epic_id+" and project = '"+jira_project+"'", maxResults=False)
    all_issues = {}
    for i in all:
        if i.fields.status.name.upper() == 'CLOSED': continue
        if all_issues.get(i.fields.summary):
            all_issues[i.fields.summary].append({i.key : i.fields.description})
        else:
            all_issues[i.fields.summary] = [{i.key : i.fields.description}]
    return all_issues

parser = argparse.ArgumentParser(description="Python script to parse AMI csv")
parser.add_argument('-i', '--input_csv', help='Input CSV File Name', type=str, required=True)
parser.add_argument('-o', '--output_csv', help='Output CSV File Name', type=str, required=True)
parser.add_argument('-a', '--ami_days', help='AWS AMI Days Column Value', type=int, required=True)
parser.add_argument('-j', '--jira_url', help='JIRA Server URL', type=str, required=True)
parser.add_argument('-p', '--jira_project', help='JIRA Project, e.g. CYBRIP', type=str, required=True)
parser.add_argument('-e', '--jira_epic_id', help='JIRA Epic ID, e.g. CYBRIP-1234', type=str, required=True)
args = parser.parse_args()

try: jira = jira_login(jira_url=args.jira_url, jira_username=jira_username, jira_password=jira_password)
except:
    print("ERROR: Unable to login to JIRA server")
    sys.exit(1)


all_issues = find_all_issues_of_epic(jira=jira, jira_project=args.jira_project, jira_epic_id=args.jira_epic_id)

file_exists = os.path.isfile(args.input_csv)
if not file_exists:
    print("ERROR: Input CSV %s does not exists. Check -i value and try again." % (args.input_csv) )
    sys.exit(1)
headers_in_output = "Account,environment,Region,InstanceId,ASV,BA,CMDBEnvironment,OwnerContact,BusOwner,DevOwner,SrvOwner,InstanceName,InstanceType,AMIId,AMIName,AMIDate,AMI_Days,IPAddress,ASGroup,Division"
headers_in_output = headers_in_output.split(',')
headers_index = []

my_dict = {'esic': 'ESIC', 'recovery': 'Recovery', 'forgots': 'Forgots', 'enrllapp': 'Enrollment', 'chalgapp': 'ChallengeApp', 'fraudfix': 'Fraudfix', 'sic': 'Sic', 'epciscic': 'epciscic', 'oigw': 'OIGW', 'deflapp': 'DeflectionApp', 'swiftid': 'SwitftId'}
with open(args.input_csv) as csvfile:
    file = csv.reader(csvfile)
    headers = next(file)
    for i,v in enumerate(headers):
        if v in headers_in_output:
            headers_index.append(i) 
            if v == 'InstanceName':
                Instance_index = i
            elif v == 'InstanceId':
                Instance_id_index = i
            elif v == 'AMI_Days':
                Ami_index = i
            elif v == 'Division':
                Division_index = i
            elif v == 'ASV':
                ASV_name = i
            elif v == 'Account':
                Account_name = i
    if len(headers_in_output) != len(headers_index):
        print("ERROR: Give input CSV %s does not have required headers.\n\nRequired headers are -" % (args.input_csv) )
        for i in headers_in_output: print("\t- %s" % (i) )
        sys.exit(1)
    headers_in_output.append('Target_Date_55_days')
    headers_in_output.append('60_Days')
    headers_in_output.append('App_name')
    headers_in_output.append('LOB')
    outfile = open(args.output_csv, 'w')
    writer = csv.writer(outfile)
    writer.writerow(headers_in_output)
    jira_data_all = {}
    tickets_to_update = {}
    for line in file:
        try: 
            days = int(line[Ami_index].strip())
            division = line[Division_index].strip()
            instance_name = line[Instance_index].strip()
            instance_id = line[Instance_id_index].strip()
            a_name = line[ASV_name].strip()
            lob = line[Account_name].strip()
            if days >= args.ami_days and division == 'Cyber' and '-' in instance_name and (instance_name.startswith('bwaf') or instance_name.startswith('CudaWAF') or a_name == 'ASVBAMANAGEDPERIMETER') :
                app_name = instance_name.strip().split('-')[1]
                lob = lob.split('-')[1]
                if a_name == 'ASVCONSUMERIDENTITYSERVICES':
                    for k in my_dict.keys() :
                        if app_name == k:
                            app_name = my_dict[k]
                AMIDate = datetime.datetime.strptime(line[22].strip(), "%Y-%m-%dT%H:%M:%SZ")
                row = []
                for i in headers_index:
                    row.append(line[i].strip())
                end_date_55 = AMIDate + datetime.timedelta(days=55)
                row.append(end_date_55.strftime('%Y-%m-%d'))
                end_date = AMIDate + datetime.timedelta(days=60)
                row.append(end_date.strftime('%Y-%m-%d'))
                row.append(app_name)
                row.append(lob)
                writer.writerow(row)
                summary = "%s-%s-%s-Rehydration" % (lob.upper(), a_name.upper(), app_name.upper())
                rec_table = """
||Attribute||Value||
|Instance Id|%s|
|Instance Name|%s|
|AMI Days|%s|
|Target End date|%s
""" % (instance_id, instance_name, days, end_date_55)
                if all_issues.get(summary):
                    already_in = False
                    for t in all_issues[summary]:
                        jira_desc = list(t.values())[0]
                        if instance_id in jira_desc:
                            already_in = True
                    if not already_in:
                        jira_id = list(all_issues[summary][0].keys())[0]
                        jira_desc = list(all_issues[summary][0].values())[0]
                        if tickets_to_update.get(jira_id):
                            tickets_to_update[jira_id] = tickets_to_update[jira_id] + '\n\n' + rec_table
                        else:      
                            tickets_to_update[jira_id] = jira_desc + '\n\n' + rec_table
                    continue
                if jira_data_all.get(summary):
                    jira_data_all[summary].append(rec_table)
                else:
                    jira_data_all[summary] = [rec_table]
        except ValueError: pass
outfile.close()


for k, v in jira_data_all.items():
    jira_data = { 'project': {'key': args.jira_project} }
    jira_data['summary'] = k
    jira_data['issuetype'] = { 'name': 'Story' }
    jira_data['priority'] = { 'name': 'P3'}
    jira_data['description'] = "*Rehydration Process* can be [found on Confluence.|http://example.com/]\n\n*Description:*\n\n%s" % ('\n\n'.join(v))
    create_jira(jira=jira, jira_project=args.jira_project, jira_epic_id=args.jira_epic_id, jira_data=jira_data)

for k, v in tickets_to_update.items():
    issue = jira.issue(k)
    issue.update(description=v)
sys.exit(0)
