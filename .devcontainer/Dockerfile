FROM mcr.microsoft.com/devcontainers/python:3.10
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y expect tmux inotify-tools gnupg software-properties-common
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
RUN chsh -s /usr/bin/zsh vscode
RUN sed -i 's/plugins=(git)/plugins=(git aws sudo)/' /home/vscode/.zshrc /root/.zshrc
USER vscode
COPY .devcontainer/install.sh /home/vscode/devcontainer-install.sh
RUN /home/vscode/devcontainer-install.sh