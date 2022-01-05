# passwords.yml

`passwords.yml` contains encrypted passwords for your site, with the encryption password stored in the file `vault_password`. Make sure not to add `vault_password` to source control!

Entries of the form `password_name:` will have passwords auto-generated on save.

View passwords with `cc-ansible view_passwords`, and edit them with `cc-ansible edit_passwords`

