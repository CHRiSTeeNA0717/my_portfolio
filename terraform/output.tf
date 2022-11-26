output "ALB_dns" {
  description = "Public DNS of ALB"
  value       = aws_lb.my_load_balancer.dns_name
}

output "EC2_dns" {
  description = "EC2 Public DNS"
  value       = aws_instance.my_web_instance.public_dns
}

output "EC2_ip" {
  description = "EC2 ip address"
  value       = aws_instance.my_web_instance.public_ip
}

output "db_host" {
  description = "Endpoint of RDS which will be used in app as db host"
  value       = split(":", aws_db_instance.my_db_instance.endpoint)[0]
}

output "db_port" {
  description = "Port of DB"
  value       = aws_db_instance.my_db_instance.port
}

output "db_name" {
  description = "db name of RDS"
  value       = aws_db_instance.my_db_instance.db_name
}

output "db_username" {
  description = "db username of RDS"
  value       = aws_db_instance.my_db_instance.username
}

output "db_password" {
  description = "db password of RDS"
  value       = aws_db_instance.my_db_instance.password
  sensitive   = true
}
