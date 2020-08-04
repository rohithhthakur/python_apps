import os.path, argparse, sys, csv, datetime

parser = argparse.ArgumentParser(description="Python script to parse AMI csv")
parser.add_argument('-i', '--input_csv', help='Input CSV File Name', type=str, required=True)
parser.add_argument('-o', '--output_csv', help='Output CSV File Name', type=str, required=True)
parser.add_argument('-ami_days', '--ami_days', help='AWS AMI Days Column Value', type=int, required=True)
args = parser.parse_args()



file_exists = os.path.isfile(args.input_csv)
if not file_exists:
    print("ERROR: Input CSV %s does not exists. Check -i value and try again." % (args.input_csv) )
    sys.exit(1)

headers_in_output = "Account,environment,Region,InstanceId,ASV,BA,CMBDEnv,Ownercontact,Busowner,devowner,srvgowner,InstanceName,InstanceType,AMIid,AMIname,AMIDate,AMI_Days,IPAddress,ASGroup,Division"
headers_in_output = headers_in_output.split(',')
headers_index = []



with open(args.input_csv) as csvfile:
    file = csv.reader(csvfile)

    headers = next(file)
    for i,v in enumerate(headers):
        if v in headers_in_output:
            headers_index.append(i) 
    if len(headers_in_output) != len(headers_index):
        print("ERROR: Give input CSV %s does not have required headers.\n\nRequired headers are -" % (args.input_csv) )
        for i in headers_in_output: print("\t- %s" % (i) )
        sys.exit(1)
    headers_in_output.append('Target_Date')
    outfile = open(args.output_csv, 'w')
    writer = csv.writer(outfile)
    writer.writerow(headers_in_output)
    for line in file:
        try: 
            days = int(line[23].strip())
            division = line[48].strip()
            instance_name = line[18].strip()
            if days >= args.ami_days and division == 'Cyber' and ( instance_name.startswith('bwaf') or instance_name.startswith('CudaWAF') ) :
                AMIDate = datetime.datetime.strptime(line[22].strip(), "%Y-%m-%dT%H:%M:%SZ")
                row = []
                for i in headers_index:
                    row.append(line[i].strip())
                end_date = AMIDate + datetime.timedelta(days=60)
                row.append(end_date.strftime('%Y-%m-%d'))
                writer.writerow(row)
        except ValueError: pass

outfile.close()
sys.exit(0)
