provider "aws" {
  region = "${var.region}"
}

resource "aws_instance" "instance" {
  count = var.windows_instance ? 0 : "${var.instace_count}"
  ami = "${data.aws_ami.latest-ami.id}"
  instance_type = "${var.instance_type}"
  associate_public_ip_address = "${var.associate_public_ip_address}"
  iam_instance_profile = "${var.iam_instance_profile}"
  subnet_id = "${var.subnet_id}"
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


resource "aws_instance" "instance_windows" {
  count = var.windows_instance ? "${var.instace_count}" : 0
  ami = "${data.aws_ami.latest-ami.id}"
  instance_type = "${var.instance_type}"
  associate_public_ip_address = "${var.associate_public_ip_address}"
  iam_instance_profile = "${var.iam_instance_profile}"
  subnet_id = "${var.subnet_id}"
  security_groups = ["${var.security_group}"]
  root_block_device  {
    volume_size = "${var.volume_size}"
    volume_type           = "${var.volume_type}"
    delete_on_termination = "${var.delete_on_termination}"
  }
  connection {
    type     = "winrm"
    user     = "Administrator"
    password = "${var.administrator_password}"
    timeout = "10m"
  }
  tags = {
    Name = "Server ${count.index}"
  }
  user_data = <<EOF
<script>
  winrm quickconfig -q & winrm set winrm/config @{MaxTimeoutms="1800000"} & winrm set winrm/config/service @{AllowUnencrypted="true"} & winrm set winrm/config/service/auth @{Basic="true"}
</script>
<powershell>
  netsh advfirewall firewall add rule name="WinRM in" protocol=TCP dir=in profile=any localport=5985 remoteip=any localip=any action=allow
  # Set Administrator password
  $admin = [adsi]("WinNT://./administrator, user")
  $admin.psbase.invoke("SetPassword", "${var.administrator_password}")
</powershell>
EOF
}

data "aws_ami" "latest-ami" {
  most_recent = true
  owners = ["self"]
  #name_regex = "COF-${var.os_identifier}-x64-HVM-Enc-[0-9]{6}(-[0-9]+)?$"
  name_regex = "${var.os_identifier}[0-9]{6}"

  filter {
      name   = "state"
      values = ["available"]
  }

  filter {
      name   = "tag:release"
      values = ["ga"]
  }
}
