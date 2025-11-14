variable "aws_region" {
  default = "us-east-1"
}

variable "weather_api_key" {
  type = string
  sensitive = true
}

variable "spoonacular_api_key" {
  type = string
  sensitive = true
}