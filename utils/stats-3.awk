BEGIN{minratio=10000;}
/winMap:/{
        p=substr($3,1,length($3)-1); 
        if (length(p)<4) {
                t=substr($5,1,length($5)-1); 
                print "scenario-" scenario "  p=" p "  t=" t "  ratio=" p/t; 
                pp=pp+p; 
                tt=tt+t; 
                count=count+1;
                if (minratio > p/t) {
                        minratio = p/t
                }
        }
}
/name_scenario/{
        namex = index($0,"name_scenario")+20;
        scenario = substr($0, namex)
        scenario = substr(scenario,1,index(scenario,",")-1)
}
END{
        print "count=" count "   pp=" pp "   tt=" tt  "   p-avg=" pp/count "   t-avg=" tt/count "  ratio=" pp/tt "  min=" min
ratio
}
