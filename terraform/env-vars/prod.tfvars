name = "tf-calculator-prod"

region = "ap-northeast-1"

# subnet list
public_subnet_cidr_list = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidr_list = ["10.0.11.0/24", "10.0.12.0/24"]

# domain_name
# using christeena0717.me
domain_name = "tl-calculator.christeena0717.me"

# RDS variables
db_engine = "mysql"
db_engine_version = "8.0"
db_instance_class = "db.t2.micro"
db_allocated_storage = 20
db_name = "tl_calculator"
db_username = "admin"

# db_password will be imported from circleCI environment variable in pipeline