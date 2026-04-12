from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR, Fargate
from diagrams.aws.database import Dynamodb
from diagrams.aws.engagement import SimpleEmailServiceSes
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch, ParameterStore
from diagrams.aws.security import IAMRole

graph_attr = {
    "fontsize": "20",
    "bgcolor": "transparent",
    "splines": "ortho",  # right-angle edges — cleaner look
    "nodesep": "0.8",  # horizontal spacing between nodes
    "ranksep": "1.0",  # vertical spacing between ranks
}

with Diagram(
    "Job Hunter Bot",
    show=False,
    graph_attr=graph_attr,
    direction="LR",  # left to right layout
    filename="img/architecture",
    outformat="png",
):
    with Cluster("AWS"):
        # Security
        exec_role = IAMRole("Task\nExecution\nRole")
        task_role = IAMRole("Task Role")
        scheduler_role = IAMRole("scheduler\nRole")

        # Application Infrastructure
        ssm = ParameterStore("SSM\nParameters")
        scheduler = Eventbridge("EventBridge\nScheduler")
        mailer = SimpleEmailServiceSes("SES")
        logs = Cloudwatch("CloudWatch\nLogs")
        register = ECR("ECR")

        with Cluster("VPC"):
            with Cluster("Public Subnet"):
                cache = Dynamodb("Jobs Cache")
                with Cluster("ECS Cluster"):
                    worker = Fargate("Fargate Task")

    # Execution flow
    scheduler >> worker  # EventBridge triggers Fargate task
    register >> worker  # Fargate pulls image from ECR at startup
    ssm >> worker  # task reads config at startup

    # IAM
    exec_role >> Edge(style="dashed", label="assumes") >> worker
    task_role >> Edge(style="dashed", label="assumes") >> worker

    # Outputs
    worker >> cache  # reads/writes job cache
    worker >> mailer  # sends email
    worker >> logs  # writes logs
