/W[Ii][Nn][Nn][Ee][Rr]: [Pb]/ {
	pp=pp+$13; 
	f=f+1; 
	p=p+1;
}
/W[Ii][Nn][Nn][Ee][Rr]: [Tr]/ {
	pp=pp+$13; 
	f=f+1; 
	t=t+1;
}
/W[Ii][Nn][Nn][Ee][Rr]: [n]/ {
	pp=pp+$8; 
	f=f+1;
}
END {
	print      \
	      f " hands\n"  \
	      pp/f " ms/hand avg\n" \
	      t " wins\n" \
	      p " losses\n" \
	      (t*1000)/f " wins/1000 hands\n" \
	      p/t " ratio\n" \
	      f-t-p " nobody\n" \
	      ((t+p)/f)*100 "% decided \n"\
	      pp/1000 " s   " pp/60000 " m   " pp/3600000 " h" 
}

