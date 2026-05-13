# Output — Questão 06

```hcl
# variables.tf
variable "owner" {
  description = "Dono do recurso (time ou pessoa responsável pela custódia operacional)."
  type        = string
}

variable "cost_center" {
  description = "Centro de custo para alocação financeira (ex.: CC-1234)."
  type        = string
}

variable "environment" {
  description = "Nome do ambiente (dev, staging, production)."
  type        = string
}

variable "bucket_suffix" {
  description = "Sufixo lógico do bucket principal (sem prefixo hvt- e sem environment)."
  type        = string
}

variable "access_logs_prefix" {
  description = "Prefixo de objetos de access log gravados no bucket de logs."
  type        = string
  default     = "s3-access-logs"
}
```

```hcl
# main.tf
locals {
  common_tags = {
    Owner       = var.owner
    CostCenter  = var.cost_center
    Environment = var.environment
  }

  bucket_suffix_clean = lower(replace(var.bucket_suffix, "_", "-"))

  primary_bucket_name = "hvt-${local.bucket_suffix_clean}-${var.environment}"
  logs_bucket_name    = "hvt-${local.bucket_suffix_clean}-logs-${var.environment}"
}

resource "aws_s3_bucket" "logs" {
  bucket = local.logs_bucket_name

  tags = merge(local.common_tags, {
    Name    = local.logs_bucket_name
    Purpose = "s3-server-access-logs"
  })
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "this" {
  bucket = local.primary_bucket_name

  tags = merge(local.common_tags, {
    Name = local.primary_bucket_name
  })
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "this" {
  bucket = aws_s3_bucket.this.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "${var.access_logs_prefix}/"
}

data "aws_iam_policy_document" "logs_policy" {
  statement {
    sid    = "AllowS3LogDeliveryWrite"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["logging.s3.amazonaws.com"]
    }

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.logs.arn}/${var.access_logs_prefix}/*"
    ]

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.this.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = data.aws_iam_policy_document.logs_policy.json
}
```

```hcl
# outputs.tf
output "primary_bucket_id" {
  description = "ID (nome) do bucket principal."
  value       = aws_s3_bucket.this.id
}

output "primary_bucket_arn" {
  description = "ARN do bucket principal."
  value       = aws_s3_bucket.this.arn
}

output "logs_bucket_id" {
  description = "ID (nome) do bucket de access logs."
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "ARN do bucket de access logs."
  value       = aws_s3_bucket.logs.arn
}
```

```hcl
# examples/basic/main.tf
module "hvt_bucket" {
  source = "../../"

  owner         = "platform-team"
  cost_center   = "CC-HVT-PLATFORM"
  environment   = "dev"
  bucket_suffix = "invoices"

  access_logs_prefix = "s3-access-logs/invoices"
}

output "bucket" {
  value = module.hvt_bucket.primary_bucket_id
}
```
