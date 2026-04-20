provider "aws" {
  region = "ap-south-1"
}

module "vpc" {
  source      = "../../modules/vpc"
  vpc_name    = var.vpc_name
  subnet_name = var.subnet_name
}

resource "aws_security_group" "sg" {
  name   = var.sg_name
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 80
    to_port   = 3000
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

module "iam" {
  source    = "../../modules/iam"
  role_name = var.iam_role_name
}

module "ec2" {
  source               = "../../modules/ec2"
  ec2_name             = var.ec2_name
  instance_type        = var.instance_type
  subnet_id            = module.vpc.subnet_id
  sg_id                = aws_security_group.sg.id
  key_name             = var.key_name
  iam_instance_profile = module.iam.instance_profile
}

module "s3" {
  source      = "../../modules/s3"
  bucket_name = var.s3_bucket
}

module "ecr" {
  source    = "../../modules/ecr"
  repo_name = var.ecr_repo
}

module "secret" {
  source      = "../../modules/secret-manager"
  secret_name = var.secret_name
}
