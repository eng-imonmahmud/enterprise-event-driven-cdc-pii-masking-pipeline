output "dynamodb_table_name" {
  value       = aws_dynamodb_table.customer_records.name
  description = "The name of the DynamoDB table"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.data_lake.bucket
  description = "The name of the S3 Data Lake bucket"
}

output "data_generator_lambda_name" {
  value       = aws_lambda_function.data_generator.function_name
  description = "Data Generator Lambda function name"
}

output "pii_masking_lambda_name" {
  value       = aws_lambda_function.pii_masking.function_name
  description = "PII Masking Lambda function name"
}

output "eventbridge_schedule_name" {
  value       = aws_scheduler_schedule.invoke_data_generator.name
  description = "EventBridge Scheduler name"
}
