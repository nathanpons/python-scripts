terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "lambda_proxy_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# -----------------------------------------------------------------------------------------------------------
# Lambda Functions
# -----------------------------------------------------------------------------------------------------------

# Lambda Function - Weather
resource "aws_lambda_function" "weather" {
  filename      = "${path.module}/../lambda/weather/deployment_package.zip"
  function_name = "weather-proxy"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.10"
  source_code_hash = filebase64sha256("${path.module}/../lambda/weather/deployment_package.zip")

  environment {
    variables = {
      WEATHER_API_KEY = var.weather_api_key
    }
  }
}

# Lambda Function - Recipe
resource "aws_lambda_function" "recipe" {
  filename      = "${path.module}/../lambda/recipe/deployment_package.zip"
  function_name = "recipe-proxy"
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.10"
  source_code_hash = filebase64sha256("${path.module}/../lambda/recipe/deployment_package.zip")
  

  environment {
    variables = {
      SPOONACULAR_API_KEY = var.spoonacular_api_key
    }
  }
}

# -----------------------------------------------------------------------------------------------------------

# API Gateway
resource "aws_apigatewayv2_api" "proxy_api" {
  name          = "python-scripts-proxy"
  protocol_type = "HTTP"
}

# Integrations
resource "aws_apigatewayv2_integration" "weather_integration" {
  api_id             = aws_apigatewayv2_api.proxy_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.weather.invoke_arn
}

resource "aws_apigatewayv2_integration" "recipe_integration" {
  api_id             = aws_apigatewayv2_api.proxy_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.recipe.invoke_arn
}

# -----------------------------------------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------------------------------------

## Weather
resource "aws_apigatewayv2_route" "weather_route" {
  api_id    = aws_apigatewayv2_api.proxy_api.id
  route_key = "GET /weather"
  target    = "integrations/${aws_apigatewayv2_integration.weather_integration.id}"
}

## Recipe
resource "aws_apigatewayv2_route" "recipe_route" {
  api_id    = aws_apigatewayv2_api.proxy_api.id
  route_key = "GET /recipe"
  target    = "integrations/${aws_apigatewayv2_integration.recipe_integration.id}"
}

# -----------------------------------------------------------------------------------------------------------

# Stage
resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.proxy_api.id
  name        = "prod"
  auto_deploy = true
}

# Permissions
resource "aws_lambda_permission" "weather_apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvokeWeather"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.proxy_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "recipe_apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvokeRecipe"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.recipe.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.proxy_api.execution_arn}/*/*"
}