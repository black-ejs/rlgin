import argparse

# Set options 
parser = argparse.ArgumentParser()
parser.add_argument("--series", nargs='?', type=str, default=None)
parser.add_argument("--params_spec", nargs='?', type=str, default=None)
parser.add_argument("--driver_id", nargs='?', type=str, default=1)
parser.add_argument("--mode", nargs='?', type=str, default="SCRATCH")
parser.add_argument("--scratch_count", nargs='?', type=int, default=20)
parser.add_argument("--scratch_start", nargs='?', type=int, default=1)
parser.add_argument("--weights_spec", nargs='?', type=str, default=None)
parser.add_argument("--train_generations", nargs='?', type=int, default=10) # run on raw vm
parser.add_argument("--lr", nargs='?', type=float, default=None)
parser.add_argument("--gamma", nargs='?', type=float, default=None)
parser.add_argument("--output_filename", nargs='?', type=str, default=None)
args = parser.parse_args()
print("job_params_generator.py: args ", args)

series=args.series
driver_id=args.driver_id

mode=args.mode
scratch_count=args.scratch_count
scratch_start=args.scratch_start

weights_spec=args.weights_spec
train_generations=args.train_generations

if not args.params_spec == None:
        params_spec=args.params_spec
else:
        params_spec=f"ginDQNParameters.py.{series}.{mode.lower()}"

if args.output_filename==None or len(args.output_filename)==0:
        output_filename=f"job-params.{series}{driver_id}.{mode.lower()}.txt"
else:
        output_filename=args.output_filename

# ####
line=""
line+=f"TRAIN_OR_SCRATCH={mode}:"
line+=f"SERIES_NICKNAME={series}:"
line+=f"SCRATCH_DRIVER_ID={driver_id}:"
line+=f"PARAMS_SPEC={params_spec}:"
if not args.lr == None:
        line+=f"LEARNING_RATE={args.lr}:"
if not args.gamma == None:
        line+=f"GAMMA={args.gamma}:"

content=""
if mode == "SCRATCH":
    for i in range(scratch_start,scratch_start+scratch_count):
        content+= line 
        content+= f"SCRATCH_DRIVER_START={i}:"
        content+= f"SCRATCH_DRIVER_END={i}\n"
elif mode == "TRAIN":
        content+= line
        content+= f"WEIGHTS_SPEC={weights_spec}:"
        content+= f"TRAIN_GENERATIONS={train_generations}\n"

with open(output_filename,"w") as f:
     f.write(content)
    
print("done.")