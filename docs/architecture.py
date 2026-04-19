from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR, Fargate
from diagrams.aws.database import Dynamodb
from diagrams.aws.engagement import SimpleEmailServiceSes
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch, ParameterStore
from diagrams.aws.security import IAMRole
from diagrams.custom import Custom

ASSETS = Path(__file__).parent / "assets"

graph_attr = {
    "fontsize": "20",
    "bgcolor": "transparent",
    "splines": "polyline",
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
    with Cluster("External"):
        ai_api = Custom("AI API", str(ASSETS / "api.png"))
        job_boards = Custom("Job Boards", str(ASSETS / "web.png"))

    with Cluster("AWS"):
        # Security
        exec_role = IAMRole("Task\nExecution\nRole")
        task_role = IAMRole("Task Role")
        scheduler_role = IAMRole("Scheduler Role")

        # Application Infrastructure
        ssm = ParameterStore("SSM\nParameters")
        scheduler = Eventbridge("EventBridge\nScheduler")
        mailer = SimpleEmailServiceSes("SES")
        logs = Cloudwatch("CloudWatch\nLogs")
        register = ECR("ECR")
        cache = Dynamodb("Jobs Cache")

        with Cluster("VPC"):
            with Cluster("Public Subnet"):
                worker = Fargate("Fargate Task")

    # Execution flow
    scheduler >> Edge(label="triggers") >> worker  # EventBridge triggers Fargate task
    (
        register >> Edge(label="pulls image") >> worker
    )  # Fargate pulls image from ECR at startup
    ssm >> worker  # task reads config at startup

    # IAM
    worker >> Edge(style="dashed", label="assumes") >> exec_role
    worker >> Edge(style="dashed", label="assumes") >> task_role
    scheduler >> Edge(style="dashed", label="assumes") >> scheduler_role

    # Outputs
    worker >> Edge(label="read/write") >> cache  # reads/writes job cache
    worker >> Edge(label="sends email") >> mailer  # sends email
    worker >> logs  # writes logs

    # External interactions
    worker >> Edge(label="scores jobs") >> ai_api  # calls AI API for job search
    job_boards >> Edge(label="scrape") >> worker  # scrapes job boards for listings
