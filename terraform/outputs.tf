output "api_gateway_url" {
  value = "${aws_apigatewayv2_api.proxy_api.api_endpoint}/prod"
}

resource "local_file" "api_config" {
  content = jsonencode({
    api_gateway_url = "${aws_apigatewayv2_api.proxy_api.api_endpoint}/prod",
  })
  filename = "${path.module}/../src/config/api_config.json"
}