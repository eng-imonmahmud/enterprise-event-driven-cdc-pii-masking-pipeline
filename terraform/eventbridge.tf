resource "aws_scheduler_schedule" "invoke_data_generator" {
  name        = "${var.project_name}-trigger"
  description = "Triggers the data generator Lambda function every minute"
  group_name  = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 minutes)"

  target {
    arn      = aws_lambda_function.data_generator.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}
