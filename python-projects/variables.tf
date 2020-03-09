variable "os_identifier" {
  description = "Imgae OS identifier for instance"
}

variable "instance_type" {
  description = "Flavor id for instance"
}

variable "subnet_id" {
  description = "Subnet id for instance"
}

variable "instace_count" {
  description = "Number of instances"
}

variable "security_group" {
  description = "Number of instances"
}


variable "iam_instance_profile" {
  description = "IAM Instance profile name"
}


variable "volume_size" {
  description = "Root volume size"
}

variable "volume_type" {
  description = "Root volume type"
}


variable "delete_on_termination" {
  description = "Delete root volume on termination"
}

variable "region" {
  description = "AWS region"
}
