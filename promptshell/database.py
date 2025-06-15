import os
from typing import Optional, Dict, Any
import json
from abc import ABC, abstractmethod
import boto3
from google.cloud import firestore
from azure.cosmos import CosmosClient
from pymongo import MongoClient
from .format_utils import format_text, reset_format

class CloudDatabase(ABC):
    """Abstract base class for cloud database implementations"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the cloud database"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to the cloud database"""
        pass
    
    @abstractmethod
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to the cloud database"""
        pass
    
    @abstractmethod
    def load_data(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Load data from the cloud database"""
        pass

class AWSDatabase(CloudDatabase):
    """AWS DynamoDB implementation"""
    
    def __init__(self, region: str, table_name: str):
        self.region = region
        self.table_name = table_name
        self.dynamodb = None
        self.table = None
    
    def connect(self) -> bool:
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            self.table = self.dynamodb.Table(self.table_name)
            return True
        except Exception as e:
            print(format_text('red') + f"Error connecting to AWS DynamoDB: {str(e)}" + reset_format())
            return False
    
    def disconnect(self) -> bool:
        try:
            self.dynamodb = None
            self.table = None
            return True
        except Exception as e:
            print(format_text('red') + f"Error disconnecting from AWS DynamoDB: {str(e)}" + reset_format())
            return False
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        try:
            self.table.put_item(Item=data)
            return True
        except Exception as e:
            print(format_text('red') + f"Error saving data to AWS DynamoDB: {str(e)}" + reset_format())
            return False
    
    def load_data(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key=query)
            return response.get('Item')
        except Exception as e:
            print(format_text('red') + f"Error loading data from AWS DynamoDB: {str(e)}" + reset_format())
            return None

class GoogleDatabase(CloudDatabase):
    """Google Cloud Firestore implementation"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db = None
    
    def connect(self) -> bool:
        try:
            self.db = firestore.Client()
            return True
        except Exception as e:
            print(format_text('red') + f"Error connecting to Google Firestore: {str(e)}" + reset_format())
            return False
    
    def disconnect(self) -> bool:
        try:
            self.db = None
            return True
        except Exception as e:
            print(format_text('red') + f"Error disconnecting from Google Firestore: {str(e)}" + reset_format())
            return False
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        try:
            doc_ref = self.db.collection(self.collection_name).document()
            doc_ref.set(data)
            return True
        except Exception as e:
            print(format_text('red') + f"Error saving data to Google Firestore: {str(e)}" + reset_format())
            return False
    
    def load_data(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            docs = self.db.collection(self.collection_name).where(**query).limit(1).get()
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            print(format_text('red') + f"Error loading data from Google Firestore: {str(e)}" + reset_format())
            return None

class AzureDatabase(CloudDatabase):
    """Azure Cosmos DB implementation"""
    
    def __init__(self, endpoint: str, key: str, database_name: str, container_name: str):
        self.endpoint = endpoint
        self.key = key
        self.database_name = database_name
        self.container_name = container_name
        self.client = None
        self.container = None
    
    def connect(self) -> bool:
        try:
            self.client = CosmosClient(self.endpoint, self.key)
            database = self.client.get_database_client(self.database_name)
            self.container = database.get_container_client(self.container_name)
            return True
        except Exception as e:
            print(format_text('red') + f"Error connecting to Azure Cosmos DB: {str(e)}" + reset_format())
            return False
    
    def disconnect(self) -> bool:
        try:
            self.client = None
            self.container = None
            return True
        except Exception as e:
            print(format_text('red') + f"Error disconnecting from Azure Cosmos DB: {str(e)}" + reset_format())
            return False
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        try:
            self.container.create_item(body=data)
            return True
        except Exception as e:
            print(format_text('red') + f"Error saving data to Azure Cosmos DB: {str(e)}" + reset_format())
            return False
    
    def load_data(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            items = list(self.container.query_items(
                query=f"SELECT * FROM c WHERE {query}",
                enable_cross_partition_query=True
            ))
            return items[0] if items else None
        except Exception as e:
            print(format_text('red') + f"Error loading data from Azure Cosmos DB: {str(e)}" + reset_format())
            return None

class MongoDBDatabase(CloudDatabase):
    """MongoDB Atlas implementation"""
    
    def __init__(self, connection_string: str, database_name: str, collection_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.collection = None
    
    def connect(self) -> bool:
        try:
            self.client = MongoClient(self.connection_string)
            db = self.client[self.database_name]
            self.collection = db[self.collection_name]
            return True
        except Exception as e:
            print(format_text('red') + f"Error connecting to MongoDB: {str(e)}" + reset_format())
            return False
    
    def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.close()
            self.client = None
            self.collection = None
            return True
        except Exception as e:
            print(format_text('red') + f"Error disconnecting from MongoDB: {str(e)}" + reset_format())
            return False
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        try:
            self.collection.insert_one(data)
            return True
        except Exception as e:
            print(format_text('red') + f"Error saving data to MongoDB: {str(e)}" + reset_format())
            return False
    
    def load_data(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            result = self.collection.find_one(query)
            return result
        except Exception as e:
            print(format_text('red') + f"Error loading data from MongoDB: {str(e)}" + reset_format())
            return None

def get_database_provider(provider: str, config: Dict[str, Any]) -> Optional[CloudDatabase]:
    """Factory function to create database provider instances"""
    try:
        if provider.lower() == 'aws':
            return AWSDatabase(
                region=config.get('aws_region', 'us-east-1'),
                table_name=config.get('aws_table_name', 'promptshell_data')
            )
        elif provider.lower() == 'google':
            return GoogleDatabase(
                collection_name=config.get('google_collection_name', 'promptshell_data')
            )
        elif provider.lower() == 'azure':
            return AzureDatabase(
                endpoint=config.get('azure_endpoint'),
                key=config.get('azure_key'),
                database_name=config.get('azure_database_name', 'promptshell'),
                container_name=config.get('azure_container_name', 'data')
            )
        elif provider.lower() == 'mongodb':
            return MongoDBDatabase(
                connection_string=config.get('mongodb_connection_string'),
                database_name=config.get('mongodb_database_name', 'promptshell'),
                collection_name=config.get('mongodb_collection_name', 'data')
            )
        else:
            print(format_text('red') + f"Unsupported database provider: {provider}" + reset_format())
            return None
    except Exception as e:
        print(format_text('red') + f"Error creating database provider: {str(e)}" + reset_format())
        return None 