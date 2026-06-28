variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Prefix for project resources"
  type        = string
  default     = "enterprise-cdc-pii"
}
