package ec2evaluation

ssh_port_open {
    instance := input.instance
    some sg
    sg = instance.SecurityGroups[_]
    some rule
    rule = sg.IpPermissions[_]
    rule.FromPort == 22
    rule.ToPort == 22
    rule.IpProtocol == "tcp"
    some ip_range
    ip_range = rule.IpRanges[_]
    ip_range.CidrIp == "0.0.0.0/0"
}


ec2evaluation = ssh_port_open
