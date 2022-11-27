# TERRAFORM 
# This file has all the resource to config an infrastructure for app
# using s3 as backend
# use CTRL+F and keyword below to search for particular resource
# resources are(from first to last):
# provider
# store tfstate in s3
# VPC
# IGW
# IGW attachment
# public subnet
# private subnet
# db subnet group for rds
# route table
# route table routing
# route table assoc public
# route table private
# route table assoc private
# EC2 instance
# ALB instance
# RDS
# public security group
# private security group
# RDS security group

# Reference when creating RDS resource: https://medium.com/strategio/using-terraform-to-create-aws-vpc-ec2-and-rds-instances-c7f3aa416133
# Reference when creating ALB resource: https://medium.com/cognitoiq/terraform-and-aws-application-load-balancers-62a6f8592bcf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.31"
    }
  }
  required_version = ">= 1.0.0"
}

# provider
provider "aws" {
  region = var.region
}

# store tfstate in s3
terraform {
  backend "s3" {}
}

# VPC
resource "aws_vpc" "my_vpc" {
  cidr_block = var.vpc_cidr

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.name}"
  }
}

# IGW
resource "aws_internet_gateway" "my_IGW" {
  tags = {
    Name = "${var.name}"
  }
}

# IGW attachment
resource "aws_internet_gateway_attachment" "my_IGW_attach" {
  vpc_id              = aws_vpc.my_vpc.id
  internet_gateway_id = aws_internet_gateway.my_IGW.id
}

# availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# public subnet
# create subnets in different AZs
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.my_vpc.id
  count                   = length(var.public_subnet_cidr_list)
  cidr_block              = var.public_subnet_cidr_list[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.name}-public-subnet-${count.index}"
  }
}

# private subnet
# create subnets in different AZs
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.my_vpc.id
  count             = length(var.private_subnet_cidr_list)
  cidr_block        = var.private_subnet_cidr_list[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.name}-private-subnet-${count.index}"
  }
}

# db subnet group for rds
resource "aws_db_subnet_group" "my_db_subnet_group" {
  name       = "my_db_subnet_group"
  subnet_ids = [aws_subnet.private[0].id, aws_subnet.private[1].id]

  tags = {
    Name = "${var.name}-subnet-group"
  }
}

# route table
resource "aws_route_table" "my_route_table" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "${var.name}-route-table"
  }
}

# route table routing
resource "aws_route" "public_IGW" {
  route_table_id         = aws_route_table.my_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.my_IGW.id
}

# route table assoc public
resource "aws_route_table_association" "public_subnet" {
  count          = length(var.public_subnet_cidr_list)
  route_table_id = aws_route_table.my_route_table.id
  subnet_id      = element(aws_subnet.public.*.id, count.index)
}

# route table private
resource "aws_route_table" "my_route_table_private" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "${var.name}-private"
  }
}

# route table assoc private
resource "aws_route_table_association" "private_subnet" {
  count          = length(var.private_subnet_cidr_list)
  route_table_id = aws_route_table.my_route_table_private.id
  subnet_id      = element(aws_subnet.private.*.id, count.index)
}


# EC2 instance
resource "aws_instance" "my_web_instance" {
  ami                         = "ami-0de5311b2a443fb89" # region: ap-northeast-1, amazon linux 2
  associate_public_ip_address = true
  instance_type               = "t2.micro"

  key_name        = "RaiseTechKP"
  subnet_id       = aws_subnet.public[0].id
  security_groups = [aws_security_group.public.id]

  ebs_block_device {
    device_name = "/dev/xvda"
    volume_size = 27
    volume_type = "gp2"
  }

  user_data = <<EOF
  #! /bin/bash
  sudo yum -y update
  amazon-linux-extras install -y nginx1
  EOF

  tags = {
    Name = "${var.name}-ec2"
  }
}

#########################################################
# ACM cert & DNS
# reference: 
#   https://dev.classmethod.jp/articles/acm-cert-by-terraform/
#   https://dev.classmethod.jp/articles/terraform-aws-certificate-validation/

data "aws_route53_zone" "domain" {
  name         = "christeena0717.me"
  private_zone = false
}

resource "aws_acm_certificate" "terraform_cert" {
  domain_name       = "${var.domain_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {

  for_each = {
    for dvo in aws_acm_certificate.terraform_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.domain.zone_id
}

resource "aws_route53_record" "alias_record" {
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = "${var.domain_name}"
  type    = "A"

  alias {
    name                    = aws_lb.my_load_balancer.dns_name
    zone_id                 = aws_lb.my_load_balancer.zone_id
    evaluate_target_health = true
  }
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.terraform_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}
#########################################################


#########################################################
# ALB instance
resource "aws_lb" "my_load_balancer" {
  name               = "${var.name}-web-alb"
  load_balancer_type = "application"

  security_groups = [aws_security_group.lb.id]
  subnets         = [for subnet in aws_subnet.public : subnet.id]

  tags = {
    Name = "${var.name}-alb"
  }
}

# ALB listener
# https setting reference: https://dev.classmethod.jp/articles/dnsrecord-acm-alb-with-terraform/
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.my_load_balancer.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-Ext-2018-06"
  certificate_arn   = aws_acm_certificate.terraform_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.my_alb_target_group.arn
  }

  depends_on = [
    aws_acm_certificate_validation.cert
  ]
}

# ALB target group
resource "aws_lb_target_group" "my_alb_target_group" {
  name        = "${var.name}-tg"
  target_type = "instance"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.my_vpc.id

  tags = {
    Name = "${var.name}-tg"
  }
}

# ALB target group attachment
resource "aws_lb_target_group_attachment" "my_tg_attachment" {
  target_group_arn = aws_lb_target_group.my_alb_target_group.arn
  target_id        = aws_instance.my_web_instance.id
  port             = 80
}
#########################################################

# RDS
resource "aws_db_instance" "my_db_instance" {
  allocated_storage = var.db_allocated_storage
  engine            = var.db_engine
  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  db_name           = var.db_name # the db name when creating rds, if not included, user has to create manually
  username          = var.db_username
  password          = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.my_db_subnet_group.id

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "${var.name}-db-for-projectcicd"
  }
}

####################################################################################################################
####################################################################################################################
# SECURITY GROUP BELOW
# load balancer security group
resource "aws_security_group" "lb" {
  name        = "${var.name}-lb"
  description = "for ALB traffic from/to everywhere"
  vpc_id      = aws_vpc.my_vpc.id

  tags = {
    Name = "${var.name}-alb"
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# public security group
resource "aws_security_group" "public" {
  name        = "${var.name}-public"
  description = "Public internet access (ssh and http from alb)"
  vpc_id      = aws_vpc.my_vpc.id

  tags = {
    Name = "${var.name}-public"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.public_subnet_cidr_list
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# private security group
resource "aws_security_group" "private" {
  name        = "${var.name}-private"
  description = "Private internet access"
  vpc_id      = aws_vpc.my_vpc.id

  tags = {
    Name = "${var.name}-private"
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.my_vpc.cidr_block]
  }
}

# RDS security group
resource "aws_security_group" "rds" {
  name        = "${var.name}-rds"
  description = "rds security group accept only ec2 traffic"
  vpc_id      = aws_vpc.my_vpc.id

  ingress {
    description     = "Allow traffic for MySql from ec2 only"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.public.id]
  }

  tags = {
    Name = "${var.name}-ec2-to-rds-mysql"
  }
}
