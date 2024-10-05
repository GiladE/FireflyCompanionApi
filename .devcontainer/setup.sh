#!/bin/bash

sudo mkdir /etc/pynamodb
sudo bash -c 'echo "host=\"http://dynamodb:8000\"" >> /etc/pynamodb/global_default_settings.py'
echo "alias activate=\"source venv/bin/activate\"" >> /home/vscode/.zshrc
echo "alias overmind=\"/workspaces/FireflyCompanionApi/.devcontainer/overmind\"" >> /home/vscode/.zshrc
echo "export PATH=\"$(yarn global bin):$PATH\"" >> /home/vscode/.zshrc
sudo bash -c 'cat << 'EOF' > /usr/local/bin/code
#!/bin/sh
code="\$(find /home/vscode/.vscode-*/bin/*/bin/remote-cli/code | head -n 1)"
exec "\$code" "\$@"
EOF'
sudo chmod +x /usr/local/bin/code
git config --global core.editor "code --wait"
sudo rm /home/vscode/.gitconfig

function echo_big_notice() { local message="$1"; local width=${#message}; local line=""; for (( i=1; i<=$width+4; i++ )); do line+="*"; done; echo -e "\033[1;33m\t\t\t\t\t '\n\t\t\t\t*\t\t  .\n\t\t\t\t\t   *\t   '\n\t\t\t\t  *\t\t\t\t*\n$line\033[0m\n\033[1;33m*\033[0m \033[1m$message\033[0m \033[1;33m*\033[0m\n\033[1;33m$line\n\t\t   *\t*\n\t\t\t\t   *\n\t\t.\t\t\t\t*\n\t\t\t\t\t\t\t   *\n\t\t\t\t\t   *\n\t\t\t\t'\t\t\t *\033[0m"; }

echo_big_notice "Setup for your devcontainer has been completed. Thank you for flying with us today. Don't forget to tip."