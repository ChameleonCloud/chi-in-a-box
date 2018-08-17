Vagrant.configure('2') do |config|
  config.vm.box = 'centos/7'

  # Copy the Ansible playbook over to the guest machine, run rsync-auto to automatically
  # pull in the latest changes while a VM is running.
  # config.vm.synced_folder './', "#{@ansible_home}", type: 'rsync'

  # The working ansible directory created by ansible_local is owned by root
  # config.vm.provision 'shell', inline: "chown vagrant:vagrant #{@ansible_home}"

  config.vm.provision 'ansible_local' do |ansible|
    ansible.playbook = "playbooks/#{ENV['PLAYBOOK']}"
  end
end
