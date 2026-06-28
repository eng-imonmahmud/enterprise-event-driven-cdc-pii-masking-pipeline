data "archive_file" "data_generator_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/data_generator"
  output_path = "${path.module}/data_generator.zip"
}

resource "aws_lambda_function" "data_generator" {
  filename         = data.archive_file.data_generator_zip.output_path
  function_name    = "${var.project_name}-data-generator"
  role             = aws_iam_role.data_generator_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.data_generator_zip.output_base64sha256
  timeout          = 15

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.customer_records.name
    }
  }
}

data "archive_file" "pii_masking_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/pii_masking"
  output_path = "${path.module}/pii_masking.zip"
}

resource "aws_lambda_function" "pii_masking" {
  filename         = data.archive_file.pii_masking_zip.output_path
  function_name    = "${var.project_name}-pii-masking"
  role             = aws_iam_role.pii_masking_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.pii_masking_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.data_lake.bucket
    }
  }
}

# DynamoDB Event Source Mapping for Lambda
resource "aws_lambda_event_source_mapping" "dynamodb_trigger" {
  event_source_arn       = aws_dynamodb_table.customer_records.stream_arn
  function_name          = aws_lambda_function.pii_masking.arn
  starting_position      = "LATEST"
  batch_size             = 100
  maximum_retry_attempts = 3
}

# CloudWatch Log Groups for Lambdas
resource "aws_cloudwatch_log_group" "data_generator_logs" {
  name              = "/aws/lambda/${aws_lambda_function.data_generator.function_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "pii_masking_logs" {
  name              = "/aws/lambda/${aws_lambda_function.pii_masking.function_name}"
  retention_in_days = 7
}
