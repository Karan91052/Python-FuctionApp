import datetime
import logging
from time import sleep
import pandas as pd
from datetime import date,timedelta
from datetime import datetime, timedelta
# from datetime import datetime, timezone
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobServiceClient, BlobClient
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential)
    query = "AzureMetrics"
    start_time = datetime(2023, 10, 14)
    duration = timedelta(days=5)
    end_time = start_time + duration
    try:
        response = client.query_workspace(
            workspace_id="4eee6649-0457-48ba-961f-6aa5a891a981",
            query=query,
            timespan=(start_time, duration)
            )
        if response.status == LogsQueryStatus.PARTIAL:
            error = response.partial_error
            data = response.partial_data
            print(error.message)
        elif response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
            for table in data:
                df = pd.DataFrame(data=table.rows, columns=table.columns)
                print(df)
                df.to_csv("Policies.csv")
                blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=karanfunctionapp;AccountKey=zHmRqGuGqu9jqERnp4mtVWnvvQ1bR1zAm3otvhM5gnpTTQ73yN0d+1f6Xk5VIYF4AiDKJgtIegcv+ASt08xciw==;EndpointSuffix=core.windows.net")
                blob_client = blob_service_client.get_blob_client(container="blobcontainer", blob="Policies.csv")
            with open("Policies.csv", "rb") as data:
                 blob_client.upload_blob(data, blob_type="AppendBlob")
    except HttpResponseError as err:
            print("something fatal happened")
            print (err)
main(func.TimerRequest)
