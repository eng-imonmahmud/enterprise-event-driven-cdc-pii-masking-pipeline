resource "aws_dynamodb_table" "customer_records" {
  name         = "${var.project_name}-customer-records"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  tags = {
    Name        = "${var.project_name}-customer-records"
    Environment = "Production"
  }
}
