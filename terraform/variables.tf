# declare variables used for env

# Environment name for Name tags of the project
#########################################################
variable "name" {
  type        = string
  description = "The prefix name for resources"
}

variable "region" {
  type    = string
  default = "ap-northeast-1"
}
#########################################################


# Subnet variable as a list
# Public subnet
variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr_list" {
  type    = list(string)
  default = []
}

# Private subnet
variable "private_subnet_cidr_list" {
  type    = list(string)
  default = []
}

#########################################################
# domain name
variable "domain_name" {
  type = string
}
#########################################################

# RDS variables
#########################################################
variable "db_allocated_storage" {
  type    = number
  default = 20
}
# the name of db when creating rds
variable "db_name" {
  type = string
}
variable "db_engine" {
  type = string
}
variable "db_engine_version" {
  type = string
}
variable "db_instance_class" {
  type = string
}
variable "db_username" {
  type = string
}
variable "db_password" {
  type = string
}
#########################################################