provider "aws" {
  region = "ap-south-1"
}

module "vpc" {
  source             = "../../modules/vpc"
  cidr_block         = var.cidr_block
  public_subnet_cidr = var.public_subnet_cidr
}

module "iam" {
  source    = "../../modules/iam"
  role_name = var.role_name
}

resource "aws_security_group" "app_sg" {
  name        = "app-sg-prd"
  description = "Allow SSH and app ports"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Frontend"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Backend"
    from_port   = 5000
    to_port     = 5000
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

module "ec2" {
  source               = "../../modules/ec2"
  ami                  = var.ami
  instance_type        = var.instance_type
  subnet_id            = module.vpc.public_subnet_id
  iam_instance_profile = module.iam.instance_profile_name
  security_group_id    = aws_security_group.app_sg.id
}