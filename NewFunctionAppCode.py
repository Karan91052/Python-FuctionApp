import logging
import os
from datetime import datetime, timedelta
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    try:
        # Use environment variables for local development
        if "AzureWebJobsStorage" not in os.environ:
            os.environ["AZURE_CLIENT_ID"] = "9b0b6cc9-55bf-4284-b017-95daaec18ec3"
            os.environ["AZURE_CLIENT_SECRET"] = "4744bd50-fd26-4154-b471-62f71ab09094"
            os.environ["AZURE_TENANT_ID"] = "5202406f-f701-4c8d-bf2c-cd63bca126b9"
            os.environ["AZURE_SUBSCRIPTION_ID"] = "7951adbe-b3bf-4ea1-9cd2-377f532cfe26"

        credential = DefaultAzureCredential()
        client = LogsQueryClient(credential)
        query = "AzureMetrics"
        
        # Specify your start and end times properly
        start_time = datetime(2023, 10, 10)
        end_time = start_time + timedelta(days=5)

        response = client.query_workspace(
            workspace_id="4eee6649-0457-48ba-961f-6aa5a891a981",
            query=query,
            timespan=(start_time, end_time)  # Use the correct end_time
        )

        if response.status == LogsQueryStatus.PARTIAL:
            error = response.partial_error
            data = response.partial_data
            print(error.message)
        elif response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
            for table in data:
                df = pd.DataFrame(data=table.rows, columns=table.columns)
                df.to_csv("Policies.csv")

                # Upload the CSV to Blob Storage
                blob_service_client = BlobServiceClient.from_connection_string(
                    "DefaultEndpointsProtocol=https;AccountName=karanfunctionapp;AccountKey=zHmRqGuGqu9jqERnp4mtVWnvvQ1bR1zAm3otvhM5gnpTTQ73yN0d+1f6Xk5VIYF4AiDKJgtIegcv+ASt08xciw==;EndpointSuffix=core.windows.net"
                )
                blob_client = blob_service_client.get_blob_client(
                    container="blobcontainer", blob="Policies.csv"
                )

                with open("Policies.csv", "rb") as data:
                    blob_client.upload_blob(data, blob_type="BlockBlob")

    except HttpResponseError as err:
        print("Something fatal happened")
        print(err)

if __name__ == "__main__":
    main(func.TimerRequest(""))
