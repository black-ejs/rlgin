import time
import json
import argparse

from google.cloud import batch_v1

# ###################################
def create_script_job_with_template(template_link: str, 
                                    script: str, 
                                    num_tasks: int,
                                    parallelism: int,
                                    params_path: str,
                                    env: dict=None) -> batch_v1.Job:
    """
    This method shows how to create a sample Batch Job that will run
    a simple command on Cloud Compute instances created using a provided Template.

    Args:
        template_link: a link to an existing Instance Template. Acceptable formats:
            * "projects/{project_id}/global/instanceTemplates/{template_name}"
            * "{template_name}" - if the template is defined in the same project as used to create the Job.

    Returns:
        A job object representing the job created.
    """
    # Define what will be done as part of the job.
    task = batch_v1.TaskSpec()
    runnable = batch_v1.Runnable()

    runnable.script = batch_v1.Runnable.Script()
    runnable.script.text = script
    # You can also run a script from a file. Just remember, that needs to be a script that's
    # already on the VM that will be running the job. Using runnable.script.text and runnable.script.path is mutually
    # exclusive.
    # runnable.script.path = '/tmp/test.sh'

    env_vars = {}
    if params_path == None:
        params_path = "."
    env_vars["RLGIN_BATCH_JOB_PARAMS_PATH"] = params_path
    if env != None:
        env_vars.update(env)
    runnable.environment = batch_v1.Environment()
    runnable.environment.variables = env_vars

    task.runnables = [runnable]

    # We can specify what resources are requested by each task.
    resources = batch_v1.ComputeResource()
    resources.cpu_milli =  1500  # in ms per cpu-second. 1000 means the task requires 1 whole vCPU
    resources.memory_mib = 2000 
    task.compute_resource = resources

    task.max_retry_count = 2
    task.max_run_duration = "360000s"  # 100 hrs

    # Tasks are grouped inside a job using TaskGroups.
    # Currently, it's possible to have only one task group.
    group = batch_v1.TaskGroup()
    group.task_count = num_tasks
    group.task_spec = task
    group.parallelism = parallelism

    # Policies are used to define on what kind of virtual machines the tasks will run on.
    # In this case, we tell the system to use an instance template that defines all the
    # required parameters.
    allocation_policy = batch_v1.AllocationPolicy()
    instances = batch_v1.AllocationPolicy.InstancePolicyOrTemplate()
    instances.instance_template = template_link
    allocation_policy.instances = [instances]

    job = batch_v1.Job()
    job.task_groups = [group]
    job.allocation_policy = allocation_policy
    job.labels = {"env": "testing", "type": "script"}
    # We use Cloud Logging as it's an out of the box available option
    job.logs_policy = batch_v1.LogsPolicy()
    job.logs_policy.destination = batch_v1.LogsPolicy.Destination.CLOUD_LOGGING

    return job

# ###################################
def create_job_request(job: batch_v1.Job, 
                       project_id: str, 
                       region: str, 
                       job_name: str) -> batch_v1.Job:
    """
    Args:
        job: the batch_v1.Job with the tasks, scripts, containters, templates, etc. 
            ready for submission
        job_name: the name of the job that will be created.
            It needs to be unique for each project and region pair.
        project_id: project ID or project number of the Cloud project you want to use.
        region: name of the region you want to use to run the job. Regions that are
            available for Batch are listed on: https://cloud.google.com/batch/docs/get-started#locations
    """
    create_request = batch_v1.CreateJobRequest()
    create_request.job = job
    create_request.job_id = job_name
    # The job's parent is the region in which the job will run
    create_request.parent = f"projects/{project_id}/locations/{region}"

    return create_request

# ###################################
def submit_job_request(create_request: batch_v1.CreateJobRequest) -> batch_v1.Job:
    client = batch_v1.BatchServiceClient()

    return client.create_job(create_request)

