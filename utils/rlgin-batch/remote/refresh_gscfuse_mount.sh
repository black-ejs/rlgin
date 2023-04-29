#!/bin/bash
gcloud compute instances list | grep RUNN | awk '
	{
		host=$1; 
		p = "echo !gcloud storage ls -l -r gs://rb-series-shared-bucket-1 | grep \"[.]log$\"";
		p = p  " \| awk <{u=substr($3,index($3,\"projects\")); print \"dev/\" u;}< " 
		p = p  " \| xargs wc -l! \| awk -f ~/escape-sq.awk > /tmp/freferr.ss; cat /tmp/freferr.ss \| ~/gssh.sh " host 
		#print "++++++ " p
		gsub("!","\047",p)
		#gsub("\"","",p) 
		print "       " p
	}
	'

