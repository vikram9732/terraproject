terraform {
  backend "s3" {
    bucket         = "clickops-terraform-state-vikram-2026"
    key            = "dev/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "clickops-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-south-1"
}

module "vpc" {
  source      = "../../modules/vpc"
  vpc_name    = var.vpc_name
  cidr_block  = var.cidr_block
  subnet_name = var.subnet_name
  public_subnet_cidr = var.public_subnet_cidr
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
  source = "../../modules/ec2"

  ami                = "ami-0f58b397bc5c1f2e8"  # Amazon Linux (ap-south-1)
  instance_type      = var.instance_type
  subnet_id          = module.vpc.subnet_id
  security_group_id  = aws_security_group.sg.id
  key_name           = var.key_name
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