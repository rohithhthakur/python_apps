output "instance_id" {
  value = "${aws_instance.instance.*.id}"
}

output "instance_windows_id" {
  value = "${aws_instance.instance_windows.*.id}"
}

