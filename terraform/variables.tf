variable "project_id"     {}
variable "region"         {}   # or your region
variable "cloudrun_name"  {}

variable "cpu" {
  description = "The CPU limit for the container"
  type        = string
  default     = "1" # Optional: Set a default value
}