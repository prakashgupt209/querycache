import boto3
import os
import pandas as pd
import time

def get_data_from_s3():
    # Initialize Glue client
    glue_client = boto3.client('glue', region_name = os.environ.get('region_name'),
                               aws_access_key_id=os.environ.get('aws_access_key_id'),
                               aws_secret_access_key=os.environ.get('aws_secret_access_key'))


    # Specify the database name
    database_name = 'curated-datalake-playground'

    # List tables in the database
    response = glue_client.get_tables(DatabaseName=database_name)


    table_name = 'gclogs'
    print(f"Fetching data from table: {table_name}")

    # Get table details
    table_details = glue_client.get_table(DatabaseName=database_name, Name=table_name)

    # Access table properties
    table_location = table_details['Table']['StorageDescriptor']['Location']

    athena_client = boto3.client('athena', region_name = os.environ.get('region_name'),
                                 aws_access_key_id=os.environ.get('aws_access_key_id'),
                                 aws_secret_access_key=os.environ.get('aws_secret_access_key'))

    # Sample query to fetch data from the table
    query = f""" SELECT * FROM "{database_name}"."{table_name}" 
    where source_cdc_event='imerit-datalake-raw-playground-ab12/source=ango/test.gclogs/partition=0/test.gclogs+0+0000000446.json'
"""
    print(query)

    # Run the query
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database_name},
        ResultConfiguration={'OutputLocation': 's3://your-bucket/query-results/'}
    )

    # Wait for the query to complete
    query_execution_id = response['QueryExecutionId']

    # Poll until the query execution completes
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']

        if status in ['FAILED', 'CANCELLED', 'SUCCEEDED']:
            break

        # If the query is still running, wait for a short time before checking again
        time.sleep(5)

    # Check if the query execution was successful
    if status == 'SUCCEEDED':
        # Get the results
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        # print('Results - {}'.format(results))
        # Process the results into a DataFrame
        column_names = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        data = [row['Data'] for row in results['ResultSet']['Rows'][1:]]  # Exclude the first row as it contains column names

        # Extract only values from the data
        values = [[cell['VarCharValue'] for cell in row] for row in data]

        # print('Values - {}'.format(values))
        # Convert to DataFrame
        df = pd.DataFrame(values, columns=column_names)

        return df

    else:
        print(f"Query execution failed with status: {status}")
        return -1
