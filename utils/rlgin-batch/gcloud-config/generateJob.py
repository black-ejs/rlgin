import time
from google.cloud import batch_v1


def create_script_job_with_template(project_id: str, region: str, job_name: str, template_link: str) -> batch_v1.Job:
    """
    This method shows how to create a sample Batch Job that will run
    a simple command on Cloud Compute instances created using a provided Template.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        region: name of the region you want to use to run the job. Regions that are
            available for Batch are listed on: https://cloud.google.com/batch/docs/get-started#locations
        job_name: the name of the job that will be created.
            It needs to be unique for each project and region pair.
        template_link: a link to an existing Instance Template. Acceptable formats:
            * "projects/{project_id}/global/instanceTemplates/{template_name}"
            * "{template_name}" - if the template is defined in the same project as used to create the Job.

    Returns:
        A job object representing the job created.
    """
    client = batch_v1.BatchServiceClient()

    # Define what will be done as part of the job.
    task = batch_v1.TaskSpec()
    runnable = batch_v1.Runnable()
    runnable.script = batch_v1.Runnable.Script()
    runnable.script.text = "echo Hello world! This is task ${BATCH_TASK_INDEX}. This job has a total of ${BATCH_TASK_COUNT} tasks."
    # You can also run a script from a file. Just remember, that needs to be a script that's
    # already on the VM that will be running the job. Using runnable.script.text and runnable.script.path is mutually
    # exclusive.
    # runnable.script.path = '/tmp/test.sh'
    task.runnables = [runnable]

    # We can specify what resources are requested by each task.
    resources = batch_v1.ComputeResource()
    resources.cpu_milli = 2000  # in milliseconds per cpu-second. This means the task requires 2 whole CPUs.
    resources.memory_mib = 16
    task.compute_resource = resources

    task.max_retry_count = 2
    task.max_run_duration = "3600s"

    # Tasks are grouped inside a job using TaskGroups.
    # Currently, it's possible to have only one task group.
    group = batch_v1.TaskGroup()
    group.task_count = 4
    group.task_spec = task

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


def create_job_request(job: batch_v1.Job, project_id: str, region: str, job_name: str, template_link: str) -> batch_v1.Job:
    create_request = batch_v1.CreateJobRequest()
    create_request.job = job
    create_request.job_id = job_name
    # The job's parent is the region in which the job will run
    create_request.parent = f"projects/{project_id}/locations/{region}"

    return create_request

def submit_job_request(create_request: batch_v1.CreateJobRequest) -> batch_v1.Job:
    client = batch_v1.BatchServiceClient()
    return client.create_job(create_request)

## #############################################
if __name__ == '__main__':

    job_id = f"rb-job-{time.time()}".replace('.','-')
    
    job = create_script_job_with_template(  "rlgin-batch", 
                                            "us-central1-a", 
                                            job_id, 
                                            "rb-a-s50-template-1")
    for att in dir(job):
        print (f"att: {getattr(job,att)}")

    create_request = create_job_request(  job, "rlgin-batch", 
                                            "us-central1-a", 
                                            job_id, 
                                            "rb-a-s50-template-1")
    for att in dir(create_request):
        print (f"att: {getattr(create_request,att)}")

#    submitted = submit_job_request(create_request)
#    for att in dir(create_request):
#        print (f"att: {getattr(create_request,att)}")
