from aws_cdk import core, aws_s3 as s3
from .monitoring import CtfMonitoring
from .function import RawDataDownloadFunction
from .bucket import CtfBucket
from .repository import CtfRepository
from . import names


class CtStack(core.Stack):
    def __init__(
        self, scope: core.Construct, id: str, notification_email, **kwargs
    ) -> None:

        super().__init__(scope, id, **kwargs)

        # Email notification for errors
        monitoring = CtfMonitoring(
            self,
            "CtfMonitoring",
            notification_email=notification_email,
        )

        # S3 bucket to store raw data at beginning of ETL pipeline
        CtfBucket(self, "RawDataFilesBucket", name=names.RAW_DATA_FILES_BUCKET)

        # Docker image for data download lambda
        repository = CtfRepository(
            self,
            "RawDataDownloadImage",
            names.RAW_DATA_DOWNLOAD_IMAGE,
        )

        # Function to download files and save in S3
        RawDataDownloadFunction(repository, monitoring)
