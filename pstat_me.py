
import sys
import pstats
from pstats import SortKey

if __name__ == "__main__":
	print("doo-doo")
	print(sys.argv)
	input_file = sys.argv[1]
	output_file = f"{input_file}.pstat"
	if len(sys.argv)>2:
		output_file = sys.argv[2]
	
	with open(output_file, 'w') as o: 
		p = pstats.Stats(input_file, stream=o)
		p.sort_stats('tottime').print_stats()
	
