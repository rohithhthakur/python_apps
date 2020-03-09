provider "aws" {
  region = "${var.region}"
}

resource "aws_instance" "instance" {
  ami = "${data.aws_ami.latest-ami.id}"
  instance_type = "${var.instance_type}"
  iam_instance_profile = "${var.iam_instance_profile}"
  subnet_id = "${var.subnet_id}"
  count = "${var.instace_count}"
  security_groups = ["${var.security_group}"]
  root_block_device  {
    volume_size = "${var.volume_size}"
    volume_type           = "${var.volume_type}"
    delete_on_termination = "${var.delete_on_termination}"
  }
  tags = {
    Name = "Server ${count.index}"
  }
}

data "aws_ami" "latest-ami" {
  most_recent = true
  owners = ["self"]
  name_regex = "COF-${var.os_identifier}-x64-HVM-Enc-[0-9]{6}(-[0-9]+)?$"

  filter {
      name   = "state"
      values = ["available"]
  }

  filter {
      name   = "tag:release"
      values = ["ga"]
  }
}
