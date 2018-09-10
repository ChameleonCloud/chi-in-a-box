require 'json'

Vagrant.configure('2') do |config|
  playbooks = ENV['PLAYBOOK'].split(',')
  host_name = "#{playbooks.join("_")}.local"
  # Check if additional variables are defined
  extra_vars = if ENV['VARS'] then JSON.parse(ENV['VARS']) else {} end

  config.vm.box = 'centos/7'

  # Create separate VM for each playbook by default.
  config.vm.define host_name do |host|
    groups = {
      # General groups used by multiple playbooks (potentially)
      'frontends' => [host_name],
    }

    playbooks.each do |playbook_name|
      # By convention, our playbooks target a host group with the same name
      # as the playbook
      groups[playbook_name] = [host_name]
    end

    playbooks.each do |playbook_name|
      host.vm.provision 'ansible_local' do |ansible|
        ansible.playbook = "playbooks/#{playbook_name}.yml"
        ansible.tags = ENV.fetch('TAGS', '').split(',')
        ansible.extra_vars = extra_vars
        # TODO: this isn't super great, as we miss testing bad permission issues.
        # However, most hosts override this at the host level anyways. Not sure
        # what the best thing is - to handle permission escalation in a task, or
        # assume the host is running at the appropriate permission already. We
        # do the latter for testing simplicity.
        ansible.become = true
        ansible.become_user = 'root'
        ansible.groups = groups
      end
    end
  end
end