# ###################################
def create_boot_script(run_script:str, 
                        saveto_name="rb-generated-script.sh") -> str:

    if run_script == None:
        run_script = ""

    run_script = run_script.replace("'","\'")
    saveto_path =  "/home/${RLGIN_BATCH_USER}/" +saveto_name +"_${BATCH_TASK_INDEX}"

    boot_script  =  "#!/bin/bash\n"
    boot_script +=  "\n#>>> created by job generator\n"
    boot_script +=  "\nrb_save_run_script() {\n" 
    #boot_script += f"\necho saveto_path={saveto_path}\n"
    #boot_script += f"\necho run_script, fixed up, is: '->$'{run_script}'<-'\n" 
    boot_script += f"\nexport RLGIN_BATCH_JOB_SCRIPT={saveto_path}"
    boot_script += f"\necho $'{run_script}' >> " + "${RLGIN_BATCH_JOB_SCRIPT}"
    boot_script +=  "\nchmod a+x ${RLGIN_BATCH_JOB_SCRIPT}"
    boot_script +=  "\necho RLGIN_BATCH_JOB_SCRIPT=${RLGIN_BATCH_JOB_SCRIPT}"
    boot_script +=  "\n}\n"
    boot_script +=  "\n#>>> end created by job generator\n"
    boot_script +=  "\n"

    inline_script_loc="/Users/edward/Documents/dev/projects/rlgin/utils/rlgin-batch/gcloud-config"
    inline_script=".job-script"
    with open(f"{inline_script_loc}/{inline_script}") as scriptfile:
        boot_script += scriptfile.read()
    
    return boot_script
        

# ###################################
def create_standard_job_request(params_path: str, 
                                num_tasks: int,
                                parallelism: int,
                                env: dict, 
                                region:str,
                                script:str,
                                template_name:str,
                                project_id:str) -> batch_v1.CreateJobRequest:

    ts=f"{time.time()}".replace('.','-')[-9:]
    job_name = f"rb-job-{params_path.lower()}-{ts}"
    job_name = job_name.replace('.','-')
    job_name = job_name.replace('_','-')
    job_name = job_name.replace('/','-')

    boot_script = create_boot_script(script)
     
    template_link = f"projects/{project_id}/global/instanceTemplates/{template_name}"
    job = create_script_job_with_template(template_link, 
                                          boot_script, 
                                          num_tasks,
                                          parallelism,
                                          params_path, 
                                          env)
    #dump(job,"-------- job before request")

    create_request = create_job_request(job,
                                        project_id,
                                        region,
                                        job_name)
    return create_request

# ###################################
def dump(obj,label:str=None):
    if not label==None:
        print(label)

    for att in dir(obj):
        if not "__" in att:
            print (f"\"{att}\": {getattr(obj,att)}")

def to_json(obj):
    json.dumps(obj,indent=4)

## #############################################
## #############################################
## #############################################
## #############################################
## #############################################
if __name__ == '__main__':

    # Set options 
    parser = argparse.ArgumentParser()
    parser.add_argument("--params_path", nargs='?', type=str, default=None)
    parser.add_argument("--num_tasks", nargs='?', type=int, default=1)
    parser.add_argument("--parallelism", nargs='?', type=int, default=1)
    parser.add_argument("--region", nargs='?', type=str, default="us-central1")
    parser.add_argument("--vm_template", nargs='?', type=str, default="rb-c2d-2x8-template-7")
    parser.add_argument("--script", nargs='?', type=str, default="./rb-run-param-job.sh")
    parser.add_argument("--scriptfile", nargs='?', type=str, default=None)
    parser.add_argument("--scriptraw", nargs='?', type=int, default=False) # run on raw vm
    parser.add_argument("--env", nargs='?', type=str, default=None)
    parser.add_argument("--project", nargs='?', type=str, default="rlgin-batch-384320")
    parser.add_argument("--max_duration", nargs='?', type=int, default=360000)
    args = parser.parse_args()
    print("generateJob: args ", args)

    if (args.params_path == None):
        print(("  please supply a path to the folder containing the\n" 
               "  job-parameters.txt file using the --params_path option.\n" 
               "  path is relative to ~/dev/projects/rlgin-batch/job-parameters\n" 
               "  this value will be passed to the script\n"
               "  as environment var RLGIN_BATCH_JOB_PARAMS_PATH"))
        exit()

    create_request = create_standard_job_request(args.params_path, 
                                                args.num_tasks,
                                                args.parallelism,
                                                args.env,
                                                args.region,
                                                args.script,
                                                args.vm_template,
                                                args.project)
    
    #dump(create_request,"-------- create_request")
    
    submitted = submit_job_request(create_request)
    dump(submitted,"-------- submitted")
