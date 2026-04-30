resource "local_file" "dev_config" {
  filename = "clickops-dev.config"

  content = <<EOT
ENVIRONMENT = dev
EC2_PUBLIC_IP = ${module.ec2.public_ip}
S3_BUCKET = ${var.s3_bucket}
ECR_REPO = ${var.ecr_repo}
EOT
}