## CircleCI config

### AWS cli config
- not using aws cli this time

### SSH config
- project settings \> Additional SSH Keys
- Add SSH Key: Copy and paste the complete secret key to the <code>Private Key</code> section
- Hostname: Keep blank to use the SSH keys for every hosts

### CircleCI Context
- Terraform prod
    - Environment Variables
        - DB_PASSWORD, DB_USERNAME, DB_NAME
        - AWS_ACCESS_KEY_ID, AWS_DEFAULT_REGION, AWS_SECRET_ACCESS_KEY
- Terraform dev
    - Environment Variables
        - DB_PASSWORD, DB_USERNAME, DB_NAME
        - AWS_ACCESS_KEY_ID, AWS_DEFAULT_REGION, AWS_SECRET_ACCESS_KEY


### Ansible
- Project Environment Variables
    - ANSIBLE_SSH_KEY