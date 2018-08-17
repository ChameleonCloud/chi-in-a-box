Vagrant.configure('2') do |config|
  config.vm.box = 'centos/7'

  config.vm.provision 'ansible_local' do |ansible|
    ansible.playbook = "playbooks/#{ENV['PLAYBOOK']}"
    ansible.become = true
    ansible.become_user = 'root'
    ansible.groups = {
      'grafana' => ['default'],
      'node_exporters' => ['default'],
    }
  end
end
