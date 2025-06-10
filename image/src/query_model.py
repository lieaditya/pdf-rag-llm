import os
import time
# from datetime import datetime, timezone
import uuid
import boto3
from pydantic import BaseModel, Field
from typing import List, Optional, Type
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
TABLE_NAME = os.environ.get("TABLE_NAME")
TTL_EXPIRE_MONTHS = 6
TTL_EXPIRE_TIMESTAMP = 60 * 60 * 24 * 30 * TTL_EXPIRE_MONTHS
GSI_INDEX_NAME = "UserIdSortedByCreatedAt"


class QueryModel(BaseModel):
    query_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    user_id: str = "nobody"
    created_at: int = Field(default_factory=lambda: int(time.time()))
    # created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ttl: int = Field(default_factory=lambda: int(time.time() + TTL_EXPIRE_TIMESTAMP))
    query_text: str
    answer_text: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    is_complete: bool = False


    @classmethod
    def get_table(cls: Type["QueryModel"]):
        dynamodb = boto3.resource("dynamodb")
        if not TABLE_NAME:
            raise ValueError("TABLE_NAME must be set")
        return dynamodb.Table(TABLE_NAME)


    def put_item(self):
        item = self.as_ddb_item()
        try:
            response = QueryModel.get_table().put_item(Item=item)
            print(response)
        except ClientError as e:
            # print("ClientError", e.response["Error"]["Message"])
            error = e.response.get("Error", {})
            message = error.get("Message", "Unknown error")
            print("ClientError:", message)
            raise e


    def as_ddb_item(self):
        item = {k: v for k, v in self.model_dump().items() if v is not None}
        return item


    @classmethod
    def get_item(cls: Type["QueryModel"], query_id: str) -> "QueryModel | None":
        try:
            response = cls.get_table().get_item(Key={"query_id": query_id})
        except ClientError as e:
            error = e.response.get("Error", {})
            message = error.get("Message", "Unknown error")
            print("ClientError:", message)
            return None

        if "Item" in response:
            item = response["Item"]
            return cls(**item) # type: ignore
        else:
            return None

    @classmethod
    def list_items(cls: Type["QueryModel"], user_id: str, count: int) -> list["QueryModel"]:
        try:
            response = cls.get_table().query(
                IndexName=GSI_INDEX_NAME,
                KeyConditionExpression="user_id = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
                Limit=count,
                ScanIndexForward=False,
            )
        except ClientError as e:
            error = e.response.get("Error", {})
            message = error.get("Message", "Unknown error")
            print("ClientError:", message)
            return []
        
        items = response.get("Items", [])
        return [cls(**item) for item in items] # type: ignore

    @classmethod
    def list_documents(cls: Type["QueryModel"], user_id: str):
        pass

